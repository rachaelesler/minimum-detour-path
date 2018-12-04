"""
ID 27799964
"""
# GLOBAL VARIABLES
INF = float('inf')


def createGraph(filename):
    """
    Creates a graph using information from the given file. Returns the graph as an adjacency list.
    """
    file = open(filename)
    n = int(file.readline())
    adjList = [None] * (n + 1)
    for line in file:
        data = line.split()
        id1 = int(data[0])
        id2 = int(data[1])
        length = int(data[2])
        if adjList[id1] is None:
            adjList[id1] = [[id2, length]]
        else:
            adjList[id1].append([id2, length])
        if adjList[id2] is None:
            adjList[id2] = [[id1, length]]
        else:
            adjList[id2].append([id1, length])
    return adjList


def createDetourGraph(edge_file, customer_file):
    """
    Creates a graph with two sets of vertices. The two sets are connected only via the customers.
    """
    # Generate list of customers
    customer_file = open(customer_file)
    customers = []
    for line in customer_file:
        line = line.strip()
        customers.append(int(line))
    # Generate adjacency list
    file = open(edge_file)
    n = int(file.readline())
    adjList = [None] * 2 * (n + 1)
    offset = n + 1
    for line in file:
        data = line.split()
        id1 = int(data[0])
        id2 = int(data[1])
        length = int(data[2])
        # Execute this block if id1 is not in the adjacency list
        if adjList[id1] is None:
            adjList[id1] = [[id2, length]]
            adjList[id1 + offset] = [[id2 + offset, length]]
            if id1 in customers:
                adjList[id1].append([id1+offset, 0])
                adjList[id1+offset].append([id1, 0])
        # Execute this block if id1 IS already in list
        else:
            adjList[id1].append([id2, length])
            adjList[id1 + offset].append([id2 + offset, length])
        # Execute this block if id2 is not yet in the adjacency list
        if adjList[id2] is None:
            adjList[id2] = [[id1, length]]
            adjList[id2 + offset] = [[id1 + offset, length]]
            if id2 in customers:
                adjList[id2].append([id2+offset, 0])
                adjList[id2 + offset].append([id2, 0])
        # Execute if id2 already in list
        else:
            adjList[id2].append([id1, length])
            adjList[id2 + offset].append([id1 + offset, length])
    return adjList


