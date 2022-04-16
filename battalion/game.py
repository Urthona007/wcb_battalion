""" game utility functions and class definitions """
from time import sleep
from ast import literal_eval
from random import randrange
from unit import get_unit_by_name
from game_ai import ai_evacuate, ai_circle
from hexl import directions, hex_next_to_enemies
from hexl import get_hex_coords_from_direction, hex_occupied #pylint: disable=E0401

def active_phases(game_dict):
    """ Are there any active phases? """
    for phase in game_dict["game_phases"]:
        if not phase[1]:
            return True
    return False

def reset_phases(game_dict):
    """ reset the state of the game phases each turn to False (ie not performed this turn.  """
    for i in range(len(game_dict["game_phases"])):
        game_dict["game_phases"][i] = (game_dict["game_phases"][i][0], False)

def process_command(unit, command, game_dict):
    """ Process a text-based unit command from a player."""
    print('\t' + command)
    two_strings = command.split(": ")
    if two_strings[1].find("EVACUATE") != -1:
        unit.status = "off_board"
    elif two_strings[1].find("PASS") != -1:
        pass
    elif two_strings[1].find("MV") != -1:
        move_strings = two_strings[1].split()
        assert "MV" == move_strings[0]
        start_hex = literal_eval(move_strings[1]+move_strings[2])
        assert "->" == move_strings[3]
        end_hex = literal_eval(move_strings[4]+move_strings[5])
        unit.x = end_hex[0]
        unit.y = end_hex[1]
    elif two_strings[1].find("ATTACK") != -1:
        attack_strings = two_strings[1].split(" ", 1)
        e_unit = get_unit_by_name(attack_strings[1], game_dict)
        print(f"{e_unit.name} destroyed!")
        e_unit.x = e_unit.y = -1
        e_unit.status = "destroyed"
    elif two_strings[1].find("RETREAT") != -1:
        # Choose one of the candidates randomly
        candidate_list = []
        for direct in directions:
            adjx, adjy = get_hex_coords_from_direction(direct, unit.x, unit.y, game_dict)
            if adjx is not None and adjy is not None and \
                not hex_occupied(adjx, adjy, game_dict) and \
                not hex_next_to_enemies(adjx, adjy, 1-unit.player, game_dict):
                    candidate_list.append((adjx, adjy))
        if len(candidate_list) == 0:
            # Nowhere to retreat.
            print(f"{unit.name} has nowhere to retreat and is destroyed!")
            unit.x = -1
            unit.y = -1
            unit.status = "destroyed"
        else:
            retreat_hex = candidate_list[randrange(len(candidate_list))]
            derived_command = f"{unit.name}: MV ({unit.x}, {unit.y}) -> " + \
                f"({retreat_hex[0]}, {retreat_hex[1]})"
            process_command(unit, derived_command, game_dict)


def evaluate_combat(player_num, game_dict):
    """ Evaluate and execute a combat phase. """
    aggressor = game_dict["players"][player_num]
    defender = game_dict["players"][player_num-1]
    for a_battalion in aggressor.battalion:
        for a_unit in a_battalion.units:
            if a_unit.status == "active":
                for d_battalion in defender.battalion:
                    for d_unit in d_battalion.units:
                        if d_unit.status == "active":
                            for direct in directions:
                                adjx, adjy = get_hex_coords_from_direction( direct, a_unit.x, a_unit.y, game_dict)
                                if adjx is not None and adjy is not None:
                                    if adjx == d_unit.x and adjy == d_unit.y:
                                        # Adjacent unit, this means combat
                                        if a_unit.strength > d_unit.strength:
                                            combat_str = f"{a_unit.name}: ATTACKS {d_unit.name}"
                                        else:
                                            combat_str = f"{a_unit.name}: RETREATS"
                                        process_command(a_unit, combat_str, game_dict)

def execute_phase(game_dict, active_phase):
    """ Basic game operation: Execute the input active phase.  """
    if "Combat" in active_phase:
        combat_words = active_phase.split()
        if "Red" in combat_words[0]:
            evaluate_combat(0, game_dict)
        else:
            evaluate_combat(1, game_dict)

    else:
        for player in game_dict["players"]:
            for battalion in player.battalion:
                if battalion.name in active_phase:
                    if battalion.strategy == "Evacuate":
                        for unit in battalion.units:
                            command = ai_evacuate(unit, game_dict)
                            process_command(unit, command, game_dict)
                    else:
                        for unit in battalion.units:
                            command = ai_circle(unit, game_dict)
                            process_command(unit, command, game_dict)
                    game_dict["update_screen"] = True

def next_phase(game_dict):
    """ Basic game operation: Select the next phase randomly and execute it.  """
    candidate_phases = []
    phase_list = game_dict["game_phases"]
    for phase in phase_list:
        if not phase[1]:
            candidate_phases.append(phase)
    active_phase = candidate_phases[randrange(len(candidate_phases))]
    print(f"Executing {active_phase[0]}")
    execute_phase(game_dict, active_phase[0])
    for i, phase in enumerate(phase_list):
        if phase[0] == active_phase[0]:
            phase_list[i] = (active_phase[0], True)
    sleep(1)

def play_game_threaded_function(game_dict, max_turns):
    """ This is the function that starts the game manager thread.  This thread is run in parallel
        to the main (display) thread. """
    while game_dict["game_running"]:
        turn = game_dict["game_turn"]
        print(f"Turn {turn}")
        while game_dict["game_running"] and active_phases(game_dict):
            next_phase(game_dict)
        reset_phases(game_dict)
        game_dict["game_turn"] += 1
    if game_dict["game_turn"] == max_turns:
        print(f"\nGAME OVER: MAX TURNS {max_turns} reached.")
    game_dict["game_running"] = False

class Battalion():
    """ Battalions consist of one or more units.  Battalions have unique movmement phases.  """
    def __init__(self, idx, name):
        self.idx = idx
        self.name = name
        self.units = []
        self.strategy = "uninitialized"

class Player():
    """ Players can be Human or AI """
    def __init__(self, idx, name):
        self.idx = idx
        self.name = name
        self.battalion = []