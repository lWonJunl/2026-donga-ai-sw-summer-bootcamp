from __future__ import annotations

import heapq
import json
import math
import os
import re
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
SQL_PATH = BASE_DIR / "navDay03.sql"
HOST = "127.0.0.1"
PORT = 8000
CURRENT_LOCATION_ID = "CURRENT_LOCATION"
RATE_LIMIT_WINDOW_SECONDS = 10
RATE_LIMIT_MAX_REQUESTS = 150
REFRESH_LIMIT_WINDOW_SECONDS = 10
REFRESH_LIMIT_MAX_REQUESTS = 5

_rate_limit_lock = threading.Lock()
_request_log: dict[str, deque[float]] = defaultdict(deque)
_refresh_log: dict[str, deque[float]] = defaultdict(deque)


def is_rate_limited(client_ip: str) -> bool:
    now = time.monotonic()
    with _rate_limit_lock:
        timestamps = _request_log[client_ip]
        while timestamps and now - timestamps[0] > RATE_LIMIT_WINDOW_SECONDS:
            timestamps.popleft()
        if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
            return True
        timestamps.append(now)
        return False


def is_refresh_limited(client_ip: str) -> bool:
    now = time.monotonic()
    with _rate_limit_lock:
        timestamps = _refresh_log[client_ip]
        while timestamps and now - timestamps[0] > REFRESH_LIMIT_WINDOW_SECONDS:
            timestamps.popleft()
        if len(timestamps) >= REFRESH_LIMIT_MAX_REQUESTS:
            return True
        timestamps.append(now)
        return False


