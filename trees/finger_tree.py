from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, Iterable, Iterator, List, Optional, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class FingerTree(Generic[T]):
    """
    Simplified persistent finger-tree-like sequence.

    This is a practical educational variant:
      - O(1) amortized prepend/append
      - fast access near ends via small 'fingers'
      - persistent (operations return new tree)
    Internally uses front/back buffers + middle tuple chunks.
    """
    _front: tuple[T, ...] = ()
    _mid: tuple[T, ...] = ()
    _back: tuple[T, ...] = ()
    _finger: int = 8  # max small buffer size before rebalancing

    @staticmethod
    def empty() -> "FingerTree[T]":
        return FingerTree()

    @staticmethod
    def from_iter(it: Iterable[T]) -> "FingerTree[T]":
        ft = FingerTree.empty()
        for x in it:
            ft = ft.append(x)
        return ft

    def __len__(self) -> int:
        return len(self._front) + len(self._mid) + len(self._back)

    def prepend(self, x: T) -> "FingerTree[T]":
        nf = (x,) + self._front
        return self._rebalance(nf, self._mid, self._back)

    def append(self, x: T) -> "FingerTree[T]":
        nb = self._back + (x,)
        return self._rebalance(self._front, self._mid, nb)

    def peek_left(self) -> T:
        if len(self) == 0:
            raise IndexError("peek_left from empty FingerTree")
        if self._front:
            return self._front[0]
        if self._mid:
            return self._mid[0]
        return self._back[0]

    def peek_right(self) -> T:
        if len(self) == 0:
            raise IndexError("peek_right from empty FingerTree")
        if self._back:
            return self._back[-1]
        if self._mid:
            return self._mid[-1]
        return self._front[-1]

    def pop_left(self) -> tuple[T, "FingerTree[T]"]:
        if len(self) == 0:
            raise IndexError("pop_left from empty FingerTree")
        if self._front:
            x = self._front[0]
            nf = self._front[1:]
            return x, self._rebalance(nf, self._mid, self._back)
        if self._mid:
            x = self._mid[0]
            nm = self._mid[1:]
            return x, self._rebalance(self._front, nm, self._back)
        x = self._back[0]
        nb = self._back[1:]
        return x, FingerTree((), (), nb, self._finger)

    def pop_right(self) -> tuple[T, "FingerTree[T]"]:
        if len(self) == 0:
            raise IndexError("pop_right from empty FingerTree")
        if self._back:
            x = self._back[-1]
            nb = self._back[:-1]
            return x, self._rebalance(self._front, self._mid, nb)
        if self._mid:
            x = self._mid[-1]
            nm = self._mid[:-1]
            return x, self._rebalance(self._front, nm, self._back)
        x = self._front[-1]
        nf = self._front[:-1]
        return x, FingerTree(nf, (), (), self._finger)

    def concat(self, other: "FingerTree[T]") -> "FingerTree[T]":
        return FingerTree.from_iter(list(self) + list(other))

    def to_list(self) -> List[T]:
        return list(self._front) + list(self._mid) + list(self._back)

    def __iter__(self) -> Iterator[T]:
        yield from self._front
        yield from self._mid
        yield from self._back

    def _rebalance(
        self, front: tuple[T, ...], mid: tuple[T, ...], back: tuple[T, ...]
    ) -> "FingerTree[T]":
        # keep front/back small; spill extras into mid
        fmax = self._finger
        bmax = self._finger

        if len(front) > fmax:
            spill = front[fmax:]
            front = front[:fmax]
            mid = spill + mid

        if len(back) > bmax:
            spill = back[:-bmax]
            back = back[-bmax:]
            mid = mid + spill

        # if front empty but mid has data, pull some to front
        if not front and mid:
            take = min(fmax, len(mid))
            front = mid[:take]
            mid = mid[take:]

        # if back empty but mid has data, pull some to back
        if not back and mid:
            take = min(bmax, len(mid))
            back = mid[-take:]
            mid = mid[:-take]

        return FingerTree(front, mid, back, self._finger)
    
    

def main() -> None:
    ft = FingerTree.empty()
    ft = ft.append(10).append(20).prepend(5).append(30).prepend(1)
    print("\nFingerTree contents:", ft.to_list())
    print("peek_left:", ft.peek_left(), "peek_right:", ft.peek_right())

    x, ft = ft.pop_left()
    y, ft = ft.pop_right()
    print("pop_left:", x, "pop_right:", y)
    print("After pops:", ft.to_list())
    
    
if __name__ == "__main__":
    main()