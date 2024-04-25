

# import os
# import pygame
# from pygame.locals import *
# from random import choice

import pygame
import random
import time
import itertools
import timeit
import numpy as np

np.set_printoptions(threshold=np.inf)

# Object options
FLOOR_OPT = 0
WALL_OPT = 1
BIN_OPT = 2
DOOR_OPT = 3
TABLE_OPT = 4

# Surrounding Values of array: check if they are free
LEFT_POS = 0
UP_POS = 1
RIGHT_POS = 2
DOWN_POS = 3

# Object colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
DARK_RED = (139, 0, 0)

# Maze grid settings (editable) 
NUM_PIXELS_EACH_CELL = 10 # Probably should be even
NUM_BENCH_COLS = 5
NUM_BENCH_ROWS = 5 # Do not do less than 2
NUM_CELLS_PER_X_BIN = 16 # Number of horizontal cells for each bin
NUM_CELLS_PER_Y_BIN = 1 # Does not include bins on either side of bin
NUM_CELLS_BETWEEN_BINS = 2
TABLE_LOC_X_BEG = 3
TABLE_LOC_X_END = 6
NUM_DEST_LOCATIONS = 8

# Dirs
NORTH = 1
EAST = 2
SOUTH = 3
WEST = 4
NONE_DIR = 5
GOAL = 6

# Make the window fit everything (non-editable)
BINS_ON_BENCH_SIDES = 2
NUM_PAD_CELLS = 2
NUM_CELL_ROWS = (NUM_BENCH_ROWS * NUM_CELLS_PER_Y_BIN) + (NUM_BENCH_ROWS * BINS_ON_BENCH_SIDES) + ((NUM_BENCH_ROWS + 1) * NUM_CELLS_BETWEEN_BINS)
NUM_CELL_COLS = (NUM_BENCH_COLS * NUM_CELLS_PER_X_BIN) + ((NUM_BENCH_COLS + 1) * NUM_CELLS_BETWEEN_BINS)
WINDOW_SHAPE = ((NUM_PIXELS_EACH_CELL * NUM_PAD_CELLS) + (NUM_PIXELS_EACH_CELL * NUM_CELL_COLS), 
                (NUM_PIXELS_EACH_CELL * NUM_PAD_CELLS) + (NUM_PIXELS_EACH_CELL * NUM_CELL_ROWS)) 
LINE_WIDTH = 0
CIRCLE_RADIUS = NUM_PIXELS_EACH_CELL // 2


# byu_store_warehouse_map = [
#     [1, 1, 1, 1, 1, 1, 1, 1],
#     [1, 2, 2, 2, 2, 2, 2, 2],
#     [1, 2, 0, 0, 0, 0, 0, 0],
#     [1, 2, 0, 0, 0, 0, 0, 0],
#     [1, 2, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
#     [1, 2, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#     [1, 2, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
#     [1, 2, 0, 0, 0, 0, 0, 0]
# ]

# Define a class of cells to hold coordinates
class Cell:
    def __init__(self, x:int, y:int, coordx:int, coordy:int, dim_x:int, dim_y:int, type:int):
        self.x = x
        self.y = y
        self.coordx = coordx
        self.coordy = coordy
        self.dimx = dim_x
        self.dimy = dim_y
        self.type = type
        self.is_used = False
        self.floor_color = (0, 0, 0) # Only used if type is floor
        self.bin_id = -1 # Only used if type is bin

# Define the warehouse array: Wall, then (floor, bin, wall, bin), then repeat, end with wall
warehouse_map = []
warehouse_cells = []
warehouse_route = []


