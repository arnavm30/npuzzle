import collections
import copy
from queue import PriorityQueue

# Check if 'N' is an int
# Arguments: string
# Returns: boolean
def valid_N(N, data):
    try:
        N = int(N)
        #if len(data) != N + 1:
            #return False
    except ValueError:
        return False
    return True

# Flattens ND iterable into 1D iterable
# Arguments: ND list
# Returns: 1D list
def flatten(nested_list):
    if isinstance(nested_list, collections.Iterable):
        return [x for next_level in nested_list for x in flatten(next_level)]
    else:
        return [nested_list]

# Opens file with initial gameboard and converts to internal representation
# Arguments: string
# Returns: 2D tuple
def LoadFromFile(filepath):
    with open(filepath, 'r') as f:
        data = f.readlines()
        print(data)
        N = data[0]
        if not valid_N(N, data):
            print('Error: invalid file')
            return None
        N = int(N)
        if len(data) != N + 1:
            print('Error: invalid file')
            return None
        tiles = []
        for row in range(1, N + 1):
            new_row = [int(num)  if num != '*' else 0 for num in data[row].strip().split('\t')]
            if len(new_row) != N:
                print('Error: invalid file')
                return None
            tiles.append(new_row)

        if sorted(flatten(tiles)) != list(range(N**2)):
            print('Error: invalid file')
            return None
        return tuple(tuple(row) for row in tiles)

# Finds location of hole on game board
# Arguments: 2D tuple
# Returns: tuple
def find_hole(state):
    hole_col = 0
    hole_row = 0
    N = len(state)

    for row in range(N):
        for col in range(N):
            if state[row][col] == 0:
                hole_row = row
                hole_col = col
    return (hole_row, hole_col)

# Swaps 2 tiles on game board and returns new board
# Arguments: 2D tuple, int, int, int, int
# Returns: 2D tuple
def swap_tiles(state, row1, col1, row2, col2):
    new_state = [list(row) for row in copy.deepcopy(state)]
    new_state[row1][col1] = new_state[row2][col2]
    new_state[row2][col2] = state[row1][col1]
    return tuple(tuple(row) for row in new_state)

# Finds neighbors of hole and the new state if hole and neighbor are switched
# Arguments: 2D tuple
# Returns: list of tuples containing an int and a 2D tuple
def ComputeNeighbors(state):
    hole_row, hole_col = find_hole(state)
    N = len(state)

    neighbors = []
    if hole_row < N - 1: # check that hole not on last row, where there would be no neighbor below
        tile_moved = state[hole_row + 1][hole_col]
        new_state = swap_tiles(state, hole_row, hole_col, hole_row + 1, hole_col)
        neighbors.append((tile_moved, new_state))
    if hole_row > 0: # check that hole not on first row, where there would be no neighbor above
        tile_moved = state[hole_row - 1][hole_col]
        new_state = swap_tiles(state, hole_row, hole_col, hole_row - 1, hole_col)
        neighbors.append((tile_moved, new_state))
    if hole_col < N - 1: # check that hole not on last col, where there would be no neighbor to the right
        tile_moved = state[hole_row][hole_col + 1]
        new_state = swap_tiles(state, hole_row, hole_col, hole_row, hole_col + 1)
        neighbors.append((tile_moved, new_state))
    if hole_col > 0: # check that hole not on first col, where there would be no neighbor to the left
        tile_moved = state[hole_row][hole_col - 1]
        new_state = swap_tiles(state, hole_row, hole_col, hole_row, hole_col - 1)
        neighbors.append((tile_moved, new_state))
    return neighbors

# Determines if game board is solvable using the counting inversions method
# Arguments: 2D tuple
# Returns: boolean
def solvable(state):
    flattened_state = flatten(state)
    flattened_state.remove(0)
    N = len(state)
    inversions = 0

    # counting all the numbers after a number that should be before it sequentially
    for i in range(len(flattened_state)):
        for j in range(len(flattened_state)):
            if i < j and flattened_state[i] > flattened_state[j]:
                inversions += 1

    if N % 2 == 1 and inversions % 2 == 0:
        return True
    elif N % 2 == 0:
        hole_row, hole_col = find_hole(state)
        hole_row_from_bottom = N - hole_row
        if hole_row_from_bottom % 2 == 0 and inversions % 2 == 1:
            return True
        elif hole_row_from_bottom % 2 == 1 and inversions % 2 == 0:
            return True
    return False

# Checks if current game board is the final, goal board
# Arguments: 2D tuple
# Returns: boolean
def IsGoal(state):
    return flatten(list(list(row) for row in state)) == list(range(1, len(state)**2)) + [0]

# Backtrack to find path from initial state to goal state
# Arguments: dict, tuple
# Return: list
def backtrack(parents, current_state):
    path = []
    while parents[current_state[1]]:
        path = [parents[current_state[1]][0]] + path
        current_state = parents[current_state[1]]
    return path

