# coding: utf-8
import math


def to_position(something):
    """Converts something (thing/position) to a position tuple."""
    if isinstance(something, tuple):
        return something
    else:
        return something.position


def distance(a, b):
    """Calculates distance between two positions or things."""
    x1, y1 = to_position(a)
    x2, y2 = to_position(b)

    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    return math.sqrt((dx ** 2) + (dy ** 2))


def manhattan_distance(a, b):
    x1, y1 = to_position(a)
    x2, y2 = to_position(b)
    return abs(x2 - x1) + abs(y2 - y1)


def sort_by_distance(something, others):
    by_distance = lambda other: distance(something, other)
    return sorted(others, key=by_distance)


def closest(something, others):
    """Returns the closest other to something (things/positions)."""
    if others:
        return sort_by_distance(something, others)[0]


def adjacent_positions(something):
    """Calculates the 4 adjacent positions of something (thing/position)."""
    position = to_position(something)
    deltas = ((0, 1),
              (0, -1),
              (1, 0),
              (-1, 0))

    return [(position[0] + delta[0],
             position[1] + delta[1])
            for delta in deltas]


def possible_moves(something, things):
    """Calculates the possible moves for a thing."""
    positions = [position for position in adjacent_positions(something)
                 if things.get(position) is None]

    return positions


def _reconstruct_path(came_from, goal):
    """Reconstructs the A* path, given the map of points 'came from', and the
    goal/end point."""

    path = [goal]
    while path[-1] in came_from:
        path.append(came_from[path[-1]])
    # remove start from path
    path.pop()
    return list(reversed(path))


def astar(start, goal, closed=set(), heuristic=manhattan_distance, goal_met=None, get_neighbors=adjacent_positions):
    """A* algorithm implementation to perform pathfinding between two points.

    :start - Start position
    :goal - End position
    :closed - Set of closed nodes (any nodes which should not be evaluated in
              pathfinding, e.g. `set(things.keys())`).  Defaults to empty set.

    :heuristic - A function over two points that returns a fast estimate of the
                 distance between them.  Defaults to Manhattan distance.

    :goal_met - A function over two points (A, Goal) that evaluates whether the
                point A is close enough to the Goal (e.g. Manhattan distance
                < 3).  Defaults to Manhattan distance == 0.

    :get_neighbors - A function over a point that returns all neighboring
                     points.  Defaults to the four cardinal directions.
    """

    if not goal_met:
        goal_met = lambda node, goal: heuristic(node, goal) <= 0
    elif isinstance(goal_met, int) or isinstance(goal_met, float):
        goal_met = lambda node, goal: heuristic(node, goal) <= goal_met
    else:
        goal_met = goal_met

    open_set = {start}
    closed = set(closed)
    if goal in closed:
        closed.remove(goal)
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    while open_set:
        best = min(open_set, key=lambda x: g_score[x])

        if goal_met(best, goal):
            path = _reconstruct_path(came_from, best)
            return path

        closed.add(best)
        open_set.remove(best)

        neighbors = get_neighbors(best)
        for neighbor in neighbors:
            if neighbor not in closed:
                score = g_score[best] + heuristic(best, neighbor)

                if neighbor not in open_set or score < g_score[neighbor]:
                    came_from[neighbor] = best
                    g_score[neighbor] = score
                    f_score[neighbor] = score + heuristic(neighbor, goal)
                    if neighbor not in open_set:
                        open_set.add(neighbor)
    return []