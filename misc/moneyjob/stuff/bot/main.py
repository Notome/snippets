# level 1
graph = {
    "A" : [('B', 1), ('C', 4)], 
    "B" : [('C', 2), ("D", 5)], 
    "C" : [('D', 1)],
    "D" : []
}

# level 2
# A->B 1
# A->B->C 3
# A->B->C->D 4

# level 3
def dijkstra1(graph=graph, start = 'A'):
    distances = {vertex : float('inf') for vertex in graph}
    distances[start] = 0
    visited = []

    while len(visited) < len(graph):
        unvisited = {key : value for key, value in distances.items() if key not in visited}
        current = min(unvisited, key= unvisited.get)
        
        for neighbour, weight in graph[current]:
            if neighbour not in visited:
                new_weight = weight + distances[current]
                distances[neighbour] = min(new_weight, distances[neighbour])
    
        visited.append(current)
    print(distances)
dijkstra1()

import heapq
# level 4
def dijkstra2(graph=graph, start = 'A'):
    distances = {}
    heap = [(0, start)]
    while heap:
        dist, node = heapq.heappop(heap)
        if node in distances: 
            continue
        distances[node] = dist
        
        for neighbour, weight in graph[node]:
            if neighbour not in distances:
                heapq.heappush(heap, (dist + weight, neighbour))
    print(distances)
dijkstra2()

# level 5
def get_path(previous, start, end):
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()
    return path if path[0] == start else None

# level 6
def dijkstra2(graph=graph, start = 'A'):
    distances = {}
    previous = {v:None for v in graph}
    heap = [(0, start)]
    while heap:
        dist, node = heapq.heappop(heap)
        if node in distances: 
            continue
        distances[node] = dist
        
        for neighbour, weight in graph[node]:
            if neighbour not in distances:
                heapq.heappush(heap, (dist + weight, neighbour))
                if previous[neighbour] is None:
                    previous[neighbour] = node
    
    return distances, previous
distances, previous = dijkstra2(graph, 'A')

print(distances)
print(get_path(previous, 'A', 'D'))