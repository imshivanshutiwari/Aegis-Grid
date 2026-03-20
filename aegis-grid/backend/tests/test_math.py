import pytest
from main.domain.geospatial.algorithms import Haversine, AStar, KalmanFilter, DBSCAN

def test_haversine_distance_same_point():
    point = (0.0, 0.0)
    assert Haversine.distance(point, point) == 0.0

def test_haversine_distance_known():
    london = (-0.1278, 51.5074)
    paris = (2.3522, 48.8566)
    dist = Haversine.distance(london, paris)
    assert 340000 < dist < 350000

def test_astar_search():
    def get_neighbors(node): x, y = node; return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    start = (0, 0); goal = (2, 2)
    path = AStar.search(start, goal, get_neighbors, Haversine.distance)
    assert len(path) == 5; assert path[0] == start; assert path[-1] == goal

def test_kalman_filter():
    kf = KalmanFilter(process_variance=1e-5, estimated_measurement_variance=0.1)
    kf.input_latest_noisy_measurement(10.0)
    est1 = kf.get_latest_estimated_measurement()
    kf.input_latest_noisy_measurement(10.5)
    est2 = kf.get_latest_estimated_measurement()
    assert est1 != est2
    assert 10.0 < est2 <= 10.5

def test_dbscan_clustering():
    data = [(0.0, 0.0), (0.1, 0.1), (10.0, 10.0), (10.1, 10.1)]
    eps = 25000
    labels = DBSCAN.cluster(data, eps=eps, min_pts=2)
    assert labels[0] == labels[1]
    assert labels[2] == labels[3]
    assert labels[0] != labels[2]
