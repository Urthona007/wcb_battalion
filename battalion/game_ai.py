""" Functions for AI """
from random import randrange
import queue
from hexl import get_hex_coords_from_direction #pylint: disable=E0401
from hexl import directions
import numpy as np

def evaluate_combat(active_phase):
    """ Evaluate and execute a combat phase. """
    return

def ai_circle(unit, game_dict):
    """ return CMD string for unit using strategy CIRCLE. """
    newx, newy = get_hex_coords_from_direction( \
        directions[game_dict["game_turn"]%6], unit.x, unit.y, game_dict)
    return f"{unit.name}: MV ({unit.x}, {unit.y}) -> ({newx}, {newy})"

def ai_evacuate(unit, game_dict):
    """ return CMD string for unit using strategy EVACUATE. """

    # Create a hexmap with the evacuation hex as its origin.
    hexmap = np.full((game_dict["map_width"], game_dict["map_height"]), 99)
    hexmap[game_dict["evacuation_hex"][0]][game_dict["evacuation_hex"][1]] = 0

    hexnode_queue = queue.Queue()
    hexnode_queue.put(game_dict["evacuation_hex"])
    while not hexnode_queue.empty():
        this_hex = hexnode_queue.get()
        for direct in directions:
            adjx, adjy = get_hex_coords_from_direction(direct, this_hex[0], this_hex[1], game_dict)
            if adjx is not None and adjy is not None and hexmap[adjx][adjy] == 99:
                hexmap[adjx][adjy] = hexmap[this_hex[0]][this_hex[1]]+1
                hexnode_queue.put((adjx, adjy))

    if hexmap[unit.x][unit.y] == 0:
        return f"{unit.name}: EVACUATE"

    # Choose one of the candidates randomly
    candidate_list = []
    for direct in directions:
        adjx, adjy = get_hex_coords_from_direction(direct, unit.x, unit.y, game_dict)
        if adjx is not None and adjy is not None and \
            hexmap[adjx][adjy] < hexmap[unit.x][unit.y]:
            candidate_list.append((adjx, adjy))
    assert len(candidate_list) > 0
    next_hex = candidate_list[randrange(len(candidate_list))]
    return f"{unit.name}: MV ({unit.x}, {unit.y}) -> ({next_hex[0]}, {next_hex[1]})"
