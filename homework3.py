from collections import deque
from queue import PriorityQueue
from heapq import heapify

from math import sqrt

ACTION_MAP = {
    1: (1, 0, 0),
    2: (-1, 0, 0),
    3: (0, 1, 0),
    4: (0, -1, 0),
    5: (0, 0, 1),
    6: (0, 0, -1),
    7: (1, 1, 0),
    8: (1, -1, 0),
    9: (-1, 1, 0),
    10: (-1, -1, 0),
    11: (1, 0, 1),
    12: (1, 0, -1),
    13: (-1, 0, 1),
    14: (-1, 0, -1),
    15: (0, 1, 1),
    16: (0, 1, -1),
    17: (0, -1, 1),
    18: (0, -1, -1),
}


class Node(object):
    """
    Represents a point on the grid
    """

    def __init__(self, coords) -> None:
        self.coords = coords
        self.children = []

    def __str__(self) -> str:
        """
        Returns the string representation of a node "x y z"
        """
        return " ".join([str(x) for x in self.coords])

    def __repr__(self) -> str:
        """
        Returns the string representation of a node "x y z" (for debugging)
        """
        return " ".join([str(x) for x in self.coords])

    def __gt__(self, other):
        """
        Break ties arbitrarily
        """
        return True


class Grid(object):
    """
    Represents a problem grid
    """

    def __init__(self, size, num_loc, points, start, finish) -> None:
        self.size = size
        self.num_loc = num_loc

        self.nodes = {}
        self.sld = {}

        # Setup nodes
        for coords in points.keys():
            if self.validate_coords(coords):
                self.nodes[coords] = Node(coords)

        # Add paths to nodes
        for coords, paths in points.items():
            for path, cost in paths:
                new_coords = (
                    coords[0] + path[0],
                    coords[1] + path[1],
                    coords[2] + path[2],
                )
                if self.validate_coords(new_coords) and new_coords in self.nodes.keys():
                    self.nodes[coords].children.append((self.nodes[new_coords], cost))

        # If the start of finish locations are missing, the search will fail
        self.start = self.nodes[start] if start in self.nodes.keys() else None
        self.finish = self.nodes[finish] if finish in self.nodes.keys() else None

    def validate_coords(self, coords):
        """
        Returns True if coords is a valid position in the grid instance
        """
        return not (
            (coords[0] > self.size[0])
            or (coords[1] > self.size[1])
            or (coords[2] > self.size[2])
        )

    def compute_heuristic(self):
        """
        Computes straight line distances from all nodes to the finish node
        """

        self.sld = {
            coords: round(
                sqrt(
                    pow((10 * node.coords[0] - 10 * self.finish.coords[0]), 2)
                    + pow((10 * node.coords[1] - 10 * self.finish.coords[1]), 2)
                    + pow((10 * node.coords[2] - 10 * self.finish.coords[2]), 2)
                )
            )
            if node != self.finish
            else 0
            for coords, node in self.nodes.items()
        }


class SearchPriorityQueue(PriorityQueue):
    def __init__(self) -> None:
        super().__init__(maxsize=0)

    def update_priority(self, item, priority, actual=False):
        index = 2 if actual else 1
        for num in range(len(self.queue)):
            if self.queue[num][index] == item:
                if actual:
                    if priority < self.queue[num][0] or (
                        priority == self.queue[num][0] and actual < self.queue[num][1]
                    ):
                        self.queue[num] = (priority, actual, item)
                        heapify(self.queue)
                        return True
                else:
                    if priority < self.queue[num][0]:
                        self.queue[num] = (priority, item)
                        heapify(self.queue)
                        return True
                    else:
                        return False

        return False


def read_input_file():

    with open("input.txt", "r") as f:
        file = f.read().splitlines()

    search_method = file[0]
    grid_size = [int(x) for x in file[1].split(" ")]
    grid_entrance = tuple(int(x) for x in file[2].split(" "))
    grid_exit = tuple(int(x) for x in file[3].split(" "))
    grid_num_locations = file[4]

    grid_positions = {}
    for line in file[5:]:
        # (x,y,z) => [(move, diagonal),...]
        grid_positions[tuple(int(x) for x in line.split(" ")[:3])] = [
            (ACTION_MAP[int(x)], 14 if int(x) > 6 else 10) for x in line.split(" ")[3:]
        ]

    return search_method, Grid(
        size=grid_size,
        num_loc=grid_num_locations,
        points=grid_positions,
        start=grid_entrance,
        finish=grid_exit,
    )


