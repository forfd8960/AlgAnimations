from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Any


@dataclass(frozen=True)
class Point:
    x: float
    y: float
    data: Any = None


@dataclass(frozen=True)
class Rect:
    """
    Axis-aligned rectangle with center (cx, cy) and half-size (hw, hh).
    """
    cx: float
    cy: float
    hw: float
    hh: float

    def contains(self, p: Point) -> bool:
        return (
            self.cx - self.hw <= p.x <= self.cx + self.hw
            and self.cy - self.hh <= p.y <= self.cy + self.hh
        )

    def intersects(self, other: "Rect") -> bool:
        return not (
            other.cx - other.hw > self.cx + self.hw
            or other.cx + other.hw < self.cx - self.hw
            or other.cy - other.hh > self.cy + self.hh
            or other.cy + other.hh < self.cy - self.hh
        )


class Quadtree:
    """
    Point Quadtree for 2D spatial indexing.

    - Every internal node subdivides into exactly four children:
      NW, NE, SW, SE
    - Stores points until capacity is exceeded, then subdivides.
    - Supports:
        insert(point)
        query_range(rect)
        query_radius(x, y, r)
        remove(point)
        clear()
    """

    __slots__ = (
        "boundary",
        "capacity",
        "points",
        "divided",
        "nw",
        "ne",
        "sw",
        "se",
    )

    def __init__(self, boundary: Rect, capacity: int = 4) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        if boundary.hw <= 0 or boundary.hh <= 0:
            raise ValueError("boundary half-width/half-height must be > 0")

        self.boundary: Rect = boundary
        self.capacity: int = capacity
        self.points: List[Point] = []
        self.divided: bool = False

        self.nw: Optional["Quadtree"] = None
        self.ne: Optional["Quadtree"] = None
        self.sw: Optional["Quadtree"] = None
        self.se: Optional["Quadtree"] = None

    # ---------------- Public API ----------------

    def insert(self, p: Point) -> bool:
        """
        Insert a point into the quadtree.
        Returns True if inserted, False if out of bounds.
        """
        if not self.boundary.contains(p):
            return False

        if len(self.points) < self.capacity and not self.divided:
            self.points.append(p)
            return True

        if not self.divided:
            self._subdivide()
            # Reinsert existing points into children
            old_points = self.points
            self.points = []
            for op in old_points:
                self._insert_into_children(op)

        return self._insert_into_children(p)

    def query_range(self, area: Rect) -> List[Point]:
        """
        Return all points inside/intersecting the query rectangle.
        """
        found: List[Point] = []
        self._query_range(area, found)
        return found

    def query_radius(self, x: float, y: float, r: float) -> List[Point]:
        """
        Return all points within a circle centered at (x, y) with radius r.
        """
        if r < 0:
            raise ValueError("radius must be >= 0")

        # First coarse filter by bounding box, then exact circle distance test.
        box = Rect(x, y, r, r)
        candidates = self.query_range(box)
        r2 = r * r
        return [p for p in candidates if (p.x - x) ** 2 + (p.y - y) ** 2 <= r2]

    def remove(self, p: Point) -> bool:
        """
        Remove first exact matching point (x, y, data).
        Returns True if removed, else False.
        """
        if not self.boundary.contains(p):
            return False

        # Leaf node case
        if not self.divided:
            for i, cur in enumerate(self.points):
                if cur == p:
                    self.points.pop(i)
                    return True
            return False

        # Internal node case
        removed = (
            self.nw.remove(p) or self.ne.remove(p) or self.sw.remove(p) or self.se.remove(p)  # type: ignore[union-attr]
        )

        if removed:
            self._try_merge()
        return removed

    def clear(self) -> None:
        self.points.clear()
        self.divided = False
        self.nw = self.ne = self.sw = self.se = None

    def __len__(self) -> int:
        if not self.divided:
            return len(self.points)
        return (
            len(self.nw) + len(self.ne) + len(self.sw) + len(self.se)  # type: ignore[arg-type]
        )

    # ---------------- Internal ----------------

    def _subdivide(self) -> None:
        cx, cy, hw, hh = (
            self.boundary.cx,
            self.boundary.cy,
            self.boundary.hw,
            self.boundary.hh,
        )
        qhw, qhh = hw / 2, hh / 2

        # NW, NE, SW, SE
        self.nw = Quadtree(Rect(cx - qhw, cy + qhh, qhw, qhh), self.capacity)
        self.ne = Quadtree(Rect(cx + qhw, cy + qhh, qhw, qhh), self.capacity)
        self.sw = Quadtree(Rect(cx - qhw, cy - qhh, qhw, qhh), self.capacity)
        self.se = Quadtree(Rect(cx + qhw, cy - qhh, qhw, qhh), self.capacity)

        self.divided = True

    def _insert_into_children(self, p: Point) -> bool:
        # Exactly one should accept if boundaries are consistent.
        return (
            self.nw.insert(p)  # type: ignore[union-attr]
            or self.ne.insert(p)  # type: ignore[union-attr]
            or self.sw.insert(p)  # type: ignore[union-attr]
            or self.se.insert(p)  # type: ignore[union-attr]
        )

    def _query_range(self, area: Rect, found: List[Point]) -> None:
        if not self.boundary.intersects(area):
            return

        if not self.divided:
            for p in self.points:
                if area.contains(p):
                    found.append(p)
            return

        self.nw._query_range(area, found)  # type: ignore[union-attr]
        self.ne._query_range(area, found)  # type: ignore[union-attr]
        self.sw._query_range(area, found)  # type: ignore[union-attr]
        self.se._query_range(area, found)  # type: ignore[union-attr]

    def _try_merge(self) -> None:
        """
        Merge children back into this node if all children are leaves and total points
        fit in this node's capacity.
        """
        if not self.divided:
            return

        children = [self.nw, self.ne, self.sw, self.se]
        if any(c is None or c.divided for c in children):
            return

        total = sum(len(c.points) for c in children if c is not None)
        if total <= self.capacity:
            self.points = []
            for c in children:
                self.points.extend(c.points)  # type: ignore[union-attr]
            self.nw = self.ne = self.sw = self.se = None
            self.divided = False

    # ---------------- Debug helpers ----------------

    def stats(self) -> Tuple[int, int]:
        """
        Returns (node_count, point_count).
        """
        if not self.divided:
            return 1, len(self.points)

        n1, p1 = self.nw.stats()  # type: ignore[union-attr]
        n2, p2 = self.ne.stats()  # type: ignore[union-attr]
        n3, p3 = self.sw.stats()  # type: ignore[union-attr]
        n4, p4 = self.se.stats()  # type: ignore[union-attr]
        return 1 + n1 + n2 + n3 + n4, p1 + p2 + p3 + p4
    