def auto_warehouse_grid_gen():

    pygame.display.update()

    ################################################
    # Warehouse array init
    ################################################

    # First create a wall set
    warehouse_map.append([WALL_OPT for i in range(NUM_PAD_CELLS + NUM_CELL_COLS)])

    # Loop through each bench set
    for i in range(NUM_BENCH_ROWS):

        # Floor first
        for j in range(NUM_CELLS_BETWEEN_BINS):
            new_list = []
            new_list.append(WALL_OPT)
            for k in range(NUM_CELL_COLS):
                new_list.append(FLOOR_OPT)
            new_list.append(WALL_OPT)
            # print("Floor: ", new_list)
            warehouse_map.append(new_list)

        # Bins next
        new_list = []
        new_list.append(WALL_OPT)
        for j in range(NUM_BENCH_COLS):
            for k in range(NUM_PAD_CELLS):
                if (i == 0 and j == 0):
                    new_list.append(DOOR_OPT)
                else:
                    new_list.append(FLOOR_OPT)
            for k in range(NUM_CELLS_PER_X_BIN):
                if (i == 0 and j == 0):
                    if (k >= TABLE_LOC_X_BEG and k <= TABLE_LOC_X_END):
                        new_list.append(TABLE_OPT)
                    else:
                        new_list.append(FLOOR_OPT)
                else:
                    new_list.append(BIN_OPT)
        for k in range(NUM_PAD_CELLS):
            new_list.append(FLOOR_OPT)
        new_list.append(WALL_OPT)
        # print("Bin:   ", new_list)
        warehouse_map.append(new_list)

        # Walls next
        for m in range(NUM_CELLS_PER_Y_BIN):
            new_list = []
            new_list.append(WALL_OPT)
            for j in range(NUM_BENCH_COLS):
                for k in range(NUM_PAD_CELLS):
                    if (i == 0 and j == 0):
                        new_list.append(DOOR_OPT)
                    else:
                        new_list.append(FLOOR_OPT)
                for k in range(NUM_CELLS_PER_X_BIN):
                    if (i == 0 and j == 0):
                        if (k >= TABLE_LOC_X_BEG and k <= TABLE_LOC_X_END):
                            new_list.append(TABLE_OPT)
                        else:
                            new_list.append(FLOOR_OPT)
                    else:
                        new_list.append(WALL_OPT)
            for k in range(NUM_PAD_CELLS):
                new_list.append(FLOOR_OPT)
            new_list.append(WALL_OPT)
            # print("Walls: ", new_list)
            warehouse_map.append(new_list)

        # Bins last
        new_list = []
        new_list.append(WALL_OPT)
        for j in range(NUM_BENCH_COLS):
            for k in range(NUM_PAD_CELLS):
                if (i == 0 and j == 0):
                    new_list.append(DOOR_OPT)
                else:
                    new_list.append(FLOOR_OPT)
            for k in range(NUM_CELLS_PER_X_BIN):
                if (i == 0 and j == 0):
                    if (k >= TABLE_LOC_X_BEG and k <= TABLE_LOC_X_END):
                        new_list.append(TABLE_OPT)
                    else:
                        new_list.append(FLOOR_OPT)
                else:
                    new_list.append(BIN_OPT)
        for k in range(NUM_PAD_CELLS):
            new_list.append(FLOOR_OPT)
        new_list.append(WALL_OPT)
        # print("Bin:   ", new_list)
        warehouse_map.append(new_list)

    # One more set of floors
    for j in range(NUM_CELLS_BETWEEN_BINS):
        new_list = []
        new_list.append(WALL_OPT)
        for k in range(NUM_CELL_COLS):
            new_list.append(FLOOR_OPT)
        new_list.append(WALL_OPT)
        # print("Floor: ", new_list)
        warehouse_map.append(new_list)

    # End with a wall set
    warehouse_map.append([WALL_OPT for i in range(NUM_PAD_CELLS + NUM_CELL_COLS)])

    ################################################
    # Get dimensions of map
    ################################################

    for i in range(len(warehouse_map)):
        new_list = []
        for j in range(len(warehouse_map[i])):
            new_list.append(Cell(j * NUM_PIXELS_EACH_CELL, i * NUM_PIXELS_EACH_CELL, j, i, NUM_PIXELS_EACH_CELL, NUM_PIXELS_EACH_CELL, warehouse_map[i][j]))
        warehouse_cells.append(new_list)
        warehouse_route.append(np.zeros_like(new_list).tolist())


def get_all_locations_and_begin():

    # Find all cells for bins, and a cell that starts at the door
    cell_begin = None
    cell_list = []
    for cell_row in warehouse_cells:
        for cell in cell_row:
            if cell.type == BIN_OPT:
                cell_list.append((cell.coordx, cell.coordy))
            elif cell.type == DOOR_OPT:
                cell_begin = (cell.coordx, cell.coordy)

    # Return these findings
    return cell_begin, cell_list