# Helper search function for BFS and DFS
# Arguments: 2D list, boolean with default to true
# Returns: list
def search(state, BFS=True):
    if not solvable(state):
        return None
    frontier = [(0, state)]
    discovered = set()
    parents = {state: None}
    while len(frontier) != 0:
        current_state = frontier.pop(0) if BFS else frontier.pop(-1)
        discovered.add(current_state[1])
        if IsGoal(current_state[1]):
           return backtrack(parents, current_state)
        for neighbor in ComputeNeighbors(current_state[1]):
            if neighbor[1] not in discovered:
                frontier.append(neighbor)
                discovered.add(neighbor[1])
                parents[neighbor[1]] = (neighbor[0], current_state[1])
    return None

# BFS
# Arguments: 2D tuple
# Returns: list
def BFS(state):
    return search(state)

# DFS
# Arguments: 2D tuple
# Returns: list
def DFS(state):
    return search(state, BFS=False)

# Generates goal state
# Arguments: 2D tuple
# Returns: 2D tuple
def generate_goal(state):
    N = len(state)
    goal = [list(range(N * row + 1, N * (row + 1) + 1)) for row in range(N)]
    goal[-1][-1] = 0
    return tuple(tuple(row) for row in goal)

# Bidirectional Search
# Arguments: 2D tuple
# Returns: list
def BidirectionalSearch(state):
    if not solvable(state):
        return None
    goal = generate_goal(state)
    frontier_front = [(0, state)]
    frontier_back = [(0, goal)]
    discovered_front = set()
    discovered_back = set()
    parents_front = {state: []}
    parents_back = {goal: []}

    while len(frontier_front) != 0 and len(frontier_back) != 0:
        current_state_front = frontier_front.pop(0)
        current_state_back = frontier_back.pop(0)
        discovered_front.add(current_state_front[1])
        discovered_back.add(current_state_back[1])
        
        for neighbor_front in ComputeNeighbors(current_state_front[1]):
            if neighbor_front[1] not in discovered_front:
                frontier_front.append(neighbor_front)
                discovered_front.add(neighbor_front[1])
                parents_front[neighbor_front[1]] = parents_front[current_state_front[1]] + [neighbor_front[0]]

        intersection = list(discovered_front.intersection(discovered_back))
        if len(intersection) > 0: 
            intersect = intersection[0]
            path_front = list(parents_front[intersect])
            path_back = list(reversed(parents_back[intersect]))
            return path_front + path_back     

        for neighbor_back in ComputeNeighbors(current_state_back[1]):
            if neighbor_back[1] not in discovered_back:
                frontier_back.append(neighbor_back)
                discovered_back.add(neighbor_back[1])
                parents_back[neighbor_back[1]] = parents_back[current_state_back[1]] + [neighbor_back[0]]
    return None

# Manhattan distance heuristic function
# Arguments: 2D tuple
# Returns: int
def h(state):
    N = len(state)
    sum_dist = 0
    for value_row in range(N):
        for value_col in range(N):
            value = state[value_row][value_col]
            if value != 0:
                goal_row = (value - 1) // N
                goal_col = (value - 1) % N
                sum_dist += abs(value_row - goal_row) + abs(value_col - goal_col)
    return sum_dist

def AStar_backtrack(parents, current_state):
    path = []
    while parents[current_state[2]]:
        path = [parents[current_state[3]]] + path
        current_state = parents[current_state[2]]
    return(path)

# AStar (brokoen)
# Arguments: 2D tuple
# Returns: list
def AStar(state):
    if not solvable(state):
        return None
    frontier = PriorityQueue()
    frontier.put((h(state), 0, 0, state)) # estimated cost, true cost, tile, state
    discovered = set()
    parents = {state: None}
    path = []
    while not frontier.empty():
        current_state = frontier.get()
        print(current_state[2])
        discovered.add(current_state[2])
        if IsGoal(current_state[2]):
            return AStar_backtrack(parents, current_state)
            '''
            while parents.get(current_state[2]) != None:
                path.insert(0, current_state[0])
                current_state = parents.get(current_state[2])
            return path
            '''
        for neighbor in ComputeNeighbors(current_state[2]):
            if neighbor[1] not in discovered:
                frontier.put((h(neighbor[1]), current_state[1] + 1, neighbor))
                discovered.add(neighbor[1])
                parents[(neighbor[0], neighbor[1])] = current_state
    return None

state = LoadFromFile('/Users/arnavmuthiayen/Workarea/workspace/ATCS_20-21/npuzzle/input.txt')
#print(ComputeNeighbors(state))
#print(BFS(state))
#print(DFS(state))
#print(BidirectionalSearch(state))
#print(AStar(state))