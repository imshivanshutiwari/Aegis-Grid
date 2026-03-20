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

class Vincenty:
    """Vincenty's formulae to calculate distance between two points on Earth's ellipsoid."""
    @staticmethod
    def distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        a = 6378137.0
        b = 6356752.314245
        f = 1 / 298.257223563
        L = math.radians(coord2[0] - coord1[0])
        U1 = math.atan((1 - f) * math.tan(math.radians(coord1[1])))
        U2 = math.atan((1 - f) * math.tan(math.radians(coord2[1])))
        sinU1 = math.sin(U1)
        cosU1 = math.cos(U1)
        sinU2 = math.sin(U2)
        cosU2 = math.cos(U2)
        lambda_val = L
        lambda_pi = 2 * math.pi
        iter_limit = 100
        while abs(lambda_val - lambda_pi) > 1e-12 and iter_limit > 0:
            sin_lambda = math.sin(lambda_val)
            cos_lambda = math.cos(lambda_val)
            sin_sigma = math.sqrt((cosU2 * sin_lambda) ** 2 + (cosU1 * sinU2 - sinU1 * cosU2 * cos_lambda) ** 2)
            if sin_sigma == 0:
                return 0.0
            cos_sigma = sinU1 * sinU2 + cosU1 * cosU2 * cos_lambda
            sigma = math.atan2(sin_sigma, cos_sigma)
            sin_alpha = cosU1 * cosU2 * sin_lambda / sin_sigma
            cos_sq_alpha = 1 - sin_alpha ** 2
            cos2_sigma_m = cos_sigma - 2 * sinU1 * sinU2 / cos_sq_alpha if cos_sq_alpha != 0 else 0
            C = f / 16 * cos_sq_alpha * (4 + f * (4 - 3 * cos_sq_alpha))
            lambda_pi = lambda_val
            lambda_val = L + (1 - C) * f * sin_alpha * (sigma + C * sin_sigma * (cos2_sigma_m + C * cos_sigma * (-1 + 2 * cos2_sigma_m ** 2)))
            iter_limit -= 1
        if iter_limit == 0:
            return float('nan')
        u_sq = cos_sq_alpha * (a ** 2 - b ** 2) / (b ** 2)
        A = 1 + u_sq / 16384 * (4096 + u_sq * (-768 + u_sq * (320 - 175 * u_sq)))
        B = u_sq / 1024 * (256 + u_sq * (-128 + u_sq * (74 - 47 * u_sq)))
        delta_sigma = B * sin_sigma * (cos2_sigma_m + B / 4 * (cos_sigma * (-1 + 2 * cos2_sigma_m ** 2) - B / 6 * cos2_sigma_m * (-3 + 4 * sin_sigma ** 2) * (-3 + 4 * cos2_sigma_m ** 2)))
        s = b * A * (sigma - delta_sigma)
        return s

class RayCasting:
    """Ray casting algorithm for Point in Polygon."""
    @staticmethod
    def is_inside(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
        x, y = point
        n = len(polygon)
        inside = False
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

class GrahamScan:
    """Graham Scan Convex Hull algorithm."""
    @staticmethod
    def get_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        if len(points) <= 3: return points
        def cross_product(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
        points = sorted(points)
        lower = []
        for p in points:
            while len(lower) >= 2 and cross_product(lower[-2], lower[-1], p) <= 0: lower.pop()
            lower.append(p)
        upper = []
        for p in reversed(points):
            while len(upper) >= 2 and cross_product(upper[-2], upper[-1], p) <= 0: upper.pop()
            upper.append(p)
        return lower[:-1] + upper[:-1]
class ThetaStar:
    """Theta* Pathfinding Algorithm."""
    @staticmethod
    def search(start: Tuple[float, float], goal: Tuple[float, float], get_neighbors: Callable, line_of_sight: Callable, heuristic: Callable) -> List[Tuple[float, float]]:
        import heapq
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {start: start}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}

        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == goal:
                path = []
                while current != came_from[current]:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path

            for neighbor in get_neighbors(current):
                if neighbor not in g_score:
                    g_score[neighbor] = float('inf')

                # Theta* core: Line of sight check
                parent = came_from[current]
                if line_of_sight(parent, neighbor):
                    tentative_g_score = g_score[parent] + Haversine.distance(parent, neighbor)
                    if tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = parent
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
                else:
                    tentative_g_score = g_score[current] + Haversine.distance(current, neighbor)
                    if tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return []
