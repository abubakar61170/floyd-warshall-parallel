import random
import time
import numpy as np
import threading
import matplotlib.pyplot as plt

INF = 1e9

class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.adjMatrix = [[INF for _ in range(vertices)] for _ in range(vertices)]
        for i in range(vertices):
            self.adjMatrix[i][i] = 0

    def addEdge(self, src, dest, weight):
        self.adjMatrix[src][dest] = weight

    def applyFloydWarshallSimple(self):
        start_time = time.time()
        dist = [row[:] for row in self.adjMatrix]

        for k in range(self.V):
            for i in range(self.V):
                for j in range(self.V):
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

        end_time = time.time()
        return end_time - start_time, dist

    def applyFloydWarshallParallel(self, num_threads):
        start_time = time.time()
        dist = [row[:] for row in self.adjMatrix]

        def floyd_warshall_thread(k):
            for i in range(self.V):
                for j in range(self.V):
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
        
        for k in range(self.V):
            threads = []
            for _ in range(num_threads):
                thread = threading.Thread(target=floyd_warshall_thread, args=(k,))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()

        end_time = time.time()
        return end_time - start_time, dist

def generate_graph(nodes, probability):
    g = Graph(nodes)
    for i in range(nodes):
        for j in range(nodes):
            if i != j and random.random() < probability:
                weight = random.randint(1, 100)
                g.addEdge(i, j, weight)
    return g

def main():
    nodes = 100
    probability = 0.5

    print(f"Graph generated with {nodes} nodes and ~{probability*100}% connection probability.")

    g = generate_graph(nodes, probability)

    time_without_parallel, _ = g.applyFloydWarshallSimple()
    print(f"Non-Parallel Execution Time: {time_without_parallel:.2f} seconds")

    max_threads = threading.active_count() + 4 #suggested max number of threads
    speedups = []
    for num_threads in range(1, max_threads + 1):
        start = time.time()
        time_with_parallel, _ = g.applyFloydWarshallParallel(num_threads)
        end = time.time()
        time_with_parallel = end-start
        speedup = time_without_parallel / time_with_parallel
        speedups.append((num_threads, speedup))
        print(f"Threads: {num_threads} Speedup: {speedup:.2f}")

    thread_counts = [num for num, _ in speedups]
    speedup_values = [speedup for _, speedup in speedups]

    plt.plot(thread_counts, speedup_values, marker="o", linestyle="-", color="b")
    plt.title("Speedup vs Number of Threads")
    plt.xlabel("Number of Threads")
    plt.ylabel("Speedup (Non-Parallel / Parallel)")
    plt.grid(True)
    plt.savefig("speedup_threads.png")
    plt.show()

    print("\nSpeedup Results:")
    for num_threads, speedup in speedups:
        print(f"Threads: {num_threads}, Speedup: {speedup:.2f}")

if __name__ == "__main__":
    main()