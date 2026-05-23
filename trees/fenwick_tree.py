from __future__ import annotations
from typing import List


class FenwickTree:
    """
    Fenwick Tree / Binary Indexed Tree for prefix sums.
    Supports:
      - add(i, delta)
      - prefix_sum(i)
      - range_sum(l, r)
      - build from array in O(n log n)
    Indices for API are 0-based.
    """

    def __init__(self, n_or_arr: int | List[int]) -> None:
        if isinstance(n_or_arr, int):
            self.n = n_or_arr
            self.bit = [0] * (self.n + 1)
        else:
            arr = n_or_arr
            self.n = len(arr)
            self.bit = [0] * (self.n + 1)
            for i, v in enumerate(arr):
                self.add(i, v)

    def add(self, idx: int, delta: int) -> None:
        i = idx + 1
        while i <= self.n:
            self.bit[i] += delta
            i += i & -i

    def prefix_sum(self, idx: int) -> int:
        """sum(arr[0..idx])"""
        if idx < 0:
            return 0
        s = 0
        i = idx + 1
        while i > 0:
            s += self.bit[i]
            i -= i & -i
        return s

    def range_sum(self, l: int, r: int) -> int:
        if r < l:
            return 0
        return self.prefix_sum(r) - self.prefix_sum(l - 1)

    def point_set(self, idx: int, val: int) -> None:
        cur = self.range_sum(idx, idx)
        self.add(idx, val - cur)
        
        
def main() -> None:
    arr = [2, 1, 5, 3, 4, 7, 6, 8]
    print("Array:", arr)

    ft = FenwickTree(arr)

    print("Fenwick sum[2..6]:", ft.range_sum(2, 6))

    for i in range(3, 6):
        ft.add(i, 10)

    print("After range add +10 to [3..5]:")
    print("Fenwick sum[2..6]:", ft.range_sum(2, 6))
    
    
if __name__ == "__main__":
    main()