# CLASSES
class MinHeap:
    """
    Implements a min-heap class, used for optimising Dijksta's algorithm. Contains, as attributes, a min-heap, and a
    vertices list that keeps track of the status of each vertex.
    """

    def __init__(self, initid, n):
        # Elements at index 0 at each entry of heap; lengths at 1
        self.heap = [[initid, 0]]
        self.count = n
        self.vertices = []
        for i in range(n + 1):
            self.vertices.append([-2, None, INF])
        self.vertices[initid][0] = 0  # Keep track of location of vertices in the min heap
        self.vertices[initid][1] = 'S'  # Indicates that this vertex was the start vertex
        self.vertices[initid][2] = 0
        self.complete = False

    def popMin(self):
        """
        Returns the top element of the heap, i.e. the minimum value
        """
        # print("Popping the min value of the heap")
        output = self.heap[0]
        self.removeRoot()
        return output

    def updateNode(self, vertexid, distance, origin):
        """
        Updates the corresponding node in the min-heap
        """
        new_node_index = self.vertices[vertexid][0]
        self.vertices[vertexid][1] = origin
        self.vertices[vertexid][2] = distance
        # Only execute this if the node to be updated is a child node in heap
        if int(new_node_index) > 0 and new_node_index < len(self.heap):
            # Parent attributes
            parent_index = (new_node_index - 1) // 2
            parent_dist = self.heap[parent_index][1]
            parent_id = self.heap[parent_index][0]

            # Upheap
            while distance > parent_dist and new_node_index != -1:
                # Swap vertices in heap
                temp = [vertexid, distance]
                self.heap[new_node_index] = self.heap[parent_index]
                self.heap[parent_index] = temp
                # Update entries in vertices array
                self.vertices[parent_id][0] = new_node_index
                self.vertices[vertexid][0] = parent_index
                # Update attributes of vertices
                new_node_index = parent_index
                parent_index = (new_node_index - 1) // 2
                parent_dist = self.heap[parent_index][1]
                parent_id = self.heap[parent_index][0]
        return new_node_index

    def addNode(self, vertexid, distance, origin):
        """
        Adds a node to the min-heap with corresponding vertexid and distance.
        """
        # Keep track of new node attributes
        new_node_index = len(self.heap)
        self.heap.append([vertexid, distance])
        self.vertices[vertexid][0] = new_node_index
        self.vertices[vertexid][1] = origin
        self.vertices[vertexid][2] = distance
        # Parent attributes
        parent_index = (new_node_index - 1) // 2
        parent_dist = self.heap[parent_index][1]
        parent_id = self.heap[parent_index][0]
        # Upheap
        while distance > parent_dist:
            # Swap vertices in heap
            temp = [vertexid, distance]
            self.heap[new_node_index] = self.heap[parent_index]
            self.heap[parent_index] = temp
            # Update entries in vertices array
            self.vertices[parent_id][0] = new_node_index
            self.vertices[vertexid][0] = parent_index
            # Update attributes of vertices
            new_node_index = parent_index
            parent_index = (new_node_index - 1) // 2
            parent_dist = self.heap[parent_index][1]
            parent_id = self.heap[parent_index][0]
        return new_node_index

    def removeRoot(self):
        """
        Removes the element at the specified index from the heap.
        """
        if len(self.heap) > 1:
            # Swap root with last element
            temp = self.heap[0]
            self.heap[0] = self.heap[-1]
            self.heap[-1] = temp
            # Remove last element
            del self.heap[len(self.heap) - 1]
            # Compare new element with children and swap if required
            self.sink(0)
        elif len(self.heap) == 1:
            del self.heap[0]
        else:
            self.complete = True
            return False

    def sink(self, heapindex):
        """
        Recursively swaps the element at heapindex with one of its children until it is in the correct position.
        """
        current = self.heap[heapindex]
        val = int(current[1])
        try:
            if val > int(self.heap[2 * heapindex + 1][1]):
                temp = self.heap[heapindex]
                self.heap[heapindex] = self.heap[2 * heapindex + 1]
                self.heap[2 * heapindex + 1] = temp
                return self.sink(2 * heapindex + 1)
            elif val > self.heap[2 * heapindex + 2][1]:
                temp = self.heap[heapindex]
                self.heap[heapindex] = self.heap[2 * heapindex + 2]
                self.heap[2 * heapindex + 2] = temp
                return self.sink(2 * heapindex + 2)
            else:
                return
        except IndexError:
            return


# FUNCTIONS
def shortestPath(s, t, adjList):
    """
    Return shortest path (as list) and shortest distance (as int) between any two given vertices s and t
    s and t are integers representing the index of the vertex
    Used for Task 1: Computing shortest path
    """
    if s == t:
        print_solution([s], 0, 1)
        return
    n = len(adjList)
    if t > n:
        return False
    minHeap = MinHeap(s, n)
    it = 0
    # Dijkstra's algorithm
    while minHeap.heap != []:  # While heap is not empty
        it += 1
        source = minHeap.popMin()  # Get vertex v with minimum distance
        source_id = source[0]
        source_edges = adjList[source_id]  # Store all outgoing edges of v
        source_dist = source[1]
        for i in range(len(source_edges)):  # For each outgoing edge u of v
            target_id = source_edges[i][0]
            target_total = minHeap.vertices[target_id][2]
            target_weight = source_edges[i][1]
            # If target vertex is undiscovered
            if target_total == INF:
                minHeap.vertices[target_id][0] = minHeap.addNode(target_id, source_dist + target_weight,
                                                                 source_id)  # add u to the heap
            # Else if target distance needs to be updated
            elif target_total > source_dist + target_weight:
                minHeap.updateNode(vertexid=target_id, distance=source_dist + target_weight, origin=source_id)
        minHeap.vertices[source_id][0] = -1  # Finalise the source vertex
    distance = minHeap.vertices[t][2]
    path = reconstructPath(t, minHeap)
    print_solution(path, distance, 1)


