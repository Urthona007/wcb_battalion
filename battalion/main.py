""" Battalion Main """
import pygame
from hexl import get_hex_coords_from_direction #pylint: disable=E0401
import unit
from hexl import draw_hexs
from hexl import directions
from threading import Thread
from time import sleep
from random import randrange

def active_phases(game_dict):
    for phase in game_dict["game_phases"]:
        if not phase[1]:
            return True

def reset_phases(game_dict):
    for i in range(len(game_dict["game_phases"])):
        game_dict["game_phases"][i] = (game_dict["game_phases"][i][0], False)

def evaluate_combat(active_phase):
    return

def execute_phase(game_dict, active_phase):
    if "combat" in active_phase:
        evaluate_combat(active_phase)
    else:
        for player in game_dict["players"]:
            for battalion in player.battalion:
                if battalion.name in active_phase:
                    for unit in battalion.units:
                        newx, newy = get_hex_coords_from_direction(directions[game_dict["game_turn"]%6], unit.x, unit.y, game_dict)
                        unit.x = newx
                        unit.y = newy
                        game_dict["update_screen"] = True

def next_phase(game_dict):
    candidate_phases = []
    phase_list = game_dict["game_phases"]
    for phase in phase_list:
        if not phase[1]:
            candidate_phases.append(phase)
    active_phase = candidate_phases[randrange(len(candidate_phases))]
    print(f"Executing {active_phase[0]}")
    execute_phase(game_dict, active_phase[0])
    for i in range(len(phase_list)):
        if phase_list[i][0] == active_phase[0]:
            phase_list[i] = (active_phase[0], True)
    sleep(1)

def play_game_threaded_function(game_dict, max_turns):
    while game_dict["game_turn"] < max_turns and game_dict["game_running"]:
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
    def __init__(self, idx, name):
        self.idx = idx
        self.name = name
        self.units = []

class Player():
    def __init__(self, idx, name):
        self.idx = idx
        self.name = name
        self.battalion = []

def draw_map(screen, a_game_dict):
    """ Draw game map. """
    draw_hexs(screen, a_game_dict)

pygame.init()
game_dict = {'name': 'Battalion', 'display_width' : 640, 'display_height' : 480, \
    'bkg_color': (50, 50, 50), 'map_width': 11, 'map_height': 8, 'map_multiplier': 50, \
    'map_border' : 8, 'unit_width': 32, 'unit_x_offset': 18, 'unit_y_offset': 34, \
    "players" : (Player(0, "Red"), Player(1, "Blu")), "game_turn": 1, \
    "game_phases":[("Red Combat", False), ("Blu Combat", False)], "game_running": True}

game_dict["players"][0].battalion.append(Battalion(0, "Rommel"))
game_dict["players"][0].battalion[0].units.append(unit.Unit("infantry", 1, 4, 2, 0))
game_dict["players"][1].battalion.append(Battalion(0, "EZ Company"))
game_dict["players"][1].battalion[0].units.append(unit.Unit("infantry", 1, 7, 5, 1))
for player in game_dict["players"]:
    for battalion in player.battalion:
        game_dict["game_phases"].append((f"{battalion.name} Movement", False))

pygame.display.set_caption(game_dict['name']) # NOTE: this is not working.

game_dict["game_running"] = True
game_screen = pygame.display.set_mode((game_dict['display_width'], game_dict['display_height']))
game_dict["update_screen"] = True



first_time = True
gamemaster_thread = None
while game_dict["game_running"]:
    for event in pygame.event.get():
        # print(event)
        if event.type == pygame.QUIT:
            game_dict["game_running"] = False
    if game_dict["update_screen"]:
        game_screen.fill(game_dict['bkg_color'])
        draw_map(game_screen, game_dict)
        unit.draw_units(game_screen, game_dict)
        pygame.display.update()
        game_dict["update_screen"] = False
        if first_time:
            first_time = False
            if __name__ == "__main__":
                sleep(1)
                gamemaster_thread = Thread(target = play_game_threaded_function, args = (game_dict, 10))
                gamemaster_thread.start()
                #    thread.join()
                #    print("thread finished...exiting")
if gamemaster_thread:
    gamemaster_thread.join()
pygame.quit()