def load_local_setting(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if value:
        return value

    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return ""

    for line in env_path.read_text(encoding="utf-8").splitlines():
        key, separator, raw_value = line.partition("=")
        if separator and key.strip() == name:
            return raw_value.strip().strip('"').strip("'")
    return ""


KAKAO_MAP_API_KEY = load_local_setting("KAKAO_MAP_API_KEY")


@dataclass(frozen=True)
class Place:
    place_id: str
    place_name: str
    latitude: float | None
    longitude: float | None
    altitude: float | None


@dataclass(frozen=True)
class Road:
    road_id: int
    from_place: str
    to_place: str
    road_type: str
    distance: int | None
    time: int | None
    twoway: bool
    indoor: bool
    stair: bool
    slope: int | None
    curve: int | None


def _extract_insert(sql: str, table_name: str) -> str:
    pattern = re.compile(
        rf"INSERT INTO {table_name} .*? VALUES\s*(.*?);",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(sql)
    if not match:
        raise ValueError(f"{table_name} INSERT 문을 찾을 수 없습니다.")
    return match.group(1)


def _split_rows(values_sql: str) -> list[str]:
    rows: list[str] = []
    start = None
    depth = 0
    in_string = False
    i = 0

    while i < len(values_sql):
        char = values_sql[i]
        next_char = values_sql[i + 1] if i + 1 < len(values_sql) else ""

        if char == "'":
            if in_string and next_char == "'":
                i += 2
                continue
            in_string = not in_string
        elif not in_string:
            if char == "(":
                if depth == 0:
                    start = i + 1
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0 and start is not None:
                    rows.append(values_sql[start:i])
                    start = None
        i += 1

    return rows


def _split_columns(row_sql: str) -> list[str]:
    columns: list[str] = []
    start = 0
    in_string = False
    i = 0

    while i < len(row_sql):
        char = row_sql[i]
        next_char = row_sql[i + 1] if i + 1 < len(row_sql) else ""

        if char == "'":
            if in_string and next_char == "'":
                i += 2
                continue
            in_string = not in_string
        elif char == "," and not in_string:
            columns.append(row_sql[start:i].strip())
            start = i + 1
        i += 1

    columns.append(row_sql[start:].strip())
    return columns


def _sql_value(raw: str):
    raw = raw.strip()
    if raw.upper() == "NULL":
        return None
    if raw.startswith("'") and raw.endswith("'"):
        return raw[1:-1].replace("''", "'")
    if "." in raw:
        return float(raw)
    return int(raw)


def _road_metadata(sql: str) -> dict[int, tuple[bool, int | None]]:
    pattern = re.compile(
        r"UPDATE\s+road_data\s+SET\s+twoway\s*=\s*(NULL|-?\d+)\s*,\s*"
        r"curve\s*=\s*(NULL|-?\d+)\s+WHERE\s+road_id\s*=\s*(\d+)\s*;",
        re.IGNORECASE,
    )
    metadata = {}
    for twoway_raw, curve_raw, road_id_raw in pattern.findall(sql):
        twoway = twoway_raw.upper() != "NULL" and bool(int(twoway_raw))
        curve = None if curve_raw.upper() == "NULL" else int(curve_raw)
        metadata[int(road_id_raw)] = (twoway, curve)
    return metadata


def load_navigation_data() -> tuple[dict[str, Place], dict[str, Place], list[Road]]:
    sql = SQL_PATH.read_text(encoding="utf-8")
    places: dict[str, Place] = {}
    geometry_waypoints: dict[str, Place] = {}
    roads: list[Road] = []

    for row_sql in _split_rows(_extract_insert(sql, "place_data")):
        place_id, place_name, latitude, longitude, altitude = [
            _sql_value(column) for column in _split_columns(row_sql)
        ]
        places[place_id] = Place(place_id, place_name or place_id, latitude, longitude, altitude)

    for row_sql in _split_rows(_extract_insert(sql, "waypoint_data")):
        place_id, place_name, latitude, longitude = [
            _sql_value(column) for column in _split_columns(row_sql)
        ]
        geometry_waypoints[place_id] = Place(
            place_id,
            place_name or place_id,
            latitude,
            longitude,
            None,
        )

    metadata = _road_metadata(sql)
    for row_sql in _split_rows(_extract_insert(sql, "road_data")):
        (
            road_id,
            from_place,
            to_place,
            road_type,
            distance,
            time,
            indoor,
            stair,
            slope,
        ) = [_sql_value(column) for column in _split_columns(row_sql)]
        twoway, curve = metadata.get(road_id, (False, None))
        roads.append(
            Road(
                road_id=road_id,
                from_place=from_place,
                to_place=to_place,
                road_type=road_type or "",
                distance=distance,
                time=time,
                twoway=twoway,
                indoor=bool(indoor),
                stair=bool(stair),
                slope=slope,
                curve=curve,
            )
        )

    return places, geometry_waypoints, roads


PLACES, GEOMETRY_WAYPOINTS, ROADS = load_navigation_data()
NAVIGATION_POINTS = {**PLACES, **GEOMETRY_WAYPOINTS}
CONNECTED_PLACE_IDS = {
    place_id
    for road in ROADS
    for place_id in (road.from_place, road.to_place)
    if place_id in NAVIGATION_POINTS
}


def is_representative_place(place_id: str) -> bool:
    if place_id == "GATE" or re.fullmatch(
        r"(?:BS\d{2}|PL\d{2}(?:-\d+)?)",
        place_id,
    ):
        return True
    match = re.fullmatch(r"S(\d{2})", place_id)
    return bool(match and 1 <= int(match.group(1)) <= 31)


def representative_sort_key(place_id: str) -> tuple[int, int, str]:
    if place_id == "GATE":
        return (0, 0, place_id)
    match = re.fullmatch(r"S(\d{2})", place_id)
    if match:
        return (1, int(match.group(1)), place_id)
    match = re.fullmatch(r"BS(\d{2})", place_id)
    if match:
        return (2, int(match.group(1)), place_id)
    match = re.fullmatch(r"PL(\d{2})(?:-\d+)?", place_id)
    if match:
        return (3, int(match.group(1)), place_id)
    return (4, 0, place_id)


def route_candidates(place_id: str) -> list[str]:
    if place_id not in PLACES:
        return []

    candidates = []
    if place_id in CONNECTED_PLACE_IDS:
        candidates.append(place_id)

    prefix = f"{place_id}-"
    candidates.extend(
        candidate_id
        for candidate_id in CONNECTED_PLACE_IDS
        if candidate_id.startswith(prefix)
    )

    building_match = re.fullmatch(r"S(\d{2})", place_id)
    if building_match:
        elevator_prefix = f"EL{building_match.group(1)}"
        candidates.extend(
            candidate_id
            for candidate_id in CONNECTED_PLACE_IDS
            if candidate_id == elevator_prefix or candidate_id.startswith(f"{elevator_prefix}-")
        )

    return sorted(set(candidates))


def normalize_place_code(place_id: str) -> str:
    value = place_id.strip()
    if not value:
        return ""
    if value in {"현위치", "현재위치", "내위치"}:
        return CURRENT_LOCATION_ID
    return value.upper().split()[0]


def parse_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def is_elevator_road(road: Road) -> bool:
    return road.from_place.startswith("EL") or road.to_place.startswith("EL")


def has_effective_stairs(road: Road) -> bool:
    return road.stair and not is_elevator_road(road)


def road_cost(
    road: Road,
    weight: str,
    travel_mode: str,
    avoid_stairs: bool,
    rainy: bool,
) -> float:
    base_cost = road.time if weight == "time" else road.distance
    if base_cost is None:
        base_cost = road.distance or road.time or 1

    cost = float(base_cost)

    if travel_mode == "walk" and avoid_stairs and has_effective_stairs(road):
        cost += 10000

    if travel_mode == "walk" and rainy and not road.indoor:
        cost += 30

    if road.slope:
        cost += road.slope

    return cost


def road_supports_mode(road: Road, travel_mode: str) -> bool:
    road_type = road.road_type.strip().lower()
    shared_types = {"도로", "road"}
    if road_type in shared_types:
        return True
    if travel_mode == "car":
        return road_type in {"차량", "차도", "car"}
    return road_type in {"도보", "보행", "walk"}


def is_parking_place(place_id: str) -> bool:
    return bool(re.fullmatch(r"PL\d+(?:-\d+)?", place_id))


def preferred_elevators(start: str, end: str) -> tuple[frozenset[str], bool]:
    all_elevators = frozenset(
        place_id for place_id in NAVIGATION_POINTS if place_id.startswith("EL")
    )
    return all_elevators, False


def elevator_progress(
    current: str,
    neighbor: str,
    used_elevators: int,
    elevator_entry: str,
    eligible_elevators: frozenset[str],
    elevator_bits: dict[str, int],
) -> tuple[int, str]:
    if current not in eligible_elevators and neighbor in eligible_elevators:
        return used_elevators, current
    if current in eligible_elevators and neighbor not in eligible_elevators:
        if elevator_entry and neighbor != elevator_entry:
            used_elevators |= elevator_bits[current]
        return used_elevators, ""
    return used_elevators, elevator_entry


def build_graph(
    weight: str,
    travel_mode: str,
    avoid_stairs: bool,
    rainy: bool,
) -> dict[str, list[tuple[float, str, Road]]]:
    graph: dict[str, list[tuple[float, str, Road]]] = {
        place_id: [] for place_id in NAVIGATION_POINTS
    }

    for road in ROADS:
        if not road_supports_mode(road, travel_mode):
            continue
        if road.from_place not in NAVIGATION_POINTS or road.to_place not in NAVIGATION_POINTS:
            continue
        cost = road_cost(road, weight, travel_mode, avoid_stairs, rainy)
        graph[road.from_place].append((float(cost), road.to_place, road))
        if road.twoway:
            graph[road.to_place].append((float(cost), road.from_place, road))

    return graph


def haversine_meters(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> int:
    radius = 6371000
    lat_a = math.radians(latitude_a)
    lat_b = math.radians(latitude_b)
    delta_lat = math.radians(latitude_b - latitude_a)
    delta_lng = math.radians(longitude_b - longitude_a)
    value = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat_a) * math.cos(lat_b) * math.sin(delta_lng / 2) ** 2
    )
    return int(round(radius * 2 * math.atan2(math.sqrt(value), math.sqrt(1 - value))))


def current_location_place(latitude: float, longitude: float) -> dict:
    return {
        "id": CURRENT_LOCATION_ID,
        "name": "현위치",
        "latitude": latitude,
        "longitude": longitude,
        "altitude": None,
    }


def nearest_connected_candidates(latitude: float, longitude: float, limit: int = 5) -> list[str]:
    distances = []
    for place_id in CONNECTED_PLACE_IDS:
        place = NAVIGATION_POINTS.get(place_id)
        if place and place.latitude is not None and place.longitude is not None:
            distances.append(
                (haversine_meters(latitude, longitude, place.latitude, place.longitude), place_id)
            )
    return [place_id for _, place_id in sorted(distances)[:limit]]


def current_location_step(from_place: dict, to_place: dict) -> dict:
    distance = haversine_meters(
        from_place["latitude"],
        from_place["longitude"],
        to_place["latitude"],
        to_place["longitude"],
    )
    return {
        "from": from_place,
        "to": to_place,
        "road_type": "현재 위치 연결",
        "travel_mode": "walk",
        "distance": distance,
        "time": max(1, round(distance / 0.56)),
        "twoway": True,
        "indoor": False,
        "stair": False,
        "slope": None,
        "curve": None,
    }


def find_route_segment(
    start: str,
    end: str,
    weight: str,
    travel_mode: str = "car",
    avoid_stairs: bool = False,
    rainy: bool = False,
    prefer_elevator: bool = False,
    current_lat: float | None = None,
    current_lng: float | None = None,
) -> dict:
    start = normalize_place_code(start)
    end = normalize_place_code(end)
    weight = weight if weight in {"distance", "time"} else "distance"
    travel_mode = travel_mode if travel_mode in {"car", "walk"} else "car"
    start_is_current = start == CURRENT_LOCATION_ID
    end_is_current = end == CURRENT_LOCATION_ID
    current_place = (
        current_location_place(current_lat, current_lng)
        if current_lat is not None and current_lng is not None
        else None
    )

    if (start_is_current or end_is_current) and current_place is None:
        return {"ok": False, "message": "현재 위치를 가져오지 못했습니다. 브라우저 위치 권한을 확인하세요."}
    if not start_is_current and start not in PLACES:
        return {"ok": False, "message": "출발지를 찾을 수 없습니다."}
    if not end_is_current and end not in PLACES:
        return {"ok": False, "message": "도착지를 찾을 수 없습니다."}
    if start == end:
        place = current_place if start_is_current else place_to_dict(PLACES[start])
        return {
            "ok": True,
            "total_distance": 0,
            "total_time": 0,
            "_search_cost": 0,
            "path": [place],
            "steps": [],
            "start": place,
            "end": place,
        }

    baseline_result = None
    preferred_cost_limit = None
    if prefer_elevator:
        baseline_result = find_route_segment(
            start,
            end,
            weight,
            travel_mode,
            avoid_stairs,
            rainy,
            False,
            current_lat,
            current_lng,
        )
        if baseline_result.get("ok"):
            preferred_cost_limit = max(
                1.0,
                float(baseline_result.get("_search_cost", 0)),
            ) * 3

    eligible_elevators, _ = (
        preferred_elevators(start, end)
        if prefer_elevator
        else (frozenset(), False)
    )
    elevator_bits = {
        elevator_id: 1 << index
        for index, elevator_id in enumerate(sorted(eligible_elevators))
    }
    required_elevator_mask = (1 << len(elevator_bits)) - 1
    require_elevator = required_elevator_mask != 0
    max_preferred_elevators = 4

    start_candidates = (
        nearest_connected_candidates(current_lat, current_lng) if start_is_current else route_candidates(start)
    )
    end_candidates = (
        nearest_connected_candidates(current_lat, current_lng) if end_is_current else route_candidates(end)
    )
    if not start_candidates:
        return {"ok": False, "message": "출발 건물과 연결된 출입구 경로가 없습니다."}
    if not end_candidates:
        return {"ok": False, "message": "도착 건물과 연결된 출입구 경로가 없습니다."}

    if require_elevator and not start_is_current and len(start_candidates) > 1:
        representative = PLACES[start]
        candidates_with_coordinates = [
            candidate
            for candidate in start_candidates
            if NAVIGATION_POINTS[candidate].latitude is not None
            and NAVIGATION_POINTS[candidate].longitude is not None
        ]
        if (
            representative.latitude is not None
            and representative.longitude is not None
            and candidates_with_coordinates
        ):
            start_candidates = [
                min(
                    candidates_with_coordinates,
                    key=lambda candidate: haversine_meters(
                        representative.latitude,
                        representative.longitude,
                        NAVIGATION_POINTS[candidate].latitude,
                        NAVIGATION_POINTS[candidate].longitude,
                    ),
                )
            ]

    walk_graph = build_graph(weight, "walk", avoid_stairs, rainy)
    car_graph = build_graph(weight, "car", avoid_stairs, rainy) if travel_mode == "car" else {}
    queue: list[tuple[float, str, str, int, str]] = []
    start_states: set[tuple[str, str, int, str]] = set()

    for place_id in start_candidates:
        elevator_entry = "__START__" if place_id in eligible_elevators else ""
        if travel_mode == "walk":
            start_states.add((place_id, "walk", 0, elevator_entry))
        elif car_graph.get(place_id):
            start_states.add((place_id, "car_ready@", 0, elevator_entry))
        else:
            start_states.add((place_id, "access_walk", 0, elevator_entry))

    for place_id, phase, used_elevators, elevator_entry in start_states:
        heapq.heappush(
            queue,
            (0, place_id, phase, used_elevators, elevator_entry),
        )

    costs = {state: 0.0 for state in start_states}
    previous: dict[
        tuple[str, str, int, str],
        tuple[tuple[str, str, int, str], Road | None, str | None],
    ] = {}
    end_candidate_set = set(end_candidates)
    destination_elevators = end_candidate_set & eligible_elevators
    reached_state: tuple[str, str, int, str] | None = None
    reached_states: list[tuple[int, float, tuple[str, str, int, str]]] = []

    while queue:
        current_cost, current, phase, used_elevators, elevator_entry = heapq.heappop(queue)
        current_state = (current, phase, used_elevators, elevator_entry)
        if current_cost > costs.get(current_state, float("inf")):
            continue
        if preferred_cost_limit is not None and current_cost > preferred_cost_limit:
            break
        phase_kind, _, parking_origin = phase.partition("@")
        valid_end_phase = travel_mode == "walk" or phase_kind in {"car_moving", "egress_walk"}
        reached_destination_elevator = current in destination_elevators
        elevator_requirement_met = (
            not require_elevator
            or used_elevators != 0
            or reached_destination_elevator
        )
        at_destination = current in end_candidate_set and valid_end_phase
        if at_destination:
            if elevator_requirement_met:
                elevator_count = used_elevators.bit_count()
                if (
                    reached_destination_elevator
                    and not used_elevators & elevator_bits[current]
                ):
                    elevator_count += 1
                reached_states.append(
                    (elevator_count, current_cost, current_state)
                )

        neighbors: list[
            tuple[float, tuple[str, str, int, str], Road | None, str | None]
        ] = []
        if phase_kind in {"walk", "access_walk", "egress_walk"}:
            for edge_cost, neighbor, road in walk_graph.get(current, []):
                if at_destination:
                    if current in destination_elevators:
                        if neighbor not in end_candidate_set:
                            continue
                    elif neighbor not in destination_elevators:
                        continue
                if (
                    neighbor in elevator_bits
                    and (
                        used_elevators & elevator_bits[neighbor]
                        or used_elevators.bit_count() >= max_preferred_elevators
                    )
                ):
                    continue
                next_used_elevators, next_elevator_entry = elevator_progress(
                    current,
                    neighbor,
                    used_elevators,
                    elevator_entry,
                    eligible_elevators,
                    elevator_bits,
                )
                neighbors.append(
                    (
                        edge_cost,
                        (neighbor, phase, next_used_elevators, next_elevator_entry),
                        road,
                        "walk",
                    )
                )
        if phase_kind in {"car_ready", "car_moving"}:
            for edge_cost, neighbor, road in car_graph.get(current, []):
                if at_destination:
                    if current in destination_elevators:
                        if neighbor not in end_candidate_set:
                            continue
                    elif neighbor not in destination_elevators:
                        continue
                if (
                    neighbor in elevator_bits
                    and (
                        used_elevators & elevator_bits[neighbor]
                        or used_elevators.bit_count() >= max_preferred_elevators
                    )
                ):
                    continue
                next_used_elevators, next_elevator_entry = elevator_progress(
                    current,
                    neighbor,
                    used_elevators,
                    elevator_entry,
                    eligible_elevators,
                    elevator_bits,
                )
                neighbors.append(
                    (
                        edge_cost,
                        (
                            neighbor,
                            f"car_moving@{parking_origin}",
                            next_used_elevators,
                            next_elevator_entry,
                        ),
                        road,
                        "car",
                    )
                )
        if travel_mode == "car" and phase_kind == "access_walk" and is_parking_place(current):
            neighbors.append(
                (
                    0,
                    (current, f"car_ready@{current}", used_elevators, elevator_entry),
                    None,
                    None,
                )
            )
        can_park = not parking_origin or current != parking_origin
        if (
            travel_mode == "car"
            and phase_kind == "car_moving"
            and is_parking_place(current)
            and can_park
        ):
            neighbors.append(
                (0, (current, "egress_walk", used_elevators, elevator_entry), None, None)
            )

        for edge_cost, next_state, road, edge_mode in neighbors:
            next_cost = current_cost + edge_cost
            if next_cost < costs.get(next_state, float("inf")):
                costs[next_state] = next_cost
                previous[next_state] = (current_state, road, edge_mode)
                heapq.heappush(
                    queue,
                    (
                        next_cost,
                        next_state[0],
                        next_state[1],
                        next_state[2],
                        next_state[3],
                    ),
                )

    if reached_states:
        reached_state = max(
            reached_states,
            key=lambda item: (item[0], -item[1]),
        )[2]

    if reached_state is None:
        if require_elevator:
            if baseline_result is not None:
                return baseline_result
            return find_route_segment(
                start, end, weight, travel_mode, avoid_stairs, rainy, False,
                current_lat, current_lng,
            )
        return {"ok": False, "message": "연결된 경로를 찾을 수 없습니다."}

    route_edges = []
    cursor_state = reached_state
    while cursor_state not in start_states:
        before_state, road, edge_mode = previous[cursor_state]
        if road is not None:
            route_edges.append((before_state[0], cursor_state[0], road, edge_mode))
        cursor_state = before_state
    route_edges.reverse()

    steps = []
    total_distance = 0
    total_time = 0
    for before, after, road, edge_mode in route_edges:
        total_distance += road.distance or 0
        total_time += road.time or 0
        elevator_road = is_elevator_road(road)
        steps.append(
            {
                "from": place_to_dict(NAVIGATION_POINTS[before]),
                "to": place_to_dict(NAVIGATION_POINTS[after]),
                "road_type": road.road_type,
                "travel_mode": edge_mode,
                "distance": road.distance,
                "time": road.time,
                "twoway": road.twoway,
                "indoor": road.indoor,
                "stair": has_effective_stairs(road),
                "elevator": elevator_road,
                "slope": road.slope,
                "curve": road.curve,
            }
        )

    path_ids = [route_edges[0][0]] if route_edges else [reached_state[0]]
    path_ids.extend(after for _, after, _, _ in route_edges)
    path = [place_to_dict(NAVIGATION_POINTS[place_id]) for place_id in path_ids]

    if start_is_current and path:
        step = current_location_step(current_place, path[0])
        path.insert(0, current_place)
        steps.insert(0, step)
        total_distance += step["distance"]
        total_time += step["time"]

    if end_is_current and path:
        step = current_location_step(path[-1], current_place)
        path.append(current_place)
        steps.append(step)
        total_distance += step["distance"]
        total_time += step["time"]

    return {
        "ok": True,
        "total_distance": total_distance,
        "total_time": total_time,
        "_search_cost": costs[reached_state],
        "path": path,
        "steps": steps,
        "start": current_place if start_is_current else place_to_dict(PLACES[start]),
        "end": current_place if end_is_current else place_to_dict(PLACES[end]),
    }


def find_route(
    start: str,
    end: str,
    weight: str,
    travel_mode: str = "car",
    avoid_stairs: bool = False,
    rainy: bool = False,
    prefer_elevator: bool = False,
    waypoints: list[str] | None = None,
    current_lat: float | None = None,
    current_lng: float | None = None,
) -> dict:
    points = [normalize_place_code(start)]
    points.extend(normalize_place_code(point) for point in (waypoints or []) if normalize_place_code(point))
    points.append(normalize_place_code(end))

    if len(points) < 2 or not points[0] or not points[-1]:
        return {"ok": False, "message": "출발지와 도착지를 모두 입력하세요."}

    def display_place(point: str) -> dict:
        if point == CURRENT_LOCATION_ID and current_lat is not None and current_lng is not None:
            return current_location_place(current_lat, current_lng)
        if point in PLACES:
            return place_to_dict(PLACES[point])
        return {"id": point, "name": point, "latitude": None, "longitude": None, "altitude": None}

    combined_path = []
    combined_steps = []
    waypoint_summaries = []
    total_distance = 0
    total_time = 0

    for index in range(len(points) - 1):
        result = find_route_segment(
            points[index],
            points[index + 1],
            weight,
            travel_mode,
            avoid_stairs,
            rainy,
            prefer_elevator,
            current_lat,
            current_lng,
        )
        if not result.get("ok"):
            return {
                "ok": False,
                "message": f"{index + 1}번째 구간: {result.get('message', '경로를 찾을 수 없습니다.')}",
            }

        if index == 0:
            combined_path.extend(result["path"])
        else:
            combined_path.extend(result["path"][1:])
        combined_steps.extend(result["steps"])
        total_distance += result["total_distance"]
        total_time += result["total_time"]
        if index < len(points) - 2:
            waypoint = points[index + 1]
            if waypoint == CURRENT_LOCATION_ID and current_lat is not None and current_lng is not None:
                waypoint_info = current_location_place(current_lat, current_lng)
            elif waypoint in PLACES:
                waypoint_info = place_to_dict(PLACES[waypoint])
            else:
                waypoint_info = None
            if waypoint_info:
                waypoint_info["after_step_index"] = len(combined_steps)
                waypoint_summaries.append(waypoint_info)

    return {
        "ok": True,
        "total_distance": total_distance,
        "total_time": total_time,
        "path": combined_path,
        "steps": combined_steps,
        "start": display_place(points[0]),
        "end": display_place(points[-1]),
        "waypoints": waypoint_summaries,
    }


def place_to_dict(place: Place) -> dict:
    return {
        "id": place.place_id,
        "name": place.place_name,
        "latitude": place.latitude,
        "longitude": place.longitude,
        "altitude": place.altitude,
    }


def api_places() -> list[dict]:
    return sorted(
        [
            place_to_dict(place)
            for place in PLACES.values()
            if is_representative_place(place.place_id)
        ],
        key=lambda item: representative_sort_key(item["id"]),
    )


def api_map_places() -> list[dict]:
    return [place_to_dict(place) for place in PLACES.values()]


INDEX_HTML = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>동아대학교 승학캠퍼스 길찾기</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #17212b;
      --muted: #66717f;
      --line: #d8e0e8;
      --panel: #ffffff;
      --paper: #f5f7fa;
      --green: #167c68;
      --blue: #2463b6;
      --orange: #c8652b;
      --danger: #ba3b46;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: Arial, "Noto Sans KR", sans-serif;
      color: var(--ink);
      background: var(--paper);
    }

    .app {
      height: 100vh;
      display: grid;
      grid-template-columns: minmax(320px, 420px) 1fr;
      grid-template-rows: auto minmax(0, 1fr);
      transition: grid-template-columns 0.18s ease;
    }

    .app.route-collapsed {
      grid-template-columns: 52px 1fr;
    }

    aside {
      background: #f8fafc;
      border-bottom: 1px solid var(--line);
      padding: 14px 16px;
      overflow: visible;
    }

    .controls {
      grid-column: 1 / -1;
      display: grid;
      grid-template-columns: 250px minmax(480px, 1.6fr) minmax(360px, 1.3fr) 120px;
      grid-template-rows: auto auto;
      gap: 8px 10px;
      align-items: start;
    }

    .controls-header {
      display: contents;
    }

    .controls-header > div {
      grid-column: 1;
      grid-row: 1 / 3;
      align-self: start;
      display: block;
    }

    .controls-header h1 {
      margin: 0 0 2px;
    }

    .controls-header .sub {
      margin: 0;
    }

    .controls-body {
      display: contents;
    }

    .route-inputs {
      grid-column: 2;
      grid-row: 1 / 3;
      display: grid;
      grid-template-columns: minmax(0, 1fr) 32px minmax(0, 1fr) 92px;
      gap: 4px 10px;
      align-items: start;
    }

    .route-inputs > .search-field:first-child {
      grid-column: 1;
      grid-row: 1;
      align-self: start;
    }

    .route-inputs > .swap-button {
      grid-column: 2;
      grid-row: 1;
      align-self: start;
      margin-top: 18px;
    }

    .route-inputs > .search-field:nth-of-type(2) {
      grid-column: 3;
      grid-row: 1;
      align-self: start;
    }

    .option-row {
      grid-column: 3;
      grid-row: 1;
    }

    .waypoint-control {
      display: contents;
    }

    .controls-body > .primary {
      grid-column: 4;
      grid-row: 2;
      align-self: end;
    }

    #toggle-controls {
      grid-column: 4;
      grid-row: 1;
      justify-self: end;
      align-self: start;
    }

    .controls.collapsed {
      grid-template-rows: auto;
    }

    .controls.collapsed .controls-header > div,
    .controls.collapsed .controls-body {
      display: none;
    }

    .panel-toggle {
      flex: 0 0 auto;
      width: 30px;
      height: 30px;
      min-height: 30px;
      padding: 0;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: #fff;
      color: var(--ink);
      cursor: pointer;
      font-size: 13px;
      line-height: 1;
      box-shadow: 0 1px 2px rgb(15 23 42 / 5%);
    }

    .panel-toggle:hover,
    .panel-toggle:focus {
      border-color: var(--blue);
      color: var(--blue);
      outline: none;
    }

    .panel-toggle.rainbow-easter-egg {
      border-color: transparent;
      background: linear-gradient(
        90deg,
        #ff4d4d,
        #ffb84d,
        #fff04d,
        #4dcc70,
        #4da6ff,
        #8359d9,
        #ff5ebc,
        #ff4d4d
      );
      background-size: 300% 100%;
      color: #172033;
      box-shadow: 0 0 0 2px #fff, 0 0 14px rgb(255 94 188 / 70%);
      animation: rainbow-button-shift 1.8s linear infinite, rainbow-button-sparkle 900ms ease-in-out infinite alternate;
    }

    @keyframes rainbow-button-shift {
      to { background-position: 100% 0; }
    }

    @keyframes rainbow-button-sparkle {
      from { box-shadow: 0 0 0 2px #fff, 0 0 8px rgb(77 166 255 / 55%); }
      to { box-shadow: 0 0 0 2px #fff, 0 0 18px rgb(255 94 188 / 85%); }
    }

    @media (prefers-reduced-motion: reduce) {
      .panel-toggle.rainbow-easter-egg {
        animation: none;
      }
    }

    .panel-toggle .chevron {
      display: inline-block;
      transition: transform 0.15s ease;
    }

    #toggle-route-panel .chevron {
      transform: rotate(180deg);
    }

    .app.route-collapsed #toggle-route-panel .chevron {
      transform: rotate(0deg);
    }

    .route-inputs .search-field label {
      margin-top: 0;
    }

    .option-row {
      display: flex;
      flex-wrap: nowrap;
      gap: 8px;
      align-self: start;
    }

    .option-row > .option-group {
      flex: 1 1 84px;
      min-width: 84px;
    }

    .option-row > .option-group.options-group {
      flex: 1.6 1 160px;
      min-width: 160px;
    }

    .option-row label {
      margin-top: 0;
    }

    .route-panel {
      min-height: 0;
      padding: 12px;
      overflow-y: auto;
      overflow-x: hidden;
      background: var(--panel);
      border-right: 1px solid var(--line);
    }

    .route-panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 10px;
    }

    .route-panel-header h2 {
      margin: 0;
      font-size: 14px;
      color: var(--ink);
      white-space: nowrap;
    }

    .app.route-collapsed .route-panel {
      padding: 14px 10px;
    }

    .app.route-collapsed .route-panel-header {
      justify-content: center;
    }

    .app.route-collapsed .route-panel-header h2,
    .app.route-collapsed .route-panel-body {
      display: none;
    }

    main {
      min-width: 0;
      min-height: 0;
      padding: 12px;
      display: grid;
      grid-template-rows: minmax(360px, 1fr) auto;
      gap: 10px;
    }

    h1 {
      margin: 0 0 2px;
      font-size: 17px;
      line-height: 1.25;
    }

    .sub {
      margin: 0 0 8px;
      color: var(--muted);
      font-size: 10.5px;
      line-height: 1.3;
    }

    label {
      display: block;
      margin: 6px 0 3px;
      font-size: 12px;
      font-weight: 700;
    }

    input, button {
      width: 100%;
      min-height: 32px;
      border-radius: 7px;
      border: 1px solid var(--line);
      font: inherit;
    }

    input {
      padding: 0 10px;
      background: #fff;
      color: var(--ink);
      font-size: 13px;
      box-shadow: 0 1px 2px rgb(15 23 42 / 5%);
    }

    .search-field {
      position: relative;
    }

    .swap-button {
      width: 32px;
      height: 32px;
      min-height: 32px;
      margin: 0;
      padding: 0;
      display: grid;
      place-items: center;
      border-color: var(--line);
      background: #fff;
      color: var(--blue);
      cursor: pointer;
      font-size: 17px;
      font-weight: 700;
      line-height: 1;
      box-shadow: 0 1px 4px rgb(0 0 0 / 10%);
    }

    .swap-button:hover,
    .swap-button:focus {
      border-color: var(--blue);
      background: #eef4f7;
      outline: none;
      transform: translateY(-1px);
    }

    .suggestions {
      position: absolute;
      z-index: 20;
      top: calc(100% + 4px);
      left: 0;
      right: 0;
      display: none;
      max-height: 220px;
      overflow-y: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      box-shadow: 0 10px 26px rgb(0 0 0 / 14%);
    }

    .suggestions.show {
      display: block;
    }

    .suggestion {
      width: 100%;
      min-height: 32px;
      padding: 6px 10px;
      border: 0;
      border-radius: 0;
      background: #fff;
      color: var(--ink);
      text-align: left;
      cursor: pointer;
    }

    .suggestion:hover,
    .suggestion:focus {
      background: #eef4f7;
      outline: none;
    }

    .suggestion strong,
    .suggestion span {
      display: block;
      line-height: 1.35;
    }

    .suggestion span {
      color: var(--muted);
      font-size: 12px;
    }

    .mode {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 3px;
      margin-top: 0;
      padding: 3px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
    }

    .mode button {
      min-height: 26px;
      border: 0;
      border-radius: 6px;
      background: transparent;
      color: var(--ink);
      cursor: pointer;
      font-size: 12px;
    }

    .mode button.active {
      background: var(--green);
      border-color: var(--green);
      color: #fff;
      font-weight: 700;
    }

    .options {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 0;
    }

    .check-option {
      display: flex;
      align-items: center;
      gap: 6px;
      min-height: 32px;
      padding: 0 9px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      color: var(--ink);
      font-size: 12px;
      font-weight: 500;
      white-space: nowrap;
    }

    .check-option input {
      width: 15px;
      min-height: 15px;
      height: 15px;
      margin: 0;
    }

    .primary {
      margin-top: 0;
      min-height: 34px;
      border: 0;
      background: var(--blue);
      color: #fff;
      font-weight: 700;
      cursor: pointer;
    }

    .waypoint-title {
      grid-column: 4;
      grid-row: 1;
      align-self: start;
      display: grid;
      gap: 3px;
      margin-top: 0;
      white-space: nowrap;
    }

    #waypoints {
      grid-column: 1 / 4;
      grid-row: 2;
      display: grid;
      gap: 4px;
    }

    .waypoint-title label {
      margin: 0 0 3px;
    }

    .add-waypoint {
      width: 100%;
      min-height: 32px;
      padding: 0 14px;
      background: #fff;
      color: var(--blue);
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 1px 2px rgb(15 23 42 / 5%);
    }

    .waypoint-row {
      display: grid;
      grid-template-columns: 1fr 32px;
      gap: 6px;
      margin-top: 0;
    }

    .remove-waypoint {
      min-height: 32px;
      padding: 0;
      background: #fff;
      color: var(--danger);
      font-size: 18px;
      font-weight: 700;
      cursor: pointer;
    }

    .stats {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-top: 8px;
    }

    .stat {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 6px 8px;
      background: #fbfcfe;
    }

    .stat span {
      display: block;
      color: var(--muted);
      font-size: 11px;
      margin-bottom: 3px;
    }

    .stat strong {
      font-size: 16px;
    }

    .error {
      margin-top: 10px;
      color: var(--danger);
      font-weight: 700;
      line-height: 1.45;
    }

    .steps {
      margin-top: 8px;
    }

    .step {
      display: grid;
      grid-template-columns: 28px 1fr;
      gap: 8px;
      padding: 8px 0;
      border-top: 1px solid var(--line);
    }

    .badge {
      width: 28px;
      height: 28px;
      border-radius: 999px;
      background: var(--green);
      color: #fff;
      display: grid;
      place-items: center;
      font-size: 12px;
      font-weight: 700;
    }

    .step.waypoint {
      background: #fff8ec;
      margin: 0 -8px;
      padding: 10px 8px;
      border-top-color: #f0c88b;
      border-radius: 8px;
    }

    .step.waypoint .badge {
      background: var(--orange);
    }

    .step.waypoint strong {
      color: var(--orange);
    }

    .step.endpoint {
      background: #eef6f3;
      margin: 0 -8px;
      padding: 10px 8px;
      border-top-color: #b9d9d0;
      border-radius: 8px;
    }

    .step.endpoint.end {
      background: #eef3fb;
      border-top-color: #bed0ec;
    }

    .step.endpoint.start .badge {
      background: var(--green);
    }

    .step.endpoint.end .badge {
      background: var(--blue);
    }

    .step.endpoint.start strong {
      color: var(--green);
    }

    .step.endpoint.end strong {
      color: var(--blue);
    }

    .step strong {
      display: block;
      font-size: 14px;
      line-height: 1.4;
    }

    .step span {
      color: var(--muted);
      font-size: 12px;
    }

    .step-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 7px;
    }

    .chip {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 0 8px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      color: var(--muted);
      font-size: 12px;
      line-height: 1;
    }

    .chip.on {
      border-color: var(--green);
      color: var(--green);
      font-weight: 700;
    }

    .map-shell {
      min-height: 360px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #eef4f7;
      overflow: hidden;
      position: relative;
    }

    #map {
      width: 100%;
      height: 100%;
      min-height: 360px;
      position: absolute;
      inset: 0;
    }

    .map-message {
      position: absolute;
      inset: 0;
      z-index: 5;
      display: none;
      place-items: center;
      background: #fff;
      color: var(--ink);
      padding: 24px;
      text-align: center;
      line-height: 1.55;
    }

    .map-message.show {
      display: grid;
    }

    .map-message strong {
      display: block;
      margin-bottom: 8px;
      font-size: 18px;
    }

    .legend {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 12px 14px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
    }

    @media (max-width: 1280px) {
      .app,
      .app.route-collapsed {
        grid-template-columns: 1fr;
        grid-template-rows: auto auto 420px;
        height: auto;
        min-height: 100vh;
      }

      .controls {
        display: flex;
        flex-direction: column;
        gap: 10px;
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }

      .controls-header,
      .controls-header > div,
      .controls-body,
      .route-inputs {
        display: block;
      }

      .swap-button {
        justify-self: center;
        margin: 8px auto;
      }

      .option-row {
        display: flex;
      }

      .waypoint-control {
        display: block;
      }

      .route-panel {
        border-right: 0;
        border-bottom: 1px solid var(--line);
        max-height: 420px;
      }

      .app.route-collapsed .route-panel {
        max-height: none;
      }

      .app.route-collapsed .route-panel-header {
        justify-content: space-between;
      }

      .app.route-collapsed .route-panel-header h2 {
        display: block;
      }

      #toggle-route-panel .chevron {
        transform: rotate(-90deg);
      }

      .app.route-collapsed #toggle-route-panel .chevron {
        transform: rotate(90deg);
      }

      main {
        grid-template-rows: 420px auto;
        padding: 14px;
      }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside class="controls">
      <div class="controls-header">
        <div>
          <h1>동아대학교 승학캠퍼스 길찾기</h1>
          <p class="sub">출발 건물과 도착 건물을 선택하면 연결된 출입구를 기준으로 최단 경로를 계산합니다.</p>
        </div>
        <button type="button" class="panel-toggle" id="toggle-controls" aria-expanded="true" aria-label="입력 패널 접기/펴기" title="입력 패널 접기/펴기">▲</button>
      </div>

      <div class="controls-body" id="controls-body">
        <div class="route-inputs">
          <div class="search-field">
            <label for="start">출발지</label>
            <input id="start" autocomplete="off" placeholder="예: 정문" />
            <div id="start-suggestions" class="suggestions"></div>
          </div>

          <button type="button" class="swap-button" id="swap-route" aria-label="출발지와 도착지 바꾸기" title="출발지와 도착지 바꾸기">⇄</button>

          <div class="search-field">
            <label for="end">도착지</label>
            <input id="end" autocomplete="off" placeholder="예: 공대5호관" />
            <div id="end-suggestions" class="suggestions"></div>
          </div>

          <div class="waypoint-control">
            <div class="waypoint-title">
              <label>경유지</label>
              <button type="button" class="add-waypoint" id="add-waypoint">+ 추가</button>
            </div>
            <div id="waypoints"></div>
          </div>
        </div>

        <div class="option-row">
          <div class="option-group">
            <label>경로 검색 기준</label>
            <div class="mode">
              <button type="button" class="active" data-weight="distance">거리</button>
              <button type="button" data-weight="time">시간</button>
            </div>
          </div>

          <div class="option-group">
            <label>이동 방식</label>
            <div class="mode">
              <button type="button" class="active" data-travel-mode="car">차량</button>
              <button type="button" data-travel-mode="walk">도보</button>
            </div>
          </div>

          <div class="option-group options-group">
            <label>경로 검색 옵션</label>
            <div class="options">
              <label class="check-option">
                <input type="checkbox" id="avoid-stairs" />
                계단 최소화
              </label>
              <label class="check-option">
                <input type="checkbox" id="rainy" />
                실내 위주
              </label>
              <label class="check-option">
                <input type="checkbox" id="prefer-elevator" />
                엘리베이터 우선
              </label>
            </div>
          </div>
        </div>

        <button type="button" class="primary" id="search">경로 찾기</button>
      </div>
    </aside>

    <section class="route-panel">
      <div class="route-panel-header">
        <h2>경로 정보</h2>
        <button type="button" class="panel-toggle" id="toggle-route-panel" aria-expanded="true" aria-label="경로 패널 접기/펴기" title="경로 패널 접기/펴기"><span class="chevron">▶</span></button>
      </div>

      <div class="route-panel-body" id="route-panel-body">
        <div id="error" class="error" hidden></div>

        <div class="stats">
          <div class="stat">
            <span>총 거리</span>
            <strong id="distance">-</strong>
          </div>
          <div class="stat">
            <span>예상 시간</span>
            <strong id="time">-</strong>
          </div>
        </div>

        <div id="steps" class="steps"></div>
      </div>
    </section>

    <main>
      <section class="map-shell">
        <div id="map"></div>
        <div id="map-message" class="map-message"></div>
      </section>
      <section class="legend">현재 S01~S04, S06, S07을 지원중이며, 추후 업데이트 예정입니다. 문의사항 및 버그신고는 2653037@donga.ac.kr로 부탁드립니다.</section>
    </main>
  </div>

  <script>
    const KAKAO_APP_KEY = __KAKAO_APP_KEY__;
    const appEl = document.querySelector(".app");
    const controlsEl = document.querySelector(".controls");
    const toggleControlsButton = document.querySelector("#toggle-controls");
    const toggleRoutePanelButton = document.querySelector("#toggle-route-panel");
    const startSelect = document.querySelector("#start");
    const endSelect = document.querySelector("#end");
    const startSuggestions = document.querySelector("#start-suggestions");
    const endSuggestions = document.querySelector("#end-suggestions");
    const swapRouteButton = document.querySelector("#swap-route");
    const addWaypointButton = document.querySelector("#add-waypoint");
    const waypointsEl = document.querySelector("#waypoints");
    const searchButton = document.querySelector("#search");
    const distanceEl = document.querySelector("#distance");
    const timeEl = document.querySelector("#time");
    const stepsEl = document.querySelector("#steps");
    const errorEl = document.querySelector("#error");
    const mapEl = document.querySelector("#map");
    const mapMessageEl = document.querySelector("#map-message");
    const modeButtons = [...document.querySelectorAll("[data-weight]")];
    const travelModeButtons = [...document.querySelectorAll("[data-travel-mode]")];
    const avoidStairsInput = document.querySelector("#avoid-stairs");
    const rainyInput = document.querySelector("#rainy");
    const preferElevatorInput = document.querySelector("#prefer-elevator");
    let places = [];
    let mapPlaces = [];
    let roads = [];
    let selectedWeight = "distance";
    let selectedTravelMode = "car";
    let swapCount = 0;
    let controlsToggleCount = 0;
    let routePanelToggleCount = 0;
    const easterEggSounds = Array.from("스왑버튼을대체몇번을누르는거야으아악아악아악아악");
    let currentRoute = null;
    let map = null;
    let markers = [];
    let routeLines = [];
    let routeLabels = [];
    let activeInfoWindow = null;
    let currentPosition = null;

    function formatDuration(seconds) {
      const value = Number(seconds);
      if (!Number.isFinite(value)) return "-";
      if (value < 60) return `${Math.max(1, Math.round(value))}\uCD08`;
      return `${Math.ceil(value / 60)}\uBD84`;
    }
    const currentLocationOption = {
      id: "CURRENT_LOCATION",
      name: "현위치",
      aliases: ["현위치", "현재위치", "내위치", "CURRENT", "CURRENT_LOCATION"],
    };

    function hasPoint(place) {
      return typeof place.latitude === "number" && typeof place.longitude === "number";
    }

    function optionText(place) {
      return `${place.name} (${place.id})`;
    }

    function normalizePlaceCode(value) {
      const text = value.trim();
      if (["현위치", "현재위치", "내위치"].includes(text)) {
        return "CURRENT_LOCATION";
      }
      return text.toUpperCase().split(/\\s+/)[0] || "";
    }

    function renderSuggestions(input, container) {
      const matches = [currentLocationOption, ...places];
      container.innerHTML = matches.map(place => `
        <button type="button" class="suggestion" data-place-id="${place.id}" data-place-label="${place.name}">
          <strong>${place.id}</strong>
          <span>${place.name}</span>
        </button>
      `).join("");
      container.classList.toggle("show", matches.length > 0);

      container.querySelectorAll(".suggestion").forEach(button => {
        button.addEventListener("mousedown", event => event.preventDefault());
        button.addEventListener("click", () => {
          input.value = button.dataset.placeId === "CURRENT_LOCATION"
            ? button.dataset.placeLabel
            : button.dataset.placeId;
          container.classList.remove("show");
        });
      });
    }

    function setupSearchInput(input, container) {
      input.addEventListener("focus", () => renderSuggestions(input, container));
      input.addEventListener("input", () => renderSuggestions(input, container));
      input.addEventListener("keydown", event => {
        if (event.key === "Escape") {
          container.classList.remove("show");
        }
      });
      input.addEventListener("blur", () => {
        setTimeout(() => container.classList.remove("show"), 120);
      });
    }

    function createWaypointInput() {
      const waypointNumber = waypointsEl.querySelectorAll(".waypoint-row").length + 1;
      const row = document.createElement("div");
      row.className = "waypoint-row";
      row.innerHTML = `
        <div class="search-field">
          <input class="waypoint-input" autocomplete="off" placeholder="경유지 검색" />
          <div class="suggestions"></div>
        </div>
        <button type="button" class="remove-waypoint" aria-label="경유지 삭제" title="경유지 삭제">×</button>
      `;
      const input = row.querySelector(".waypoint-input");
      const suggestions = row.querySelector(".suggestions");
      const removeButton = row.querySelector(".remove-waypoint");
      setupSearchInput(input, suggestions);
      removeButton.addEventListener("click", () => row.remove());
      waypointsEl.appendChild(row);
      if (waypointNumber >= 4) {
        input.value = "대체 얼마나 더 경유를 하실려고요?";
      }
      input.focus();
      if (waypointNumber >= 4) {
        input.select();
      }
    }

    function getWaypointCodes() {
      return [...waypointsEl.querySelectorAll(".waypoint-input")]
        .map(input => normalizePlaceCode(input.value))
        .filter(Boolean);
    }

    function requestCurrentLocation() {
      if (!navigator.geolocation) {
        return;
      }

      navigator.geolocation.getCurrentPosition(
        position => {
          currentPosition = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          };
          if (!startSelect.value.trim()) {
            startSelect.value = "현위치";
          }
        },
        () => {},
        { enableHighAccuracy: true, timeout: 8000, maximumAge: 30000 }
      );
    }

    function swapRouteInputs() {
      const startValue = startSelect.value;
      startSelect.value = endSelect.value;
      endSelect.value = startValue;
      startSuggestions.classList.remove("show");
      endSuggestions.classList.remove("show");

      swapCount += 1;
      if (swapCount === 10) {
        easterEggSounds.forEach(sound => window.alert(sound));
        swapCount = 0;
      }
    }

    async function loadData() {
      [places, mapPlaces, roads] = await Promise.all([
        fetch("/api/places").then(response => response.json()),
        fetch("/api/map-places").then(response => response.json()),
        fetch("/api/roads").then(response => response.json()),
      ]);

      setupSearchInput(startSelect, startSuggestions);
      setupSearchInput(endSelect, endSuggestions);
      requestCurrentLocation();

      await loadKakaoMap();
      if (window.kakao?.maps) {
        initMap();
        drawMap();
      }
    }

    function latLng(place) {
      return new kakao.maps.LatLng(place.latitude, place.longitude);
    }

    function showMapMessage(title, body) {
      mapMessageEl.innerHTML = `<strong>${title}</strong><span>${body}</span>`;
      mapMessageEl.classList.add("show");
    }

    function hideMapMessage() {
      mapMessageEl.classList.remove("show");
      mapMessageEl.innerHTML = "";
    }

    function loadKakaoMap() {
      if (window.kakao?.maps) {
        return Promise.resolve();
      }

      if (!KAKAO_APP_KEY) {
        showMapMessage(
          "카카오 지도 API 키가 필요합니다.",
          "KAKAO_MAP_API_KEY 환경변수에 카카오 JavaScript 키를 넣고 서버를 다시 실행하세요."
        );
        return Promise.resolve();
      }

      return new Promise(resolve => {
        const script = document.createElement("script");
        script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${encodeURIComponent(KAKAO_APP_KEY)}&autoload=false`;
        script.onload = () => kakao.maps.load(resolve);
        script.onerror = () => {
          showMapMessage(
            "카카오 지도를 불러오지 못했습니다.",
            `카카오 개발자 콘솔의 Web 플랫폼에 현재 주소(${location.origin})를 등록했는지 확인하세요. localhost와 127.0.0.1은 서로 다르게 처리됩니다.`
          );
          resolve();
        };
        document.head.appendChild(script);
      });
    }

    function fitMapTo(points, level = 4) {
      if (!points.length) {
        map.setCenter(new kakao.maps.LatLng(35.116, 128.968));
        map.setLevel(level);
        return;
      }

      const bounds = new kakao.maps.LatLngBounds();
      points.forEach(place => bounds.extend(latLng(place)));
      map.setBounds(bounds, 48, 48, 48, 48);
    }

    function initMap() {
      if (map) return;
      const points = mapPlaces.filter(hasPoint);
      hideMapMessage();
      map = new kakao.maps.Map(mapEl, {
        center: new kakao.maps.LatLng(35.116, 128.968),
        level: 4,
      });
      map.addControl(new kakao.maps.MapTypeControl(), kakao.maps.ControlPosition.TOPRIGHT);
      map.addControl(new kakao.maps.ZoomControl(), kakao.maps.ControlPosition.RIGHT);
      kakao.maps.event.addListener(map, "click", () => {
        if (activeInfoWindow) {
          activeInfoWindow.close();
          activeInfoWindow = null;
        }
      });
      fitMapTo(points);
      setTimeout(() => {
        map.relayout();
        drawMap();
      }, 0);
    }

    function clearMapItems() {
      if (activeInfoWindow) {
        activeInfoWindow.close();
        activeInfoWindow = null;
      }
      markers.forEach(marker => marker.setMap(null));
      routeLabels.forEach(label => label.setMap(null));
      routeLines.forEach(line => line.setMap(null));
      markers = [];
      routeLabels = [];
      routeLines = [];
    }

    function drawMap() {
      if (!map) return;
      const placeMap = new Map(mapPlaces.map(place => [place.id, place]));
      const routeIds = new Set((currentRoute?.path || []).map(place => place.id));
      const routePoints = (currentRoute?.path || []).filter(hasPoint);
      clearMapItems();

      const routeSteps = currentRoute?.steps || [];
      routeSteps.forEach(step => {
        if (!hasPoint(step.from) || !hasPoint(step.to)) return;
        const mode = step.travel_mode || (step.road_type === "차량" ? "car" : "walk");
        routeLines.push(new kakao.maps.Polyline({
          map,
          path: [latLng(step.from), latLng(step.to)],
          strokeWeight: 7,
          strokeColor: mode === "car" ? "#2563eb" : "#16a34a",
          strokeOpacity: 0.95,
          strokeStyle: "solid",
        }));
      });

      if (!routeSteps.length && routePoints.length > 1) {
        routeLines.push(new kakao.maps.Polyline({
          map,
          path: routePoints.map(latLng),
          strokeWeight: 7,
          strokeColor: "#16a34a",
          strokeOpacity: 0.95,
          strokeStyle: "solid",
        }));
      }

      const routePointCounts = new Map();
      routePoints.forEach(place => {
        const key = `${place.latitude},${place.longitude}`;
        routePointCounts.set(key, (routePointCounts.get(key) || 0) + 1);
      });

      const routePointSeen = new Map();
      routePoints.forEach((place, index) => {
        const key = `${place.latitude},${place.longitude}`;
        const count = routePointCounts.get(key) || 1;
        const seen = routePointSeen.get(key) || 0;
        const offset = count > 1 ? (seen - (count - 1) / 2) * 30 : 0;
        routePointSeen.set(key, seen + 1);
        const relatedStep = routeSteps[Math.min(index, routeSteps.length - 1)];
        const pointMode = relatedStep?.travel_mode
          || (relatedStep?.road_type === "차량" ? "car" : "walk");
        const isElevator = place.id.startsWith("EL");
        const pointColor = pointMode === "car" ? "#2563eb" : "#16a34a";
        const featureIcon = isElevator ? "↕" : "";
        const featureTitle = isElevator ? "엘리베이터" : "";
        const featureColor = "#7c3aed";
        const featureBadge = featureIcon
          ? `<span title="${featureTitle}" aria-label="${featureTitle}" style="position:absolute;top:-9px;right:-9px;width:16px;height:16px;border:2px solid ${featureColor};border-radius:50%;background:#fff;color:${featureColor};display:grid;place-items:center;font-size:10px;font-weight:900;line-height:1;box-shadow:0 2px 5px rgba(0,0,0,.2);">${featureIcon}</span>`
          : "";

        const label = new kakao.maps.CustomOverlay({
          map,
          position: latLng(place),
          xAnchor: 0.5,
          yAnchor: 0.5,
          content: `<div style="position:relative;transform:translateX(${offset}px);width:26px;height:26px;border-radius:999px;background:${pointColor};color:#fff;display:grid;place-items:center;box-shadow:0 3px 10px rgba(0,0,0,.22);font-size:13px;font-weight:700;border:2px solid #fff;">${index + 1}${featureBadge}</div>`,
        });
        routeLabels.push(label);
      });

      const visiblePlaceMap = new Map();
      if (!currentRoute?.path) {
        for (const place of places.filter(hasPoint)) {
          visiblePlaceMap.set(place.id, place);
        }
      }

      for (const place of [...visiblePlaceMap.values()]) {
        const marker = new kakao.maps.Marker({
          map,
          position: latLng(place),
          title: optionText(place),
        });
        markers.push(marker);

        const infoWindow = new kakao.maps.InfoWindow({
          content: `<div style="padding:8px 10px;font-size:13px;line-height:1.45;"><strong>${place.name}</strong><br>${place.id}</div>`,
        });
        kakao.maps.event.addListener(marker, "click", () => {
          if (activeInfoWindow === infoWindow) {
            infoWindow.close();
            activeInfoWindow = null;
            return;
          }
          if (activeInfoWindow) {
            activeInfoWindow.close();
          }
          infoWindow.open(map, marker);
          activeInfoWindow = infoWindow;
        });

      }

      const focusPoints = routePoints.length > 1 ? routePoints : places.filter(hasPoint);
      if (focusPoints.length) {
        fitMapTo(focusPoints);
      }
    }

    async function searchRoute() {
      const start = normalizePlaceCode(startSelect.value);
      const end = normalizePlaceCode(endSelect.value);
      const waypoints = getWaypointCodes();
      startSelect.value = start === "CURRENT_LOCATION" ? "현위치" : start;
      endSelect.value = end === "CURRENT_LOCATION" ? "현위치" : end;
      startSuggestions.classList.remove("show");
      endSuggestions.classList.remove("show");

      if (!start || !end) {
        currentRoute = null;
        errorEl.hidden = false;
        errorEl.textContent = "출발지와 도착지를 모두 입력하세요.";
        distanceEl.textContent = "-";
        timeEl.textContent = "-";
        stepsEl.innerHTML = "";
        drawMap();
        return;
      }

      const needsCurrentLocation =
        start === "CURRENT_LOCATION" || end === "CURRENT_LOCATION" || waypoints.includes("CURRENT_LOCATION");
      if (needsCurrentLocation && !currentPosition) {
        currentRoute = null;
        errorEl.hidden = false;
        errorEl.textContent = "현재 위치를 가져오지 못했습니다. 브라우저 위치 권한을 허용한 뒤 다시 시도하세요.";
        distanceEl.textContent = "-";
        timeEl.textContent = "-";
        stepsEl.innerHTML = "";
        drawMap();
        return;
      }

      const params = new URLSearchParams({
        start,
        end,
        weight: selectedWeight,
        travel_mode: selectedTravelMode,
        avoid_stairs: avoidStairsInput.checked ? "1" : "0",
        rainy: rainyInput.checked ? "1" : "0",
        prefer_elevator: preferElevatorInput.checked ? "1" : "0",
      });
      if (waypoints.length) {
        params.set("waypoints", waypoints.join(","));
      }
      if (needsCurrentLocation) {
        params.set("current_lat", currentPosition.latitude);
        params.set("current_lng", currentPosition.longitude);
      }
      const url = `/api/route?${params.toString()}`;
      const result = await fetch(url).then(response => response.json());
      currentRoute = result.ok ? result : null;
      errorEl.hidden = result.ok;
      errorEl.textContent = result.ok ? "" : result.message;

      distanceEl.textContent = result.ok ? `${result.total_distance}m` : "-";
      timeEl.textContent = result.ok ? formatDuration(result.total_time) : "-";
      const waypointHtml = result.ok && result.waypoints?.length ? `
        <div class="step">
          <div class="badge">경</div>
          <div>
            <strong>경유지</strong>
            <span>${result.waypoints.map(place => `${place.name} (${place.id})`).join(" → ")}</span>
          </div>
        </div>
      ` : "";
      const routeStepsHtml = result.ok && result.steps.length === 0 ? `
        <div class="step">
          <div class="badge">0</div>
          <div>
            <strong>출발지와 도착지가 같습니다.</strong>
            <span>이동 경로가 없습니다.</span>
          </div>
        </div>
      ` : result.ok ? result.steps.map((step, index) => `
        <div class="step">
          <div class="badge">${index + 1}</div>
          <div>
            <strong>${step.from.name} → ${step.to.name}</strong>
            <span>${step.road_type || "경로"}</span>
            <div class="step-meta">
              <span class="chip">거리 ${step.distance ?? "-"}m</span>
              <span class="chip">시간 ${formatDuration(step.time)}</span>
              <span class="chip ${step.elevator || step.stair ? "on" : ""}">${step.elevator ? "엘리베이터" : step.stair ? "계단 있음" : "계단 없음"}</span>
              <span class="chip ${step.indoor ? "on" : ""}">${step.indoor ? "실내" : "실외"}</span>
            </div>
          </div>
        </div>
      `).join("") : "";
      stepsEl.innerHTML = result.ok ? routeStepsHtml : "";
      if (result.ok) {
        stepsEl.insertAdjacentHTML("afterbegin", `
          <div class="step endpoint start">
            <div class="badge">출</div>
            <div>
              <strong>출발지</strong>
              <span>${result.start.name} (${result.start.id})</span>
            </div>
          </div>
        `);
        stepsEl.insertAdjacentHTML("beforeend", `
          <div class="step endpoint end">
            <div class="badge">도</div>
            <div>
              <strong>도착지</strong>
              <span>${result.end.name} (${result.end.id})</span>
            </div>
          </div>
        `);
      }
      if (result.ok && result.waypoints?.length && result.steps.length > 0) {
        result.waypoints
          .slice()
          .sort((left, right) => right.after_step_index - left.after_step_index)
          .forEach(place => {
            const stepItems = [...stepsEl.querySelectorAll(".step:not(.waypoint):not(.endpoint)")];
            const target = stepItems[place.after_step_index - 1];
            if (!target) return;

            const waypointEl = document.createElement("div");
            waypointEl.className = "step waypoint";
            waypointEl.innerHTML = `
              <div class="badge">경</div>
              <div>
                <strong>경유지 도착</strong>
                <span>${place.name} (${place.id})</span>
              </div>
            `;
            target.insertAdjacentElement("afterend", waypointEl);
          });
      }

      drawMap();
      if (result.ok) {
        stepsEl.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }

    modeButtons.forEach(button => {
      button.addEventListener("click", () => {
        selectedWeight = button.dataset.weight;
        modeButtons.forEach(item => item.classList.toggle("active", item === button));
      });
    });

    travelModeButtons.forEach(button => {
      button.addEventListener("click", () => {
        selectedTravelMode = button.dataset.travelMode;
        travelModeButtons.forEach(item => item.classList.toggle("active", item === button));
      });
    });

    function relayoutMapSoon() {
      setTimeout(() => {
        if (map) {
          map.relayout();
          drawMap();
        }
      }, 200);
    }

    toggleControlsButton.addEventListener("click", () => {
      const collapsed = controlsEl.classList.toggle("collapsed");
      toggleControlsButton.textContent = collapsed ? "▼" : "▲";
      toggleControlsButton.setAttribute("aria-expanded", String(!collapsed));
      controlsToggleCount += 1;
      if (controlsToggleCount === 10) {
        toggleControlsButton.classList.add("rainbow-easter-egg");
      }
    });

    toggleRoutePanelButton.addEventListener("click", () => {
      const collapsed = appEl.classList.toggle("route-collapsed");
      toggleRoutePanelButton.setAttribute("aria-expanded", String(!collapsed));
      routePanelToggleCount += 1;
      if (routePanelToggleCount === 10) {
        toggleRoutePanelButton.classList.add("rainbow-easter-egg");
      }
      relayoutMapSoon();
    });

    swapRouteButton.addEventListener("click", swapRouteInputs);
    addWaypointButton.addEventListener("click", createWaypointInput);
    searchButton.addEventListener("click", searchRoute);
    window.addEventListener("resize", () => {
      if (map) {
        map.relayout();
        drawMap();
      }
    });
    loadData();
  </script>
</body>
</html>
"""


def render_index_html() -> str:
    return INDEX_HTML.replace("__KAKAO_APP_KEY__", json.dumps(KAKAO_MAP_API_KEY))


class NavigationServer(ThreadingHTTPServer):
    allow_reuse_address = os.name != "nt"
    daemon_threads = True


def stop_server_when_parent_exits(server: NavigationServer) -> None:
    if os.name != "nt":
        return

    import ctypes
    import threading

    parent_pid = os.getppid()

    def monitor_parent() -> None:
        synchronize = 0x00100000
        infinite = 0xFFFFFFFF
        wait_object_0 = 0
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(synchronize, False, parent_pid)
        if not handle:
            return
        try:
            if kernel32.WaitForSingleObject(handle, infinite) == wait_object_0:
                server.shutdown()
        finally:
            kernel32.CloseHandle(handle)

    threading.Thread(target=monitor_parent, name="nav-parent-monitor", daemon=True).start()


class NavigationHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/" and is_refresh_limited(self.client_address[0]):
            self.send_rate_limit(
                REFRESH_LIMIT_WINDOW_SECONDS,
                "새로고침 요청이 너무 많습니다. 10초 후 다시 시도하세요.",
            )
            return

        if is_rate_limited(self.client_address[0]):
            self.send_rate_limit(RATE_LIMIT_WINDOW_SECONDS, "요청이 너무 많습니다.")
            return

        if parsed.path == "/":
            self.send_text(render_index_html(), "text/html; charset=utf-8")
            return

        if parsed.path == "/api/places":
            self.send_json(api_places())
            return

        if parsed.path == "/api/map-places":
            self.send_json(api_map_places())
            return

        if parsed.path == "/api/roads":
            self.send_json([road.__dict__ for road in ROADS])
            return

        if parsed.path == "/api/route":
            query = parse_qs(parsed.query)
            start = query.get("start", [""])[0]
            end = query.get("end", [""])[0]
            weight = query.get("weight", ["distance"])[0]
            travel_mode = query.get("travel_mode", ["car"])[0]
            avoid_stairs = parse_bool(query.get("avoid_stairs", ["0"])[0])
            rainy = parse_bool(query.get("rainy", ["0"])[0])
            prefer_elevator = parse_bool(query.get("prefer_elevator", ["0"])[0])
            waypoints = [
                item
                for item in query.get("waypoints", [""])[0].split(",")
                if item.strip()
            ]
            current_lat = parse_float(query.get("current_lat", [""])[0])
            current_lng = parse_float(query.get("current_lng", [""])[0])
            if weight not in {"distance", "time"}:
                weight = "distance"
            self.send_json(
                find_route(
                    start,
                    end,
                    weight,
                    travel_mode,
                    avoid_stairs,
                    rainy,
                    prefer_elevator,
                    waypoints,
                    current_lat,
                    current_lng,
                )
            )
            return

        self.send_error(404)

    def send_text(self, body: str, content_type: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def send_json(self, data) -> None:
        self.send_text(json.dumps(data, ensure_ascii=False), "application/json; charset=utf-8")

    def send_rate_limit(self, retry_after: int, message: str) -> None:
        encoded = message.encode("utf-8")
        self.send_response(429)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Retry-After", str(retry_after))
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args) -> None:
        print(f"[nav] {self.address_string()} - {format % args}")


def main() -> None:
    server = NavigationServer((HOST, PORT), NavigationHandler)
    stop_server_when_parent_exits(server)
    print(f"교내 길찾기 서버 실행 중: http://{HOST}:{PORT}")
    print("종료하려면 Ctrl+C를 누르세요.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n교내 길찾기 서버를 종료합니다.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
