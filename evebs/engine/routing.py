"""BFS routing engine for finding reachable Eve systems within a jump count."""
import json
import os
from collections import deque

_GRAPH_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'universe_graph.json')

with open(_GRAPH_PATH) as _f:
    GRAPH = json.load(_f)


def find_systems_within_jumps(
    origin,
    max_jumps,
    avoid_lowsec=False,
    avoid_nullsec=False,
    graph=GRAPH
):
    """Return all systems reachable from origin within max_jumps gate jumps.

    Args:
        origin: Name of the starting system.
        max_jumps: Maximum number of jumps to traverse.
        avoid_lowsec: Skip lowsec systems (0.0 < security < 0.5).
        avoid_nullsec: Skip nullsec systems (security <= 0.0).
        graph: Adjacency list dict; defaults to the module-level GRAPH.

    Returns:
        Dict mapping system name to {'jumps': int, 'security': float}.
    """
    def is_allowed(system):
        """True if the system passes the security filter."""
        sec = graph[system]["security"]
        if avoid_lowsec and 0.0 < sec < 0.5:
            return False
        if avoid_nullsec and sec <= 0.0:
            return False
        return True

    visited = {origin: 0}
    queue = deque([(origin, 0)])
    result = {}

    while queue:
        system, jumps = queue.popleft()

        if jumps > max_jumps:
            continue

        result[system] = {
            "jumps": jumps,
            "security": graph[system]["security"]
        }

        for neighbor in graph[system]["neighbors"]:
            if neighbor not in visited and is_allowed(neighbor):
                visited[neighbor] = jumps + 1
                queue.append((neighbor, jumps + 1))

    return result
