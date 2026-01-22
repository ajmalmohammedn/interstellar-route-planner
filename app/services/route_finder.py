from app.models import Gate
from app.constants import HYPERSPACE_COST_PER_PASSENGER_PER_HU


def find_cheapest_route(origin_id: str, destination_id: str) -> dict | None:
    """
    Find the cheapest route between two gates using Dijkstra's algorithm.
    Returns route info with path, total HU distance, and cost per passenger.
    """
    origin_id = origin_id.upper()
    destination_id = destination_id.upper()

    if origin_id == destination_id:
        return {
            "origin": origin_id,
            "destination": destination_id,
            "path": [origin_id],
            "total_hu": 0,
            "cost_per_passenger_gbp": 0.0,
        }

    # Build adjacency map from database
    gates = { gate.id: gate for gate in Gate.objects.all()}

    if origin_id not in gates:
        raise ValueError(f"Origin gate '{origin_id}' not found")
    if destination_id not in gates:
        raise ValueError(f"Destination gate '{destination_id}' not found")

    graph = {}
    for gate_id, gate in gates.items():
        graph[gate_id] = []
        for conn in gate.connections:
            neighbor_gate_id = conn.get("id")
            distance_hu = int(conn.get("hu", 0))
            graph[gate_id].append((neighbor_gate_id, distance_hu))


    # Using Dijkstra's algorithm
    distances = {gate_id: float("inf") for gate_id in gates}
    distances[origin_id] = 0
    previous = {}
    unvisited = set(gates.keys()) 

    while unvisited:
        current_node = min(unvisited, key=lambda node: distances[node])

        if distances[current_node] == float("inf") or current_node == destination_id:
            break

        unvisited.remove(current_node)

        for neighbor_id, hu in graph.get(current_node, []):
            if neighbor_id  in unvisited:
                new_distance = distances[current_node] + hu
                if new_distance < distances[neighbor_id]:
                    distances[neighbor_id] = new_distance
                    previous[neighbor_id] = current_node

    if distances[destination_id] == float("inf"):   
        return None
    
    path = []
    target_node = destination_id
    while target_node in previous:
        path.append(target_node)
        target_node = previous[target_node]
    path.append(origin_id)
    path.reverse()

    total_hu = distances[destination_id]
    cost_per_passenger = total_hu * HYPERSPACE_COST_PER_PASSENGER_PER_HU * 2

    return {
        "origin": origin_id,
        "destination": destination_id,
        "path": path,
        "total_hu": total_hu,
        "cost_per_passenger_gbp": round(cost_per_passenger, 2),
    }