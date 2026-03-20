import math
from typing import Tuple, List, Callable
class Haversine:
    @staticmethod
    def distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        lon1, lat1 = coord1; lon2, lat2 = coord2
        R = 6371000; phi1 = math.radians(lat1); phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1); delta_lambda = math.radians(lon2 - lon1)
        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))
class AStar:
    @staticmethod
    def search(start: Tuple[float, float], goal: Tuple[float, float], get_neighbors: Callable, heuristic: Callable) -> List[Tuple[float, float]]:
        import heapq
        open_set = []; heapq.heappush(open_set, (0, start))
        came_from = {}; g_score = {start: 0}; f_score = {start: heuristic(start, goal)}
        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == goal:
                path = []
                while current in came_from: path.append(current); current = came_from[current]
                path.append(start); path.reverse(); return path
            for neighbor in get_neighbors(current):
                tentative_g_score = g_score[current] + Haversine.distance(current, neighbor)
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current; g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    if neighbor not in [i[1] for i in open_set]: heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return []
class KalmanFilter:
    def __init__(self, process_variance: float, estimated_measurement_variance: float):
        self.process_variance = process_variance
        self.estimated_measurement_variance = estimated_measurement_variance
        self.posteri_estimate = 0.0; self.posteri_error_estimate = 1.0; self.is_initialized = False
    def input_latest_noisy_measurement(self, measurement: float):
        if not self.is_initialized: self.posteri_estimate = measurement; self.is_initialized = True; return
        priori_estimate = self.posteri_estimate; priori_error_estimate = self.posteri_error_estimate + self.process_variance
        blending_factor = priori_error_estimate / (priori_error_estimate + self.estimated_measurement_variance)
        self.posteri_estimate = priori_estimate + blending_factor * (measurement - priori_estimate)
        self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate
    def get_latest_estimated_measurement(self) -> float: return self.posteri_estimate
class DBSCAN:
    @staticmethod
    def cluster(data: List[Tuple[float, float]], eps: float, min_pts: int) -> List[int]:
        labels = [0] * len(data); cluster_id = 0
        for i, point in enumerate(data):
            if labels[i] != 0: continue
            neighbors = [j for j, p in enumerate(data) if Haversine.distance(point, p) <= eps]
            if len(neighbors) < min_pts: labels[i] = -1; continue
            cluster_id += 1; labels[i] = cluster_id; seed_set = neighbors; seed_set.remove(i)
            while seed_set:
                current_point_idx = seed_set.pop(0)
                if labels[current_point_idx] == -1: labels[current_point_idx] = cluster_id
                if labels[current_point_idx] != 0: continue
                labels[current_point_idx] = cluster_id
                current_neighbors = [j for j, p in enumerate(data) if Haversine.distance(data[current_point_idx], p) <= eps]
                if len(current_neighbors) >= min_pts: seed_set.extend(current_neighbors)
        return labels
