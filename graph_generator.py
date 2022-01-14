import networkx as nx
import matplotlib.pyplot as plt
import random

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

ACTION_MAP_INVERSE = {v: k for k, v in ACTION_MAP.items()}


def generate_graph(size):
    G = nx.Graph()

    nodes = set(
        (x, y, z)
        for x in range(size[0])
        for y in range(size[1])
        for z in range(size[2])
        if random.random() > 0.7
    )
    G.add_nodes_from(nodes)

    weights = {}
    paths = {}
    for i in nodes:
        for x in range(-1, 1):
            for y in range(-1, 1):
                for z in range(-1, 1):
                    if x == 0 or y == 0 or z == 0:
                        nxt = (i[0] + x, i[1] + y, i[2] + z)
                        if nxt in nodes and i != nxt:
                            G.add_edge(i, nxt)

                            if paths.get(i):
                                paths[i].append((x, y, z))
                            else:
                                paths[i] = [(x, y, z)]

                            if paths.get(nxt):
                                paths[nxt].append((-x, -y, -z))
                            else:
                                paths[nxt] = [(-x, -y, -z)]

                            if (x and y) or (y and z) or (z and x):
                                weights[(i, nxt)] = 14
                            else:
                                weights[(i, nxt)] = 10

    nx.set_edge_attributes(G, weights, "weight")
    return G, paths


if __name__ == "__main__":
    for i in range(10, 101):
        graph_size = (10, 10, 10)
        G, paths = generate_graph(graph_size)

        search_method = random.choice(["A*"])

        start_node = random.choice(list(G.nodes()))
        finish_node = random.choice(list(G.nodes()))
        while finish_node == start_node:
            finish_node = random.choice(list(G.nodes()))

        if search_method == "UCS":
            heuristic = lambda n1, n2: 0
        else:
            heuristic = (
                lambda n1, n2: 0
                if n1 == n2
                else int(
                    sqrt(
                        pow((10 * n1[0] - 10 * n2[0]), 2)
                        + pow((10 * n1[1] - 10 * n2[1]), 2)
                        + pow((10 * n1[2] - 10 * n2[2]), 2)
                    )
                )
            )

        try:
            solution_path = nx.astar_path(
                G,
                start_node,
                finish_node,
                heuristic,
            )
        except nx.NetworkXNoPath:
            solution_path = False

        lines = [
            search_method,
            " ".join([str(x) for x in graph_size]),
            " ".join([str(x) for x in start_node]),
            " ".join([str(x) for x in finish_node]),
            str(len(G.nodes)),
        ] + [
            f"{k[0]} {k[1]} {k[2]} {' '.join([str(ACTION_MAP_INVERSE[x]) for x in v])}"
            for k, v in paths.items()
        ]

        with open(f".\\test_cases\input{i}.txt", "w") as f:
            f.write("\n".join([x for x in lines]))

        if start_node == finish_node:
            output = []
            output.append("0")
            output.append("1")
            node = " ".join([str(x) for x in start_node])
            output.append(node + " 0")
            output = "\n".join(output)
        elif solution_path:
            output = []
            output.append(str(nx.classes.path_weight(G, solution_path, "weight")))
            output.append(str(len(solution_path)))
            for line in range(len(solution_path)):
                if line != 0:
                    path_cost = str(
                        nx.classes.path_weight(
                            G, (solution_path[line - 1], solution_path[line]), "weight"
                        )
                    )
                else:
                    path_cost = 0
                output.append(
                    " ".join([str(x) for x in solution_path[line]])
                    + " "
                    + str(path_cost)
                )
            output = "\n".join(output)
        else:
            output = "FAIL"

        with open(f".\\test_cases\output{i}.txt", "w") as f:
            f.write(output)
