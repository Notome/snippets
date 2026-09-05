import heapq
import matplotlib.pyplot as plt
import networkx as nx


graph = {
    'А': [('Б', 258), ('Г', 319), ('В', 148)],
    'Б': [('А', 258), ('Д', 719), ('Г', 125)],
    'В': [('А', 148), ('Д', 348), ('Е', 412)],
    'Г': [('А', 319), ('Б', 125), ('Е', 422)],
    'Д': [('Б', 719), ('В', 348), ('Ж', 198), ('З', 1521)],
    'Е': [('В', 412), ('Г', 422), ('З', 1078)],
    'Ж': [('Д', 198), ('В', 517)],
    'З': [('Д', 1521), ('Е', 1078)]
}


def dijkstra(graph, start='А'):
    distances = {vertex: float('inf') for vertex in graph}
    previous = {vertex: None for vertex in graph}

    distances[start] = 0
    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_vertex = heapq.heappop(priority_queue)

        if current_distance > distances[current_vertex]:
            continue

        for neighbor, weight in graph[current_vertex]:
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_vertex
                heapq.heappush(priority_queue, (distance, neighbor))

    return distances, previous


def get_path(previous, start, end):
    path = []
    current = end

    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()

    if path[0] == start:
        return path
    return []


def visualize_graph(graph, previous, start='А'):
    G = nx.Graph()

    for node in graph:
        for neighbor, weight in graph[node]:
            G.add_edge(node, neighbor, weight=weight)

    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(10, 7))

    nx.draw(
        G, pos,
        with_labels=True,
        node_size=2500,
        font_size=14
    )

    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    shortest_edges = []
    for node in graph:
        if node != start and previous[node]:
            shortest_edges.append((previous[node], node))

    nx.draw_networkx_edges(
        G, pos,
        edgelist=shortest_edges,
        width=3
    )

    plt.title(f"Граф и кратчайшие пути от вершины {start}")
    plt.show()

start_vertex = 'А'
distances, previous = dijkstra(graph, start_vertex)

print("Кратчайшие расстояния:")
for vertex, dist in distances.items():
    print(f"{start_vertex} -> {vertex}: {dist}")

print("\nКратчайшие пути:")
for vertex in graph:
    path = get_path(previous, start_vertex, vertex)
    print(f"{start_vertex} -> {vertex}: {' -> '.join(path)}")

visualize_graph(graph, previous, start_vertex)