import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.spatial import distance
from shapely.geometry import Point
from shapely.ops import unary_union
import tkinter as tk
from tkinter import ttk

# Константы
S = 40000  # Площадь области
SIDE = np.sqrt(S)  # Сторона квадрата
EXPERIMENTS = 1000  # Количество экспериментов

class Node:
    def __init__(self, mu, sigma):
      # Среднее значение и стандартное отклонение
        self.r = max(0, np.random.normal(mu, sigma))  # Убедимся, что радиус не отрицательный
        self.x, self.y = self._generate_valid_coordinates()

    def _generate_valid_coordinates(self):
        while True:
            x = np.random.uniform(-np.sqrt(2) * SIDE / 2, np.sqrt(2) * SIDE / 2)
            y = np.random.uniform(-np.sqrt(2) * SIDE / 2, np.sqrt(2) * SIDE / 2)
            if abs(x) + abs(y) < np.sqrt(2) * SIDE / 2:
                return x, y

def generate_nodes(n, r, s):
    """Генерация координат узлов в квадрате."""
    return [Node(r,s) for _ in range(n)]

def build_graph(nodes):
    """Построение графа на основе расстояний между узлами и радиуса r."""
    G = nx.DiGraph()

    for num, node in enumerate(nodes):
        G.add_node(num, pos=(node.x,node.y))

    positions = np.array([[node.x, node.y] for node in nodes])
    distances = distance.cdist(positions, positions)

    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if i == j:
                continue
            if distances[i, j] < nodes[i].r:
                G.add_edge(i, j)

    return G

def analyze_graph(G, nodes):
    """Анализ графа: количество слабосвязанных компонент и процент покрытия."""
    components = list(nx.weakly_connected_components(G))
    num_components = len(components)

    # Процент покрытия площади S
    circles = [Point(node.x, node.y).buffer(node.r) for node in nodes]
    union = unary_union(circles)
    covered_area = union.area

    percent_coverage = min(covered_area / S, 1.0) * 100

    return num_components, percent_coverage

def experiment(n, r, s):
    """Проведение одного эксперимента."""
    nodes = generate_nodes(n, r, s)
    G = build_graph(nodes)
    return analyze_graph(G, nodes)

def run_experiments():
    nodes_start = int(entry_nodes_start.get())
    nodes_end = int(entry_nodes_end.get())
    nodes_step = int(entry_nodes_step.get())

    radius_start = int(entry_radius_start.get())
    radius_end = int(entry_radius_end.get())
    radius_step = int(entry_radius_step.get())

    sigma = int(entry_sigma.get())



    RADIUS = range(radius_start, radius_end + 1, radius_step)
    NODES = range(nodes_start, nodes_end + 1, nodes_step)

    results = []
    for n in NODES:
        for r in RADIUS:
            components_list = []
            coverage_list = []
            for _ in range(EXPERIMENTS):
                num_components, percent_coverage = experiment(n, r, sigma)
                components_list.append(num_components)
                coverage_list.append(percent_coverage)
            avg_components = np.mean(components_list)
            avg_coverage = np.mean(coverage_list)
            results.append((n, r, avg_components, avg_coverage))

    plot_results(results, NODES, RADIUS)
    return results

def plot_results(results, NODES, RADIUS):
    """Визуализация результатов на одном графике."""
    plt.figure(figsize=(14, 6))

    plt.subplot(1, 2, 1)
    for n in NODES:
        components = [res[2] for res in results if res[0] == n]
        plt.plot(RADIUS, components, label=f'n={n}')
    plt.title('Среднее количество слабосвязанных компонент')
    plt.xlabel('Радиус (r)')
    plt.ylabel('Количество компонент')
    plt.legend()

    plt.subplot(1, 2, 2)
    for n in NODES:
        coverage = [res[3] for res in results if res[0] == n]
        plt.plot(RADIUS, coverage, label=f'n={n}')
    plt.title('Процент покрытия')
    plt.xlabel('Радиус (r)')
    plt.ylabel('Процент покрытия')
    plt.legend()

    plt.tight_layout()
    plt.show()

# Интерфейс пользователя
root = tk.Tk()
root.title("Моделирование беспроводной сети")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

ttk.Label(frame, text="Количество узлов:").grid(column=1, row=1, sticky=tk.W)

ttk.Label(frame, text="Н").grid(column=2, row=1, sticky=tk.W)
entry_nodes_start = ttk.Entry(frame)
entry_nodes_start.insert(0, '10')
entry_nodes_start.grid(column=3, row=1, sticky=(tk.W, tk.E))

ttk.Label(frame, text="К").grid(column=4, row=1, sticky=tk.W)
entry_nodes_end = ttk.Entry(frame)
entry_nodes_end.insert(0, '100')
entry_nodes_end.grid(column=5, row=1, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Ш").grid(column=6, row=1, sticky=tk.W)
entry_nodes_step = ttk.Entry(frame)
entry_nodes_step.insert(0, '10')
entry_nodes_step.grid(column=7, row=1, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Радиус mu:").grid(column=1, row=2, sticky=tk.W)

ttk.Label(frame, text="Н").grid(column=2, row=2, sticky=tk.W)
entry_radius_start = ttk.Entry(frame)
entry_radius_start.insert(0, '0')
entry_radius_start.grid(column=3, row=2, sticky=(tk.W, tk.E))

ttk.Label(frame, text="К").grid(column=4, row=2, sticky=tk.W)
entry_radius_end = ttk.Entry(frame)
entry_radius_end.insert(0, '100')
entry_radius_end.grid(column=5, row=2, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Ш").grid(column=6, row=2, sticky=tk.W)
entry_radius_step = ttk.Entry(frame)
entry_radius_step.insert(0, '10')
entry_radius_step.grid(column=7, row=2, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Радиус sigma:").grid(column=1, row=3, sticky=tk.W)
entry_sigma = ttk.Entry(frame)
entry_sigma.insert(0, '5')
entry_sigma.grid(column=2, row=3, sticky=(tk.W, tk.E))




ttk.Button(frame, text="Запустить симуляцию", command=run_experiments).grid(column=2, row=5, sticky=tk.E)

root.mainloop()
