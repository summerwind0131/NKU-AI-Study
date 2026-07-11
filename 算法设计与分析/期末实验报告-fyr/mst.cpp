#include <algorithm>
#include <functional>
#include <iomanip>
#include <iostream>
#include <queue>
#include <string>
#include <tuple>
#include <vector>
using namespace std;
// Edge stores one undirected weighted edge: u-v with weight w.
struct Edge {
    int u;
    int v;
    int w;
};
// Disjoint Set Union is used by Kruskal to check whether an edge creates a cycle.
class DSU {
public:
    explicit DSU(int n) : parent(n + 1), rank(n + 1, 0) {
        for (int i = 1; i <= n; ++i) {
            parent[i] = i;
        }
    }
    // Find the root of x and compress the path to speed up later searches.
    int find(int x) {
        if (parent[x] != x) {
            parent[x] = find(parent[x]);
        }
        return parent[x];
    }
    // Merge two sets. Return true if the edge can be added to the MST.
    bool unite(int a, int b) {
        int rootA = find(a);
        int rootB = find(b);
        if (rootA == rootB) {
            return false;
        }
        if (rank[rootA] < rank[rootB]) {
            swap(rootA, rootB);
        }
        parent[rootB] = rootA;
        if (rank[rootA] == rank[rootB]) {
            ++rank[rootA];
        }
        return true;
    }
private:
    vector<int> parent;
    vector<int> rank;
};
// Convert vertex number to its name in the problem, such as 1 -> V1.
string vertexName(int x) {
    return "V" + to_string(x);
}
// Print all selected edges and the total weight of the MST.
void printResult(const string &algorithmName, const vector<Edge> &mst, int totalWeight) {
    cout << algorithmName << " result:\n";
    cout << left << setw(12) << "Edge" << "Weight\n";
    cout << "-------------------\n";
    for (const auto &edge : mst) {
        cout << left << setw(12) << (vertexName(edge.u) + "-" + vertexName(edge.v)) << edge.w << '\n';
    }
    cout << "Total weight: " << totalWeight << "\n\n";
}
// Kruskal algorithm:
// 1. Sort all edges by weight.
// 2. Scan edges from small to large.
// 3. Add an edge only when it connects two different components.
// 4. Stop when n - 1 edges have been selected.
pair<vector<Edge>, int> kruskal(int n, vector<Edge> edges) {
    sort(edges.begin(), edges.end(), [](const Edge &a, const Edge &b) {
        if (a.w != b.w) {
            return a.w < b.w;
        }
        if (min(a.u, a.v) != min(b.u, b.v)) {
            return min(a.u, a.v) < min(b.u, b.v);
        }
        return max(a.u, a.v) < max(b.u, b.v);
    });
    DSU dsu(n);
    vector<Edge> mst;
    int totalWeight = 0;
    for (const auto &edge : edges) {
        if (dsu.unite(edge.u, edge.v)) {
            mst.push_back(edge);
            totalWeight += edge.w;
            if (static_cast<int>(mst.size()) == n - 1) {
                break;
            }
        }
    }
    return {mst, totalWeight};
}
// Prim algorithm:
// Start from one vertex, always choose the smallest edge from visited vertices
// to unvisited vertices, and grow the MST step by step.
pair<vector<Edge>, int> prim(int n, const vector<Edge> &edges, int start) {
    vector<vector<pair<int, int>>> graph(n + 1);
    for (const auto &edge : edges) {
        graph[edge.u].push_back({edge.v, edge.w});
        graph[edge.v].push_back({edge.u, edge.w});
    }
    // State means (weight, from, to). The priority queue works as a min-heap.
    using State = tuple<int, int, int>;
    priority_queue<State, vector<State>, greater<State>> pq;
    vector<bool> visited(n + 1, false);
    vector<Edge> mst;
    int totalWeight = 0;
    visited[start] = true;
    for (size_t i = 0; i < graph[start].size(); ++i) {
        int to = graph[start][i].first;
        int weight = graph[start][i].second;
        pq.push(State(weight, start, to));
    }
    while (!pq.empty() && static_cast<int>(mst.size()) < n - 1) {
        State current = pq.top();
        pq.pop();
        int weight = get<0>(current);
        int from = get<1>(current);
        int to = get<2>(current);
        if (visited[to]) {
            continue;
        }
        visited[to] = true;
        mst.push_back(Edge{from, to, weight});
        totalWeight += weight;
        for (size_t i = 0; i < graph[to].size(); ++i) {
            int next = graph[to][i].first;
            int nextWeight = graph[to][i].second;
            if (!visited[next]) {
                pq.push(State(nextWeight, to, next));
            }
        }
    }
    return {mst, totalWeight};
}
int main() {
    const int n = 6;
    // Input all undirected edges from the graph in the assignment picture.
    vector<Edge> edges = {
        {1, 2, 4}, {1, 3, 3}, {1, 4, 1},
        {2, 4, 5}, {2, 5, 7},
        {3, 4, 2}, {3, 6, 3},
        {4, 5, 5}, {4, 6, 4},
        {5, 6, 6}
    };
    pair<vector<Edge>, int> kruskalResult = kruskal(n, edges);
    vector<Edge> kruskalMst = kruskalResult.first;
    int kruskalWeight = kruskalResult.second;
    pair<vector<Edge>, int> primResult = prim(n, edges, 1);
    vector<Edge> primMst = primResult.first;
    int primWeight = primResult.second;
    printResult("Kruskal", kruskalMst, kruskalWeight);
    printResult("Prim(start from V1)", primMst, primWeight);
    return 0;
}