def write_output_file(solution):
    if isinstance(solution, tuple):
        output = []
        output.append(str(solution[0]))
        output.append(str(solution[1]))

        for node in solution[2]:
            output.append(f"{node[0]} {node[1]}")
        output = "\n".join(output)
    else:
        output = "FAIL"

    with open("output.txt", "w") as f:
        f.write(output)


def breadth_first_search(grid: Grid):
    start_node = grid.start
    finish_node = grid.finish

    explored = set()
    revealed = set()
    parent = {}

    frontier = deque([start_node])

    while len(frontier):
        curr_node = frontier.popleft()
        explored.add(curr_node)

        for child_node, _ in curr_node.children:
            if child_node not in explored and child_node not in revealed:
                parent[child_node] = curr_node
                revealed.add(child_node)

                if child_node == finish_node:
                    solution_path = deque()

                    while parent.get(child_node):
                        solution_path.appendleft((child_node, 1))
                        child_node = parent.get(child_node)
                    solution_path.appendleft((child_node, 0))

                    return len(solution_path) - 1, len(solution_path), solution_path

                frontier.append(child_node)
    return False


def uniform_cost_search(grid: Grid):
    start_node = grid.start
    finish_node = grid.finish

    explored = set()
    revealed = set()
    parent = {}

    frontier = SearchPriorityQueue()
    frontier.put((0, start_node))

    while frontier.qsize() != 0:
        curr_path_cost, curr_node = frontier.get()
        explored.add(curr_node)

        if curr_node == finish_node:
            solution_path = deque()

            while parent.get(curr_node):
                solution_path.appendleft((curr_node, parent.get(curr_node)[1]))
                curr_node = parent.get(curr_node)[0]
            solution_path.appendleft((curr_node, 0))

            return (curr_path_cost, len(solution_path), solution_path)

        for child_node, path_cost in curr_node.children:
            child_path_cost = curr_path_cost + path_cost
            if child_node not in explored and child_node not in revealed:
                parent[child_node] = (curr_node, path_cost)
                revealed.add(child_node)

                frontier.put((child_path_cost, child_node))

            elif child_node not in explored and child_node in revealed:
                if frontier.update_priority(child_node, child_path_cost):
                    parent[child_node] = (curr_node, path_cost)
    return False


def a_star_search(grid: Grid):

    start_node = grid.start
    finish_node = grid.finish

    explored = set()
    revealed = set()
    parent = {}

    frontier = SearchPriorityQueue()
    frontier.put((0, 0, start_node))

    while frontier.qsize() != 0:
        _, actual_cost, curr_node = frontier.get()
        explored.add(curr_node)

        if curr_node == finish_node:
            solution_path = deque()

            while parent.get(curr_node):
                solution_path.appendleft((curr_node, parent.get(curr_node)[1]))
                curr_node = parent.get(curr_node)[0]
            solution_path.appendleft((curr_node, 0))

            return (actual_cost, len(solution_path), solution_path)

        for child_node, path_cost in curr_node.children:
            child_path_cost = actual_cost + path_cost + grid.sld[child_node.coords]
            if child_node not in explored and child_node not in revealed:
                parent[child_node] = (curr_node, path_cost)
                revealed.add(child_node)

                frontier.put((child_path_cost, actual_cost + path_cost, child_node))

            elif child_node not in explored and child_node in revealed:
                if frontier.update_priority(
                    child_node, child_path_cost, actual_cost + path_cost
                ):
                    parent[child_node] = (curr_node, path_cost)
    return False


if __name__ == "__main__":
    search_methods = {
        "BFS": breadth_first_search,
        "UCS": uniform_cost_search,
        "A*": a_star_search,
    }
    search_method, problem_grid = read_input_file()

    if problem_grid.start and problem_grid.finish:

        if problem_grid.start == problem_grid.finish:
            solution = (0, 1, [(problem_grid.start, 0)])
        else:
            if search_method == "A*":
                problem_grid.compute_heuristic()

            solution = search_methods[search_method](problem_grid)
    else:
        solution = False

    write_output_file(solution)
