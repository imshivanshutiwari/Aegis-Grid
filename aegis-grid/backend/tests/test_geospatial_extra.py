import pytest
from main.domain.geospatial.algorithms import GrahamScan, RayCasting, ThetaStar

def test_graham_scan():
    points = [(0, 0), (0, 3), (3, 3), (3, 0), (1, 1)]
    hull = GrahamScan.get_hull(points)
    # The point (1, 1) is strictly inside, shouldn't be in the hull
    assert (1, 1) not in hull
    assert len(hull) >= 3

def test_ray_casting():
    polygon = [(0, 0), (0, 4), (4, 4), (4, 0)]
    assert RayCasting.is_inside((2, 2), polygon) is True
    assert RayCasting.is_inside((5, 5), polygon) is False

def test_theta_star():
    def get_neighbors(node):
        x, y = node
        return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    def line_of_sight(p1, p2):
        return True # Mock line of sight always clear
    def heuristic(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    start = (0, 0)
    goal = (2, 2)
    path = ThetaStar.search(start, goal, get_neighbors, line_of_sight, heuristic)
    assert len(path) > 0
    assert path[0] == start
    assert path[-1] == goal
