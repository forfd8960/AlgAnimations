from __future__ import annotations
from typing import List


class DisjointSetForest:
    """
    Union-Find / Disjoint Set Union (DSU):
      - path compression
      - union by rank + size tracking
    """

    def __init__(self, n: int) -> None:
        self.parent: List[int] = list(range(n))
        self.rank: List[int] = [0] * n
        self.size: List[int] = [1] * n
        self.components = n

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a: int, b: int) -> bool:
        ra = self.find(a)
        rb = self.find(b)
        if ra == rb:
            return False

        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra

        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1

        self.components -= 1
        return True

    def connected(self, a: int, b: int) -> bool:
        return self.find(a) == self.find(b)

    def component_size(self, x: int) -> int:
        return self.size[self.find(x)]
    
    
def main() -> None:
    dsu = DisjointSetForest(7)
    dsu.union(0, 1)
    dsu.union(1, 2)
    dsu.union(3, 4)
    print("\nDSU connected(0,2):", dsu.connected(0, 2))
    print("DSU connected(0,4):", dsu.connected(0, 4))
    dsu.union(2, 4)
    print("After union(2,4), connected(0,4):", dsu.connected(0, 4))
    print("Component size of 3:", dsu.component_size(3))
    print("Components:", dsu.components)
    
if __name__ == "__main__":
    main()