import csv
import networkx as nx
from itertools import combinations

# =========================
# 1. 读取清洗后的文本
# =========================
with open("清洗_智能交通文献摘要.txt", "r", encoding="utf-8") as f:
    text = f.read()

# =========================
# 2. 转换为词列表
# =========================
tokens = text.split()

print(f"词数量：{len(tokens)}")

# =========================
# 3. 构建共现网络函数
# =========================
def build_cooccurrence_network(tokens, window_size=5):

    G = nx.Graph()

    for i, word in enumerate(tokens):

        # 取窗口（前后window_size）
        window = tokens[max(0, i - window_size): i] + \
                 tokens[i + 1: i + window_size + 1]

        # 两两组合
        for pair in combinations(window, 2):

            if G.has_edge(*pair):
                G[pair[0]][pair[1]]["weight"] += 1
            else:
                G.add_edge(pair[0], pair[1], weight=1)

    return G

# =========================
# 4. 生成网络
# =========================
G = build_cooccurrence_network(tokens, window_size=5)

print(f"节点数: {G.number_of_nodes()}")
print(f"边数: {G.number_of_edges()}")

# =========================
# 5. 导出 nodes.csv
# =========================
with open("nodes.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Id", "Label"])

    for node in G.nodes():
        writer.writerow([node, node])

# =========================
# 6. 导出 edges.csv
# =========================
with open("edges.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Source", "Target", "Weight"])

    for u, v, data in G.edges(data=True):
        writer.writerow([u, v, data["weight"]])

print("Gephi文件已生成：nodes.csv + edges.csv")