#include <algorithm>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <queue>
#include <stdexcept>
#include <tuple>
#include <vector>

using namespace std;

struct Edge {
    int u;
    int v;
    int weight;
};

// Disjoint-set union supports cycle detection in Kruskal.
class DisjointSet {
public:
    explicit DisjointSet(int n) : parent(n + 1), rank_value(n + 1, 0) {
        iota(parent.begin(), parent.end(), 0);
    }

    int find(int x) {
        if (parent[x] != x) {
            parent[x] = find(parent[x]);
        }
        return parent[x];
    }

    bool unite(int a, int b) {
        int root_a = find(a);
        int root_b = find(b);
        if (root_a == root_b) {
            return false;
        }

        if (rank_value[root_a] < rank_value[root_b]) {
            swap(root_a, root_b);
        }
        parent[root_b] = root_a;
        if (rank_value[root_a] == rank_value[root_b]) {
            ++rank_value[root_a];
        }
        return true;
    }

private:
    vector<int> parent;
    vector<int> rank_value;
};

tuple<int, int, int> normalizedKey(const Edge& edge) {
    return {edge.weight, min(edge.u, edge.v), max(edge.u, edge.v)};
}

bool edgeLess(const Edge& a, const Edge& b) {
    return normalizedKey(a) < normalizedKey(b);
}

vector<Edge> kruskal(int vertex_count, vector<Edge> edges) {
    // Equal-weight edges are ordered by their normalized endpoints.
    sort(edges.begin(), edges.end(), edgeLess);

    DisjointSet dsu(vertex_count);
    vector<Edge> mst;

    for (const Edge& edge : edges) {
        if (dsu.unite(edge.u, edge.v)) {
            mst.push_back(edge);
            if (static_cast<int>(mst.size()) == vertex_count - 1) {
                break;
            }
        }
    }

    if (static_cast<int>(mst.size()) != vertex_count - 1) {
        throw runtime_error("The graph is disconnected; no spanning tree exists.");
    }
    return mst;
}

vector<Edge> prim(int vertex_count, const vector<Edge>& edges, int start) {
    // Build an undirected adjacency list.
    vector<vector<pair<int, int>>> graph(vertex_count + 1);
    for (const Edge& edge : edges) {
        graph[edge.u].push_back({edge.v, edge.weight});
        graph[edge.v].push_back({edge.u, edge.weight});
    }

    // weight, smaller endpoint, larger endpoint, from, to
    using Candidate = tuple<int, int, int, int, int>;
    priority_queue<Candidate, vector<Candidate>, greater<Candidate>> candidates;
    vector<bool> visited(vertex_count + 1, false);
    vector<Edge> mst;

    auto addCandidates = [&](int vertex) {
        visited[vertex] = true;
        for (const auto& [next, weight] : graph[vertex]) {
            if (!visited[next]) {
                candidates.push(
                    {weight, min(vertex, next), max(vertex, next), vertex, next});
            }
        }
    };

    addCandidates(start);
    while (!candidates.empty() &&
           static_cast<int>(mst.size()) < vertex_count - 1) {
        auto [weight, smaller, larger, from, to] = candidates.top();
        candidates.pop();
        (void)smaller;
        (void)larger;

        if (visited[to]) {
            // This candidate became stale after both endpoints were visited.
            continue;
        }

        mst.push_back({from, to, weight});
        addCandidates(to);
    }

    if (static_cast<int>(mst.size()) != vertex_count - 1) {
        throw runtime_error("The graph is disconnected; no spanning tree exists.");
    }
    return mst;
}

int totalWeight(const vector<Edge>& mst) {
    int total = 0;
    for (const Edge& edge : mst) {
        total += edge.weight;
    }
    return total;
}

bool isSpanningTree(int vertex_count, const vector<Edge>& edges) {
    // A spanning tree on n vertices must contain exactly n - 1 edges.
    if (static_cast<int>(edges.size()) != vertex_count - 1) {
        return false;
    }

    DisjointSet dsu(vertex_count);
    for (const Edge& edge : edges) {
        if (!dsu.unite(edge.u, edge.v)) {
            return false;
        }
    }

    const int root = dsu.find(1);
    for (int vertex = 2; vertex <= vertex_count; ++vertex) {
        if (dsu.find(vertex) != root) {
            return false;
        }
    }
    return true;
}

vector<tuple<int, int, int>> normalizedEdgeSet(const vector<Edge>& edges) {
    vector<tuple<int, int, int>> result;
    result.reserve(edges.size());
    for (const Edge& edge : edges) {
        result.push_back(normalizedKey(edge));
    }
    sort(result.begin(), result.end());
    return result;
}

void printResult(const string& algorithm, const vector<Edge>& mst) {
    cout << algorithm << '\n';
    cout << "Step  Selected edge  Weight\n";

    for (size_t i = 0; i < mst.size(); ++i) {
        const Edge& edge = mst[i];
        cout << setw(4) << i + 1 << "  V" << edge.u << "-V" << edge.v
             << setw(12) << edge.weight << '\n';
    }

    cout << "Edge count: " << mst.size() << '\n';
    cout << "Total weight: " << totalWeight(mst) << "\n\n";
}

int main() {
    const int vertex_count = 6;
    const vector<Edge> edges = {
        {1, 2, 4}, {1, 3, 3}, {1, 4, 1}, {2, 4, 5}, {2, 5, 7},
        {3, 4, 2}, {3, 6, 3}, {4, 5, 5}, {4, 6, 4}, {5, 6, 6},
    };

    try {
        const vector<Edge> kruskal_mst = kruskal(vertex_count, edges);
        const vector<Edge> prim_mst = prim(vertex_count, edges, 1);

        printResult("Kruskal algorithm", kruskal_mst);
        printResult("Prim algorithm (start from V1)", prim_mst);

        const bool same_weight = totalWeight(kruskal_mst) == totalWeight(prim_mst);
        const bool same_edges =
            normalizedEdgeSet(kruskal_mst) == normalizedEdgeSet(prim_mst);
        const bool kruskal_valid =
            isSpanningTree(vertex_count, kruskal_mst);
        const bool prim_valid = isSpanningTree(vertex_count, prim_mst);

        cout << "Verification\n";
        cout << "Kruskal is a spanning tree: "
             << (kruskal_valid ? "YES" : "NO") << '\n';
        cout << "Prim is a spanning tree: " << (prim_valid ? "YES" : "NO")
             << '\n';
        cout << "Same total weight: " << (same_weight ? "YES" : "NO") << '\n';
        cout << "Same normalized edge set: " << (same_edges ? "YES" : "NO")
             << '\n';
        cout << "Verification passed: "
             << (kruskal_valid && prim_valid && same_weight ? "YES" : "NO")
             << '\n';

        // Different edge sets can both be correct when an MST is not unique.
        return kruskal_valid && prim_valid && same_weight ? 0 : 1;
    } catch (const exception& error) {
        cerr << "Error: " << error.what() << '\n';
        return 1;
    }
}