def main():
    # World boundary centered at (0,0), width=200, height=200
    world = Rect(cx=0, cy=0, hw=100, hh=100)
    qt = Quadtree(boundary=world, capacity=4)

    points = [
        Point(-10, 20, "A"),
        Point(15, 25, "B"),
        Point(30, -40, "C"),
        Point(-50, -60, "D"),
        Point(70, 80, "E"),
        Point(5, 5, "F"),
        Point(8, 7, "G"),
        Point(9, 6, "H"),
    ]

    print("=== INSERT ===")
    for p in points:
        ok = qt.insert(p)
        print(f"insert({p}) -> {ok}")

    nodes, total_points = qt.stats()
    print(f"\nTree stats: nodes={nodes}, points={total_points}, len={len(qt)}")

    print("\n=== RANGE QUERY ===")
    area = Rect(cx=0, cy=0, hw=20, hh=30)
    found = qt.query_range(area)
    print(f"query_range(center=(0,0), hw=20, hh=30) -> {len(found)} point(s)")
    for p in found:
        print(" ", p)

    print("\n=== RADIUS QUERY ===")
    near = qt.query_radius(x=0, y=0, r=15)
    print(f"query_radius(center=(0,0), r=15) -> {len(near)} point(s)")
    for p in near:
        print(" ", p)

    print("\n=== REMOVE ===")
    target = Point(5, 5, "F")
    print(f"remove({target}) -> {qt.remove(target)}")
    print(f"remove({target}) again -> {qt.remove(target)}")

    nodes, total_points = qt.stats()
    print(f"\nAfter remove: nodes={nodes}, points={total_points}, len={len(qt)}")


if __name__ == "__main__":
    main()