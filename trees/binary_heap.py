from __future__ import annotations
from typing import Generic, List, Optional, TypeVar, Callable

T = TypeVar("T")


class BinaryHeap(Generic[T]):
    """
    Binary Heap (array-based), supports min-heap by default.
    Set is_min_heap=False for max-heap behavior.
    """

    def __init__(self, data: Optional[List[T]] = None, *, is_min_heap: bool = True) -> None:
        self._a: List[T] = list(data) if data else []
        self._is_min = is_min_heap
        if self._a:
            self._heapify()

    def __len__(self) -> int:
        return len(self._a)

    def __bool__(self) -> bool:
        return bool(self._a)

    def __repr__(self) -> str:
        kind = "MinHeap" if self._is_min else "MaxHeap"
        return f"{kind}({self._a})"

    # ---------- Public API ----------

    def push(self, x: T) -> None:
        self._a.append(x)
        self._sift_up(len(self._a) - 1)

    def peek(self) -> T:
        if not self._a:
            raise IndexError("peek from empty heap")
        return self._a[0]

    def pop(self) -> T:
        if not self._a:
            raise IndexError("pop from empty heap")
        root = self._a[0]
        last = self._a.pop()
        if self._a:
            self._a[0] = last
            self._sift_down(0)
        return root

    def replace(self, x: T) -> T:
        """
        Pop root and push x in one operation.
        More efficient than pop() + push(x).
        """
        if not self._a:
            raise IndexError("replace from empty heap")
        root = self._a[0]
        self._a[0] = x
        self._sift_down(0)
        return root

    def pushpop(self, x: T) -> T:
        """
        Push x, then pop and return root in one operation.
        """
        if not self._a:
            return x
        if self._comes_before(x, self._a[0]):
            # x would be popped immediately
            return x
        root = self._a[0]
        self._a[0] = x
        self._sift_down(0)
        return root

    def clear(self) -> None:
        self._a.clear()

    def to_list(self) -> List[T]:
        """Returns internal heap array (not sorted)."""
        return list(self._a)

    @classmethod
    def heap_sort(cls, data: List[T], *, ascending: bool = True) -> List[T]:
        """
        Heap sort using this class.
        ascending=True  -> returns ascending sorted list
        ascending=False -> returns descending sorted list
        """
        if ascending:
            h = cls(data, is_min_heap=True)
            return [h.pop() for _ in range(len(h))]
        else:
            h = cls(data, is_min_heap=False)
            return [h.pop() for _ in range(len(h))]

    # ---------- Internal ----------

    def _comes_before(self, x: T, y: T) -> bool:
        """Heap order relation: True if x should be above y."""
        return x < y if self._is_min else x > y

    def _heapify(self) -> None:
        # Last parent down to root
        for i in range((len(self._a) - 2) // 2, -1, -1):
            self._sift_down(i)

    def _sift_up(self, i: int) -> None:
        a = self._a
        while i > 0:
            p = (i - 1) // 2
            if self._comes_before(a[i], a[p]):
                a[i], a[p] = a[p], a[i]
                i = p
            else:
                break

    def _sift_down(self, i: int) -> None:
        a = self._a
        n = len(a)
        while True:
            l = 2 * i + 1
            r = l + 1
            best = i

            if l < n and self._comes_before(a[l], a[best]):
                best = l
            if r < n and self._comes_before(a[r], a[best]):
                best = r

            if best == i:
                break

            a[i], a[best] = a[best], a[i]
            i = best

    # ---------- Optional safety check ----------

    def validate(self) -> None:
        """Raises AssertionError if heap invariant is violated."""
        a = self._a
        for i in range(len(a)):
            l = 2 * i + 1
            r = l + 1
            if l < len(a):
                assert self._comes_before(a[i], a[l]) or a[i] == a[l]
            if r < len(a):
                assert self._comes_before(a[i], a[r]) or a[i] == a[r]



def main():
    nums = [10, 4, 7, 1, 3, 20, 15]

    print("=== Min Heap Demo ===")
    h = BinaryHeap(nums, is_min_heap=True)
    print("initial heap array:", h.to_list())
    print("peek:", h.peek())

    h.push(2)
    print("after push(2):", h.to_list())
    print("pop:", h.pop())
    print("after pop:", h.to_list())
    h.validate()

    print("\nPop all in order:")
    while h:
        print(h.pop(), end=" ")
    print()

    print("\n=== Max Heap Demo ===")
    mh = BinaryHeap(nums, is_min_heap=False)
    print("initial heap array:", mh.to_list())
    print("peek:", mh.peek())
    print("pop sequence:")
    while mh:
        print(mh.pop(), end=" ")
    print()

    print("\n=== Heap Sort ===")
    print("ascending :", BinaryHeap.heap_sort(nums, ascending=True))
    print("descending:", BinaryHeap.heap_sort(nums, ascending=False))


if __name__ == "__main__":
    main()