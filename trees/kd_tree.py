from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, List, Optional, Sequence, Tuple, TypeVar
import math
import heapq

T = TypeVar("T")  # payload type attached to each point


@dataclass
class KDNode(Generic[T]):
    point: Tuple[float, ...]
    value: Optional[T] = None
    axis: int = 0
    left: Optional["KDNode[T]"] = None
    right: Optional["KDNode[T]"] = None


class KDTree(Generic[T]):
    """
    K-Dimensional Tree (KD-Tree), in-memory.

    Supports:
      - build from points
      - insert(point, value)
      - contains(point)
      - nearest(query) -> (point, value, distance)
      - k_nearest(query, k) -> list[(point, value, distance)] sorted by distance
      - range_search(lower, upper) -> points within axis-aligned box
      - delete(point) (deletes one matching point if duplicates exist)

    Notes:
      - Points are tuples/lists of numeric coordinates with fixed dimension k.
      - Distance metric: Euclidean.
      - Duplicate points are allowed (stored as separate nodes).
    """

    def __init__(
        self,
        points: Optional[Sequence[Tuple[Sequence[float], Optional[T]]]] = None,
        k: Optional[int] = None,
    ) -> None:
        self.root: Optional[KDNode[T]] = None
        self.k: Optional[int] = k

        if points:
            normalized: List[Tuple[Tuple[float, ...], Optional[T]]] = []
            for p, v in points:
                pt = tuple(float(x) for x in p)
                if self.k is None:
                    self.k = len(pt)
                self._check_dim(pt)
                normalized.append((pt, v))
            self.root = self._build_balanced(normalized, depth=0)

    # ---------------- Public API ----------------

    def insert(self, point: Sequence[float], value: Optional[T] = None) -> None:
        pt = self._norm_point(point)
        if self.root is None:
            self.root = KDNode(point=pt, value=value, axis=0)
            return
        self.root = self._insert(self.root, pt, value, depth=0)

    def contains(self, point: Sequence[float]) -> bool:
        pt = self._norm_point(point)
        cur = self.root
        depth = 0
        while cur:
            if cur.point == pt:
                return True
            axis = depth % self.k  # type: ignore[arg-type]
            if pt[axis] < cur.point[axis]:
                cur = cur.left
            else:
                cur = cur.right
            depth += 1
        return False

    def nearest(self, query: Sequence[float]) -> Optional[Tuple[Tuple[float, ...], Optional[T], float]]:
        if self.root is None:
            return None
        q = self._norm_point(query)
        best = [self.root.point, self.root.value, self._dist2(q, self.root.point)]  # mutable holder
        self._nearest(self.root, q, best)
        return best[0], best[1], math.sqrt(best[2])

    def k_nearest(
        self, query: Sequence[float], k: int
    ) -> List[Tuple[Tuple[float, ...], Optional[T], float]]:
        if self.root is None or k <= 0:
            return []
        q = self._norm_point(query)

        # max-heap by negative distance: [(-dist2, point, value)]
        heap: List[Tuple[float, Tuple[float, ...], Optional[T]]] = []
        self._k_nearest(self.root, q, k, heap)

        out = [(pt, val, math.sqrt(-neg_d2)) for (neg_d2, pt, val) in heap]
        out.sort(key=lambda x: x[2])
        return out

    def range_search(
        self, lower: Sequence[float], upper: Sequence[float]
    ) -> List[Tuple[Tuple[float, ...], Optional[T]]]:
        lo = self._norm_point(lower)
        hi = self._norm_point(upper)
        for i in range(self.k or 0):
            if lo[i] > hi[i]:
                raise ValueError(f"lower[{i}] cannot be > upper[{i}]")

        out: List[Tuple[Tuple[float, ...], Optional[T]]] = []
        self._range_search(self.root, lo, hi, out)
        return out

    def delete(self, point: Sequence[float]) -> bool:
        """
        Deletes one node matching 'point'. Returns True if deleted, else False.
        """
        pt = self._norm_point(point)
        self.root, deleted = self._delete(self.root, pt, depth=0)
        return deleted

    # ---------------- Build ----------------

    def _build_balanced(
        self, items: List[Tuple[Tuple[float, ...], Optional[T]]], depth: int
    ) -> Optional[KDNode[T]]:
        if not items:
            return None
        axis = depth % (self.k or 1)
        items.sort(key=lambda x: x[0][axis])
        mid = len(items) // 2

        point, value = items[mid]
        node = KDNode(point=point, value=value, axis=axis)
        node.left = self._build_balanced(items[:mid], depth + 1)
        node.right = self._build_balanced(items[mid + 1 :], depth + 1)
        return node

    # ---------------- Insert ----------------

    def _insert(
        self, node: Optional[KDNode[T]], point: Tuple[float, ...], value: Optional[T], depth: int
    ) -> KDNode[T]:
        if node is None:
            return KDNode(point=point, value=value, axis=depth % (self.k or 1))

        axis = depth % (self.k or 1)
        if point[axis] < node.point[axis]:
            node.left = self._insert(node.left, point, value, depth + 1)
        else:
            node.right = self._insert(node.right, point, value, depth + 1)
        return node

    # ---------------- Nearest ----------------

    def _nearest(self, node: Optional[KDNode[T]], q: Tuple[float, ...], best: list) -> None:
        if node is None:
            return

        d2 = self._dist2(q, node.point)
        if d2 < best[2]:
            best[0], best[1], best[2] = node.point, node.value, d2

        axis = node.axis
        diff = q[axis] - node.point[axis]

        near = node.left if diff < 0 else node.right
        far = node.right if diff < 0 else node.left

        self._nearest(near, q, best)
        if diff * diff < best[2]:
            self._nearest(far, q, best)

    # ---------------- K-Nearest ----------------

    def _k_nearest(
        self,
        node: Optional[KDNode[T]],
        q: Tuple[float, ...],
        k: int,
        heap: List[Tuple[float, Tuple[float, ...], Optional[T]]],
    ) -> None:
        if node is None:
            return

        d2 = self._dist2(q, node.point)
        item = (-d2, node.point, node.value)

        if len(heap) < k:
            heapq.heappush(heap, item)
        else:
            if -heap[0][0] > d2:
                heapq.heapreplace(heap, item)

        axis = node.axis
        diff = q[axis] - node.point[axis]

        near = node.left if diff < 0 else node.right
        far = node.right if diff < 0 else node.left

        self._k_nearest(near, q, k, heap)

        worst_d2 = -heap[0][0] if heap else float("inf")
        if len(heap) < k or diff * diff < worst_d2:
            self._k_nearest(far, q, k, heap)

    # ---------------- Range Search ----------------

    def _range_search(
        self,
        node: Optional[KDNode[T]],
        lo: Tuple[float, ...],
        hi: Tuple[float, ...],
        out: List[Tuple[Tuple[float, ...], Optional[T]]],
    ) -> None:
        if node is None:
            return

        inside = all(lo[i] <= node.point[i] <= hi[i] for i in range(self.k or 0))
        if inside:
            out.append((node.point, node.value))

        axis = node.axis
        if node.left is not None and lo[axis] <= node.point[axis]:
            self._range_search(node.left, lo, hi, out)
        if node.right is not None and node.point[axis] <= hi[axis]:
            self._range_search(node.right, lo, hi, out)

    # ---------------- Delete ----------------

    def _delete(
        self, node: Optional[KDNode[T]], point: Tuple[float, ...], depth: int
    ) -> Tuple[Optional[KDNode[T]], bool]:
        if node is None:
            return None, False

        axis = depth % (self.k or 1)

        if node.point == point:
            # Case 1: If right subtree exists, replace with min from right on current axis
            if node.right is not None:
                min_node = self._find_min(node.right, axis, depth + 1)
                node.point, node.value = min_node.point, min_node.value
                node.right, _ = self._delete(node.right, min_node.point, depth + 1)
                return node, True

            # Case 2: Else if left exists, replace with min from left, then move left subtree to right
            if node.left is not None:
                min_node = self._find_min(node.left, axis, depth + 1)
                node.point, node.value = min_node.point, min_node.value
                node.right = node.left
                node.left = None
                node.right, _ = self._delete(node.right, min_node.point, depth + 1)
                return node, True

            # Case 3: leaf
            return None, True

        deleted = False
        if point[axis] < node.point[axis]:
            node.left, deleted = self._delete(node.left, point, depth + 1)
        else:
            node.right, deleted = self._delete(node.right, point, depth + 1)
        return node, deleted

    def _find_min(self, node: KDNode[T], target_axis: int, depth: int) -> KDNode[T]:
        if node is None:
            raise ValueError("node cannot be None")

        axis = depth % (self.k or 1)

        if axis == target_axis:
            if node.left is None:
                return node
            return self._find_min(node.left, target_axis, depth + 1)

        mins = [node]
        if node.left is not None:
            mins.append(self._find_min(node.left, target_axis, depth + 1))
        if node.right is not None:
            mins.append(self._find_min(node.right, target_axis, depth + 1))
        return min(mins, key=lambda n: n.point[target_axis])

    # ---------------- Helpers ----------------

    def _norm_point(self, point: Sequence[float]) -> Tuple[float, ...]:
        pt = tuple(float(x) for x in point)
        if self.k is None:
            self.k = len(pt)
        self._check_dim(pt)
        return pt

    def _check_dim(self, pt: Tuple[float, ...]) -> None:
        if self.k is None:
            return
        if len(pt) != self.k:
            raise ValueError(f"Point dimension {len(pt)} != tree dimension {self.k}")

    @staticmethod
    def _dist2(a: Tuple[float, ...], b: Tuple[float, ...]) -> float:
        return sum((x - y) ** 2 for x, y in zip(a, b))
    


def main():
    points = [
        ((2, 3), "A"),
        ((5, 4), "B"),
        ((9, 6), "C"),
        ((4, 7), "D"),
        ((8, 1), "E"),
        ((7, 2), "F"),
    ]

    tree = KDTree(points=points, k=2)

    print("Contains (5,4):", tree.contains((5, 4)))
    print("Contains (1,1):", tree.contains((1, 1)))

    print("\nInsert (1,1)='G'")
    tree.insert((1, 1), "G")
    print("Contains (1,1):", tree.contains((1, 1)))

    q = (6, 3)
    nn = tree.nearest(q)
    print(f"\nNearest to {q}: {nn}")

    knn = tree.k_nearest(q, k=3)
    print(f"\n3 nearest to {q}:")
    for item in knn:
        print(item)

    print("\nRange search box [(3,2) .. (9,6)]:")
    inside = tree.range_search((3, 2), (9, 6))
    for p, v in inside:
        print(p, v)

    print("\nDelete (5,4):", tree.delete((5, 4)))
    print("Contains (5,4):", tree.contains((5, 4)))


if __name__ == "__main__":
    main()