def reconstructPath(targetVertex, heapObject):
    reverse_path = [targetVertex]
    current = heapObject.vertices[targetVertex][1]
    while current != 'S':
        reverse_path.append(current)
        prev = current
        current = heapObject.vertices[prev][1]
    path = []
    for i in range(len(reverse_path)):
        item = reverse_path.pop()
        path.append(item)
    return path


def minDetourPath(s, t, detourList):
    """
    Return shortest path from s to t that passes through at least one customer, and its length
    """
    offset = len(detourList) // 2
    n = len(detourList)  # We want to find the second instance of the target vertex
    detourHeap = MinHeap(s, n)
    it = 0  # to count number of iterations
    # Implement Dijstra's algorithm on detour graph
    while detourHeap.heap != []:  # While heap is not empty
        it += 1
        source = detourHeap.popMin()  # Get vertex, source, with minimum distance
        source_id = source[0]
        source_dist = source[1]
        source_edges = detourList[source_id]  # Store all outgoing edges of source
        if source_edges is not None:
            for i in range(len(source_edges)):  # Iterate through all outgoing edges of current source
                target_id = source_edges[i][0]
                target_total = detourHeap.vertices[target_id][2]  # Current total length of path including this vertex
                target_weight = source_edges[i][1]
                # Check if target vertex is undiscovered
                if target_total == INF:
                    detourHeap.vertices[target_id][0] = detourHeap.addNode(vertexid=target_id,
                                                                     distance=source_dist + target_weight,
                                                                     origin=source_id)
                elif target_total > source_dist + target_weight and detourHeap.vertices[target_id][0] < len(detourHeap.heap):
                    detourHeap.updateNode(vertexid=target_id, distance=source_dist + target_weight, origin=source_id)
        detourHeap.vertices[source_id][0] = -1
    distance = detourHeap.vertices[t + offset][2]
    path = reconstructDetour(targetVertex=(t + offset), heapObject=detourHeap, offset=offset)
    print_solution(path, distance, 2)


def reconstructDetour(targetVertex, heapObject, offset):
    output = [targetVertex - offset]
    current = heapObject.vertices[targetVertex][1]
    while current != 'S':
        if current > offset:
            current -= offset
        output.append(current)
        current = heapObject.vertices[current][1]
    output.reverse()
    return output


###################################################
# DO NOT MODIFY THE LINES IN THE BLOCK BELOW.
# YOU CAN WRITE YOUR CODE ABOVE OR BELOW THIS BLOCK
###################################################
def get_customers(filename):
    file = open(filename)
    customers = []
    for line in file:
        line = line.strip()
        customers.append(int(line))
    return customers


# path is a list of vertices on the path, distance is the total length of the path
# task_id must be 1 or 2 (corresponding to the task for which solution is being printed
def print_solution(path, distance, task_id):
    print()
    if task_id == 1:
        print("Shortest path: ", end="")
    else:
        print("Minimum detour path: ", end="")

    customers = get_customers("customers.txt")

    vertices = []
    for item in path:
        if item in customers:
            vertices.append(str(item) + "(C)")
        else:
            vertices.append(str(item))

    print(" --> ".join(vertices))
    if task_id == 1:
        print("Shortest distance:", distance)
    else:
        print("Minimum detour distance:", distance)


source = int(input("Enter source vertex: "))
target = int(input("Enter target vertex: "))

####################################################
# DO NOT MODIFY THE LINES IN THE ABOVE BLOCK.
# YOU CAN WRITE YOUR CODE ABOVE OR BELOW THIS BLOCK
###################################################


if __name__ == "__main__":
    adjList = createGraph("edges.txt")
    detourList = createDetourGraph("edges.txt", "customers.txt")
    shortestPath(source, target, adjList)
    minDetourPath(source, target, detourList)