def draw_warehouse(window):

    for list_cells in warehouse_cells:
        for cell in list_cells:

            if cell.type == FLOOR_OPT:
                # print(cell.is_used, ", ", cell.floor_color)
                if cell.is_used:
                    pygame.draw.rect(window, cell.floor_color, (cell.x, cell.y, cell.dimx, cell.dimy), LINE_WIDTH)
                else:
                    pygame.draw.rect(window, WHITE, (cell.x, cell.y, cell.dimx, cell.dimy), LINE_WIDTH)
            elif cell.type == WALL_OPT:
                pygame.draw.rect(window, BLACK, (cell.x, cell.y, cell.dimx, cell.dimy), LINE_WIDTH)
            elif cell.type == BIN_OPT:
                coord1 = (cell.x + (cell.dimx // 2))
                coord2 = (cell.y + (cell.dimy // 2))
                # print("Coord 1: ", coord1, ", Coord 2: ", coord2, "Rect: X: ", cell.x, ", Y: ", cell.y)
                if cell.is_used:
                    pygame.draw.rect(window, cell.floor_color, (cell.x, cell.y, cell.dimx, cell.dimy), LINE_WIDTH)
                else:
                    pygame.draw.rect(window, WHITE, (cell.x, cell.y, cell.dimx, cell.dimy), LINE_WIDTH)
                pygame.draw.circle(window, DARK_RED, (coord1, coord2), CIRCLE_RADIUS, LINE_WIDTH)
            elif cell.type == DOOR_OPT:
                pygame.draw.rect(window, RED, (cell.x, cell.y, cell.dimx, cell.dimy), LINE_WIDTH)
            elif cell.type == TABLE_OPT:
                pygame.draw.rect(window, YELLOW, (cell.x, cell.y, cell.dimx, cell.dimy), LINE_WIDTH)

    pygame.display.update()
    pygame.time.wait(50)


# def lm_check_move_to_neighbours(cell_array, scratchpad, cnt_var, point_dest):
#     index1_list = np.where(scratchpad == (cnt_var - 1))[0]
#     # print(index1_list)

#     for index1 in index1_list:
#         index2_list = np.where(scratchpad[index1] == (cnt_var - 1))[0]
#         # print(index1)
#         # print(index2_list)

#         for index2 in index2_list:
#             # print(index2)
            

#             if (cell_array[index1 + 1][index2].type == 0 or (point_dest[0] == index2 and point_dest[1] == (index1 + 1))) and scratchpad[index1 + 1][index2] == 0:
#                 scratchpad[index1 + 1][index2] = cnt_var
#             if (cell_array[index1 - 1][index2].type == 0 or (point_dest[0] == index2 and point_dest[1] == (index1 - 1))) and scratchpad[index1 - 1][index2] == 0:
#                 scratchpad[index1 - 1][index2] = cnt_var
#             if (cell_array[index1][index2 + 1].type == 0 or (point_dest[0] == (index2 + 1) and point_dest[1] == (index1))) and scratchpad[index1][index2 + 1] == 0:
#                 scratchpad[index1][index2 + 1] = cnt_var
#             if (cell_array[index1][index2 - 1].type == 0 or (point_dest[0] == (index2 - 1) and point_dest[1] == (index1))) and scratchpad[index1][index2 - 1] == 0:
#                 scratchpad[index1][index2 - 1] = cnt_var



class RouteRouter:

    def __init__(self):
        pass

    def lee_moore(self, route_array, scratchpad, point_src : tuple, point_dest : tuple, wire : bool):
        
        cnt_val = 1
        abs_cost = 0
        # if route_array[point_src[1]][point_src[0]] != 0:
        #     print("Errors have occured")
        #     print(route_array)
        #     exit()
        
        scratchpad[point_src[1]][point_src[0]] = cnt_val

        while scratchpad[point_dest[1]][point_dest[0]] == 0:
            cnt_val += 1

            # Find the next neighbour to fill
            # lm_check_move_to_neighbours(warehouse_cells, scratchpad, cnt_val, point_dest)
            index1_list = np.where(scratchpad == (cnt_val - 1))[0]
            # print(index1_list)

            for index1 in index1_list:
                index2_list = np.where(scratchpad[index1] == (cnt_val - 1))[0]
                # print(index1)
                # print(index2_list)

                for index2 in index2_list:
                    # print(index2)
                    

                    if (warehouse_cells[index1 + 1][index2].type == 0 or (point_dest[0] == index2 and point_dest[1] == (index1 + 1))) and scratchpad[index1 + 1][index2] == 0:
                        scratchpad[index1 + 1][index2] = cnt_val
                    if (warehouse_cells[index1 - 1][index2].type == 0 or (point_dest[0] == index2 and point_dest[1] == (index1 - 1))) and scratchpad[index1 - 1][index2] == 0:
                        scratchpad[index1 - 1][index2] = cnt_val
                    if (warehouse_cells[index1][index2 + 1].type == 0 or (point_dest[0] == (index2 + 1) and point_dest[1] == (index1))) and scratchpad[index1][index2 + 1] == 0:
                        scratchpad[index1][index2 + 1] = cnt_val
                    if (warehouse_cells[index1][index2 - 1].type == 0 or (point_dest[0] == (index2 - 1) and point_dest[1] == (index1))) and scratchpad[index1][index2 - 1] == 0:
                        scratchpad[index1][index2 - 1] = cnt_val

        abs_cost = scratchpad[point_dest[1]][point_dest[0]]

        if not wire:
            
            return abs_cost
        
        else:

            # Here we wire it up (put values in warehouse_cells array)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            cur_point = list(point_dest)

            warehouse_cells[cur_point[1]][cur_point[0]].is_used = True
            warehouse_cells[cur_point[1]][cur_point[0]].floor_color = color

            while (cur_point[0] != point_src[0]) or (cur_point[1] != point_src[1]):
                # print("Cur point: ", cur_point, ", Point src: ", point_src)

                # Find next neighbour
                val_to_find = scratchpad[cur_point[1]][cur_point[0]] - 1
                if (scratchpad[cur_point[1] + 1][cur_point[0]] == val_to_find):
                    cur_point[1] += 1
                elif (scratchpad[cur_point[1] - 1][cur_point[0]] == val_to_find):
                    cur_point[1] -= 1
                elif (scratchpad[cur_point[1]][cur_point[0] + 1] == val_to_find):
                    cur_point[0] += 1
                elif (scratchpad[cur_point[1]][cur_point[0] - 1] == val_to_find):
                    cur_point[0] -= 1

                warehouse_cells[cur_point[1]][cur_point[0]].is_used = True
                warehouse_cells[cur_point[1]][cur_point[0]].floor_color = color

            return abs_cost



            
            # for war in scratchpad:
            #     print("[", end = "")
            #     for w in war:
            #         print(w, ", ", end="")
            #     print("]")

            # exit()

        # First find the route and the cost in lee moore fashion


    def a_star(self, route_array, scratchpad, point_src : tuple, point_dest : tuple, wire : bool):

        print("Source: col: ", point_src[0], ", row: ", point_src[1])
        print("Destin: col: ", point_dest[0], ", row: ", point_dest[1])
        
        cost_val = abs(point_dest[0] - point_src[0]) + abs(point_dest[1] - point_src[1])
        abs_cost = 0
        scratchpad_dir = np.zeros_like(scratchpad)

        # Find the direction we are going.
        low_col_lim = 0
        low_row_lim = 0
        high_col_lim = 0
        high_row_lim = 0
        if (point_src[0] >= point_dest[0]):
            low_col_lim = point_dest[0]
            high_col_lim = point_src[0]
        else:
            high_col_lim = point_dest[0]
            low_col_lim = point_src[0]

        if (point_src[1] >= point_dest[1]):
            low_row_lim = point_dest[1]
            high_row_lim = point_src[1]
        else:
            high_row_lim = point_dest[1]
            low_row_lim = point_src[1]


        
        scratchpad[point_src[1]][point_src[0]] = cost_val
        # scratchpad[5][3] = cost_val

        while scratchpad[point_dest[1]][point_dest[0]] == 0:

            # Find when no moves have been taken
            mv_cnt = 0

            # Find the next neighbour to fill
            # lm_check_move_to_neighbours(warehouse_cells, scratchpad, cnt_val, point_dest)
            # First find the rows where scratchpad is not empty
            index1_list = np.where(scratchpad != 0)[0]
            # print(index1_list)

            for index1 in index1_list:
                # Find the columns where scratchpad is not empty
                index2_list = np.where(scratchpad[index1] != 0)[0]
                # print(index1)
                # print(index2_list)
                

                for index2 in index2_list:
                    # print(index2)
                    

                    if (warehouse_cells[index1 + 1][index2].type == 0 or (point_dest[0] == index2 and point_dest[1] == (index1 + 1))) and (scratchpad[index1 + 1][index2] == 0 and (index1 + 1) <= high_row_lim):
                        scratchpad[index1 + 1][index2] = cost_val
                        scratchpad_dir[index1 + 1][index2] = NORTH
                        mv_cnt += 1
                    if (warehouse_cells[index1 - 1][index2].type == 0 or (point_dest[0] == index2 and point_dest[1] == (index1 - 1))) and (scratchpad[index1 - 1][index2] == 0 and (index1 - 1) >= low_row_lim):
                        scratchpad[index1 - 1][index2] = cost_val
                        scratchpad_dir[index1 - 1][index2] = SOUTH
                        mv_cnt += 1
                    if (warehouse_cells[index1][index2 + 1].type == 0 or (point_dest[0] == (index2 + 1) and point_dest[1] == (index1))) and (scratchpad[index1][index2 + 1] == 0 and (index2 + 1) <= high_col_lim):
                        scratchpad[index1][index2 + 1] = cost_val
                        scratchpad_dir[index1][index2 + 1] = WEST
                        mv_cnt += 1
                    if (warehouse_cells[index1][index2 - 1].type == 0 or (point_dest[0] == (index2 - 1) and point_dest[1] == (index1))) and (scratchpad[index1][index2 - 1] == 0 and (index2 - 1) >= low_col_lim):
                        scratchpad[index1][index2 - 1] = cost_val
                        scratchpad_dir[index1][index2 - 1] = EAST
                        mv_cnt += 1

            # If no moves have been taken, increase the cost and the boundries
            if mv_cnt == 0:
                if (low_col_lim > 0):
                    low_col_lim -= 1
                if (high_col_lim < (scratchpad.shape[1] - 1)):
                    high_col_lim += 1
                if (low_row_lim > 0):
                    low_row_lim -= 1
                if (high_row_lim < (scratchpad.shape[0] - 1)):
                    high_row_lim += 1

                cost_val += 2

        abs_cost = scratchpad[point_dest[1]][point_dest[0]]

        if not wire:
            
            return abs_cost
        
        else:

            # Here we wire it up (put values in warehouse_cells array)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            cur_point = list(point_dest)

            warehouse_cells[cur_point[1]][cur_point[0]].is_used = True
            warehouse_cells[cur_point[1]][cur_point[0]].floor_color = color

            while (cur_point[0] != point_src[0]) or (cur_point[1] != point_src[1]):
                # print("Cur point: ", cur_point, ", Point src: ", point_src)

                # Find next neighbour
                if (scratchpad_dir[cur_point[1]][cur_point[0]] == EAST):
                    cur_point[0] += 1
                elif (scratchpad_dir[cur_point[1]][cur_point[0]] == WEST):
                    cur_point[0] -= 1
                elif (scratchpad_dir[cur_point[1]][cur_point[0]] == SOUTH):
                    cur_point[1] += 1
                elif (scratchpad_dir[cur_point[1]][cur_point[0]] == NORTH):
                    cur_point[1] -= 1
                else:
                    print("WARNING: No valid direction taken!!!!!! Current point: row: ", cur_point[1], ", col: ", cur_point[0])
                    exit()

                warehouse_cells[cur_point[1]][cur_point[0]].is_used = True
                warehouse_cells[cur_point[1]][cur_point[0]].floor_color = color

            print("Found current point!! HURRAH!!")

            return abs_cost



            
            # for war in scratchpad:
            #     print("[", end = "")
            #     for w in war:
            #         print(w, ", ", end="")
            #     print("]")

            # exit()

        # First find the route and the cost in lee moore fashion

    pass


class Router:

    def __init__(self):
        self.route_router = RouteRouter()

    def brute_force_method(self, warehouse_route, beg_loc, rand_locs_list):

        # Record the total cost
        self.total_cost = 0
        
        # Prepare scratchpad
        scratchpad = np.zeros_like(warehouse_route)

        # First find all possible routes
        unique_combinations = []
        permut = itertools.permutations(rand_locs_list, len(rand_locs_list))

        # Make unique combinations a list of lists of tuples: each list is 
        # a unique list of all elements of rand_locs_list
        for p in permut:
            new_list = list(p)
            # Insert beginning location at beg and end of list
            new_list.insert(0, beg_loc)
            new_list.append(beg_loc)
            unique_combinations.append(list(new_list))
            # print("new list: ", new_list)


        # Now find the cost of every combination, even the beginning
        rand_locs_list.append(beg_loc)        
        total_route_pairs = []
        # Go through every pair of locations
        for i in range(len(rand_locs_list)):
            for j in range(len(rand_locs_list)):

                # Only get unique pairs (ex if number routes desired is 3, then (1, 2), (1, 3), (2, 3))
                if i < j:

                    # Order is this: location 1, location 2, cost # route_maker.lee_moore(warehouse_route, scratchpad, (3, 8), (3, 20), True)
                    total_route_pairs.append((rand_locs_list[i], rand_locs_list[j], self.route_router.a_star(warehouse_route, scratchpad, rand_locs_list[i], rand_locs_list[j], wire=False)))
                    
                    # Clear scratchpad
                    scratchpad = np.zeros_like(warehouse_route)

        # Calculate the costs for each unique combination
        # for unique_comb in unique_combinations
        list_of_costs = []
        for unique_comb in unique_combinations:
            cost = 0
            # print("Unique combo: ", unique_comb)
            for i in range(len(unique_comb) - 1):
                # print("Index: ", i, ", Comb: ", unique_comb[i], ", ", unique_comb[i + 1])
                # print("Total route pairs: ", total_route_pairs)
                element = next(filter(lambda x: ((x[0] == unique_comb[i] and x[1] == unique_comb[i + 1]) or (x[1] == unique_comb[i] and x[0] == unique_comb[i + 1])), total_route_pairs), None)
                assert element != None
                cost += element[2]
            list_of_costs.append(cost)
        unique_comb_to_use = unique_combinations[list_of_costs.index(min(list_of_costs))]

        # Finally, route the path
        for i in range(len(unique_comb_to_use) - 1):
            self.total_cost += self.route_router.a_star(warehouse_route, scratchpad, unique_comb_to_use[i], unique_comb_to_use[i + 1], wire=True)
            scratchpad = np.zeros_like(warehouse_route)

        # print(total_routes)
        pass

    def branch_and_bound(self, warehouse_route, beg_loc, rand_locs_list):
        
        # Record the total cost
        self.total_cost = 0
        
        # Prepare scratchpad
        scratchpad = np.zeros_like(warehouse_route)

        # First find all possible routes
        unique_combinations = []
        permut = itertools.permutations(rand_locs_list, len(rand_locs_list))

        # Make unique combinations a list of lists of tuples: each list is 
        # a unique list of all elements of rand_locs_list
        for p in permut:
            new_list = list(p)
            # Insert beginning location at beg and end of list
            new_list.insert(0, beg_loc)
            new_list.append(beg_loc)
            unique_combinations.append(list(new_list))
            # print("new list: ", new_list)


        # Now find the cost of every combination, even the beginning
        rand_locs_list.append(beg_loc)        
        total_route_pairs = []
        # Go through every pair of locations
        for i in range(len(rand_locs_list)):
            for j in range(len(rand_locs_list)):

                # Only get unique pairs (ex if number routes desired is 3, then (1, 2), (1, 3), (2, 3))
                if i < j:

                    # Order is this: location 1, location 2, cost # route_maker.lee_moore(warehouse_route, scratchpad, (3, 8), (3, 20), True)
                    total_route_pairs.append((rand_locs_list[i], rand_locs_list[j], self.route_router.lee_moore(warehouse_route, scratchpad, rand_locs_list[i], rand_locs_list[j], wire=False)))
                    
                    # Clear scratchpad
                    scratchpad = np.zeros_like(warehouse_route)

        # Calculate the costs for each unique combination
        # for unique_comb in unique_combinations
        list_of_costs = []
        for unique_comb in unique_combinations:
            cost = 0
            # print("Unique combo: ", unique_comb)
            for i in range(len(unique_comb) - 1):
                # print("Index: ", i, ", Comb: ", unique_comb[i], ", ", unique_comb[i + 1])
                # print("Total route pairs: ", total_route_pairs)
                element = next(filter(lambda x: ((x[0] == unique_comb[i] and x[1] == unique_comb[i + 1]) or (x[1] == unique_comb[i] and x[0] == unique_comb[i + 1])), total_route_pairs), None)
                assert element != None
                cost += element[2]
            list_of_costs.append(cost)
        unique_comb_to_use = unique_combinations[list_of_costs.index(min(list_of_costs))]

        # Finally, route the path
        for i in range(len(unique_comb_to_use) - 1):
            self.total_cost += self.route_router.lee_moore(warehouse_route, scratchpad, unique_comb_to_use[i], unique_comb_to_use[i + 1], wire=True)
            scratchpad = np.zeros_like(warehouse_route)

        # print(total_routes)
        pass

    def min_span_tree(self, warehouse_route, beg_loc, rand_locs_list):
        self.total_cost = 0
        
        # Prepare scratchpad and find shortest route
        scratchpad = np.zeros_like(warehouse_route)
        route_path = [beg_loc]
        route_index = 0

        # Find the lowest cost from the beginning to a node
        lowest_cost = []
        for i in range(len(rand_locs_list)):
            lowest_cost.append(self.route_router.lee_moore(warehouse_route, scratchpad, beg_loc, rand_locs_list[i], wire=False))
            scratchpad = np.zeros_like(warehouse_route)

        print("Stage 1")
        
        # Find the place with the lowest cost and route to it
        self.total_cost += min(lowest_cost)
        delete_index = lowest_cost.index(min(lowest_cost))
        route_path.append(rand_locs_list[delete_index])
        rand_locs_list.pop(delete_index)

        # Go through each point, find the closest node, add it
        while len(rand_locs_list) > 0:
            
            # Find the lowest costs
            lowest_cost = []
            for i in range(len(rand_locs_list)):
                lowest_cost.append(self.route_router.lee_moore(warehouse_route, scratchpad, route_path[route_index], rand_locs_list[i], wire=False))
                scratchpad = np.zeros_like(warehouse_route)

            self.total_cost += min(lowest_cost)
            delete_index = lowest_cost.index(min(lowest_cost))
            route_path.append(rand_locs_list[delete_index])
            rand_locs_list.pop(delete_index)
            route_index += 1

            print("Stage {}".format(route_index + 1))

        # Lastly, append the home node
        self.total_cost += self.route_router.lee_moore(warehouse_route, scratchpad, route_path[route_index], beg_loc, wire=False)
        scratchpad = np.zeros_like(warehouse_route)
        route_path.append(beg_loc)

        print("Finally routing")

        # Finally, route the path
        for i in range(len(route_path) - 1):
            self.route_router.lee_moore(warehouse_route, scratchpad, route_path[i], route_path[i + 1], wire=True)
            scratchpad = np.zeros_like(warehouse_route)
            
        pass

    pass
            

def main():

    # Random seed
    random.seed(time.time())

    # Init pygame and generate warehouse
    pygame.init()
    window = pygame.display.set_mode(WINDOW_SHAPE)
    auto_warehouse_grid_gen()

    # Get the list of locations for all bins and starting point
    beg_loc, locations_list = get_all_locations_and_begin()

    # Make sure number of locations desired does not exceed number of locations possible
    assert len(locations_list) >= NUM_DEST_LOCATIONS

    # Get random list of elements from locations list
    rand_locs_list = random.sample(locations_list, NUM_DEST_LOCATIONS)

    # # Draw the warehouse, clear scratchpad
    # draw_warehouse(window)
    # input("Press Enter to continue...")

    # route_maker = RouteRouter()
    # route_maker.lee_moore(warehouse_route, scratchpad, (3, 8), (3, 20), True)
    router = Router()
    t_0 = timeit.default_timer()
    router.brute_force_method(warehouse_route, beg_loc, rand_locs_list)
    t_1 = timeit.default_timer()
    print("Cost: ", router.total_cost, ", Exec time: ", t_1 - t_0, " sec")

    draw_warehouse(window)

    # for war in scratchpad:
    #     print("[", end = "")
    #     for w in war:
    #         print(w, ", ", end="")
    #     print("]")
    # for war in warehouse_route:
    #     print("[", end = "")
    #     for w in war:
    #         print(w, ", ", end="")
    #     print("]")
    # for war in warehouse_cells:
    #     print("[", end = "")
    #     for w in war:
    #         print(w.is_used, ", ", end="")
    #     print("]")

    input("Press Enter to continue...")
    # time.sleep(2)
    

    







if __name__ == '__main__':
    main()
