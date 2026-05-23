from __future__ import annotations
from typing import List


class SegmentTree:
    """
    Segment Tree for range sum query with:
      - point update
      - range add update (lazy propagation)
      - range sum query

    0-based indexing for input array.
    """

    def __init__(self, arr: List[int]) -> None:
        self.n = len(arr)
        if self.n == 0:
            self.tree = [0]
            self.lazy = [0]
            return
        self.tree = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        self._build(1, 0, self.n - 1, arr)

    def _build(self, node: int, l: int, r: int, arr: List[int]) -> None:
        if l == r:
            self.tree[node] = arr[l]
            return
        m = (l + r) // 2
        self._build(node * 2, l, m, arr)
        self._build(node * 2 + 1, m + 1, r, arr)
        self.tree[node] = self.tree[node * 2] + self.tree[node * 2 + 1]

    def _push(self, node: int, l: int, r: int) -> None:
        if self.lazy[node] != 0:
            add = self.lazy[node]
            self.tree[node] += (r - l + 1) * add
            if l != r:
                self.lazy[node * 2] += add
                self.lazy[node * 2 + 1] += add
            self.lazy[node] = 0

    def range_add(self, ql: int, qr: int, val: int) -> None:
        if self.n == 0:
            return
        self._range_add(1, 0, self.n - 1, ql, qr, val)

    def _range_add(self, node: int, l: int, r: int, ql: int, qr: int, val: int) -> None:
        self._push(node, l, r)
        if qr < l or r < ql:
            return
        if ql <= l and r <= qr:
            self.lazy[node] += val
            self._push(node, l, r)
            return
        m = (l + r) // 2
        self._range_add(node * 2, l, m, ql, qr, val)
        self._range_add(node * 2 + 1, m + 1, r, ql, qr, val)
        self.tree[node] = self.tree[node * 2] + self.tree[node * 2 + 1]

    def point_set(self, idx: int, val: int) -> None:
        if self.n == 0:
            return
        cur = self.range_sum(idx, idx)
        self.range_add(idx, idx, val - cur)

    def range_sum(self, ql: int, qr: int) -> int:
        if self.n == 0:
            return 0
        return self._range_sum(1, 0, self.n - 1, ql, qr)

    def _range_sum(self, node: int, l: int, r: int, ql: int, qr: int) -> int:
        self._push(node, l, r)
        if qr < l or r < ql:
            return 0
        if ql <= l and r <= qr:
            return self.tree[node]
        m = (l + r) // 2
        return self._range_sum(node * 2, l, m, ql, qr) + self._range_sum(node * 2 + 1, m + 1, r, ql, qr)
    
    
    
def main() -> None:
    arr = [2, 1, 5, 3, 4, 7, 6, 8]
    print("Array:", arr)

    st = SegmentTree(arr)

    print("Segment sum[2..6]:", st.range_sum(2, 6))

    st.range_add(3, 5, 10)   # add +10 to indices 3..5

    print("After range add +10 to [3..5]:")
    print("Segment sum[2..6]:", st.range_sum(2, 6))
    
    
if __name__ == "__main__":
    main()