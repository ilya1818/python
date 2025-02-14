import matplotlib.pyplot as plt
import networkx as nx

# Создание графа
G = nx.DiGraph()

# Добавление узлов с текстом внутри
G.add_node('A', label='Начало')
G.add_node('B', label='Ввод N и M')
G.add_node('C', label='Инициализация матрицы N*M')
G.add_node('D', label='Ввод элементов матрицы')
G.add_node('E', label='Отображение матрицы')
G.add_node('F', label='Для каждой строки: Подсчёт положительных элементов')
G.add_node('G', label='Проверка: Больше ли текущий счётчик максимального?')
G.add_node('H', label='Обновление максимального значения и номера строки')
G.add_node('I', label='Вывод строки с наибольшим количеством положительных элементов')
G.add_node('J', label='Конец')

# Добавление рёбер (связей между узлами)
G.add_edges_from([
    ('A', 'B'),
    ('B', 'C'),
    ('C', 'D'),
    ('D', 'E'),
    ('E', 'F'),
    ('F', 'G'),
    ('G', 'H'),
    ('G', 'F'),  # Обратная связь "Нет"
    ('H', 'F'),
    ('F', 'I'),
    ('I', 'J')
])

# Позиции узлов
pos = {
    'A': (1, 2), 'B': (1, 1), 'C': (1, 0), 'D': (1, -1), 'E': (1, -2),
    'F': (1, -3), 'G': (-1, -3), 'H': (0, -5), 'I': (1, -6), 'J': (2, -7)
}

# Рисование графа
plt.figure(figsize=(10, 8))
nx.draw(G, pos, with_labels=True, labels=nx.get_node_attributes(G, 'label'),
        node_size=3000, node_color='skyblue', font_size=10, font_weight='bold', arrows=True)

# Отображение графика
plt.title("Блок-схема алгоритма")
plt.show()
