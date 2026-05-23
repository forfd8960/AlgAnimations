from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple


@dataclass(frozen=True)
class Point3D:
    x: float
    y: float
    z: float
    data: Any = None


@dataclass(frozen=True)
class Box:
    """
    Axis-aligned 3D box defined by center (cx, cy, cz) and half sizes (hx, hy, hz).
    """
    cx: float
    cy: float
    cz: float
    hx: float
    hy: float
    hz: float

    def contains(self, p: Point3D) -> bool:
        return (
            self.cx - self.hx <= p.x <= self.cx + self.hx
            and self.cy - self.hy <= p.y <= self.cy + self.hy
            and self.cz - self.hz <= p.z <= self.cz + self.hz
        )

    def intersects(self, other: "Box") -> bool:
        return not (
            other.cx - other.hx > self.cx + self.hx
            or other.cx + other.hx < self.cx - self.hx
            or other.cy - other.hy > self.cy + self.hy
            or other.cy + other.hy < self.cy - self.hy
            or other.cz - other.hz > self.cz + self.hz
            or other.cz + other.hz < self.cz - self.hz
        )


class Octree:
    """
    Point Octree for 3D spatial indexing.

    Each internal node splits into exactly 8 children (octants):
      LDB, RDB, LUB, RUB, LDF, RDF, LUF, RUF
      (L/R = left/right x, D/U = down/up y, B/F = back/front z)

    Supports:
      - insert(point)
      - query_box(box)
      - query_radius(x, y, z, r)
      - remove(point)
      - clear()
      - stats() -> (node_count, point_count)
    """

    __slots__ = (
        "boundary",
        "capacity",
        "points",
        "divided",
        "children",  # length 8 when divided else None
    )

    def __init__(self, boundary: Box, capacity: int = 8) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        if boundary.hx <= 0 or boundary.hy <= 0 or boundary.hz <= 0:
            raise ValueError("boundary half-sizes must be > 0")

        self.boundary: Box = boundary
        self.capacity: int = capacity
        self.points: List[Point3D] = []
        self.divided: bool = False
        self.children: Optional[List["Octree"]] = None

    # ---------------- Public API ----------------

    def insert(self, p: Point3D) -> bool:
        """Insert a point. Returns False if out of boundary."""
        if not self.boundary.contains(p):
            return False

        if not self.divided and len(self.points) < self.capacity:
            self.points.append(p)
            return True

        if not self.divided:
            self._subdivide()
            old = self.points
            self.points = []
            for q in old:
                self._insert_into_children(q)

        return self._insert_into_children(p)

    def query_box(self, area: Box) -> List[Point3D]:
        found: List[Point3D] = []
        self._query_box(area, found)
        return found

    def query_radius(self, x: float, y: float, z: float, r: float) -> List[Point3D]:
        if r < 0:
            raise ValueError("radius must be >= 0")
        # coarse box filter
        area = Box(x, y, z, r, r, r)
        candidates = self.query_box(area)
        r2 = r * r
        return [
            p for p in candidates
            if (p.x - x) ** 2 + (p.y - y) ** 2 + (p.z - z) ** 2 <= r2
        ]

    def remove(self, p: Point3D) -> bool:
        """Remove first exact matching point. Returns True if removed."""
        if not self.boundary.contains(p):
            return False

        if not self.divided:
            for i, cur in enumerate(self.points):
                if cur == p:
                    self.points.pop(i)
                    return True
            return False

        assert self.children is not None
        removed = False
        for child in self.children:
            if child.remove(p):
                removed = True
                break

        if removed:
            self._try_merge()
        return removed

    def clear(self) -> None:
        self.points.clear()
        self.divided = False
        self.children = None

    def __len__(self) -> int:
        if not self.divided:
            return len(self.points)
        assert self.children is not None
        return sum(len(ch) for ch in self.children)

    def stats(self) -> Tuple[int, int]:
        """Returns (node_count, point_count)."""
        if not self.divided:
            return 1, len(self.points)
        assert self.children is not None
        node_count = 1
        point_count = 0
        for ch in self.children:
            n, p = ch.stats()
            node_count += n
            point_count += p
        return node_count, point_count

    # ---------------- Internal ----------------

    def _subdivide(self) -> None:
        b = self.boundary
        qx, qy, qz = b.hx / 2.0, b.hy / 2.0, b.hz / 2.0

        xs = [b.cx - qx, b.cx + qx]  # L, R
        ys = [b.cy - qy, b.cy + qy]  # D, U
        zs = [b.cz - qz, b.cz + qz]  # B, F

        # Order: LDB, RDB, LUB, RUB, LDF, RDF, LUF, RUF
        centers = [
            (xs[0], ys[0], zs[0]),
            (xs[1], ys[0], zs[0]),
            (xs[0], ys[1], zs[0]),
            (xs[1], ys[1], zs[0]),
            (xs[0], ys[0], zs[1]),
            (xs[1], ys[0], zs[1]),
            (xs[0], ys[1], zs[1]),
            (xs[1], ys[1], zs[1]),
        ]

        self.children = [
            Octree(Box(cx, cy, cz, qx, qy, qz), self.capacity) for (cx, cy, cz) in centers
        ]
        self.divided = True

    def _insert_into_children(self, p: Point3D) -> bool:
        assert self.children is not None
        for ch in self.children:
            if ch.insert(p):
                return True
        return False  # should not happen if boundaries are consistent

    def _query_box(self, area: Box, out: List[Point3D]) -> None:
        if not self.boundary.intersects(area):
            return

        if not self.divided:
            for p in self.points:
                if area.contains(p):
                    out.append(p)
            return

        assert self.children is not None
        for ch in self.children:
            ch._query_box(area, out)

    def _try_merge(self) -> None:
        """Merge children back if all children are leaves and total points <= capacity."""
        if not self.divided or self.children is None:
            return

        # Can merge only if all children are non-divided
        if any(ch.divided for ch in self.children):
            return

        total = sum(len(ch.points) for ch in self.children)
        if total <= self.capacity:
            self.points = []
            for ch in self.children:
                self.points.extend(ch.points)
            self.children = None
            self.divided = False
            
            
            
def main():
    world = Box(cx=0, cy=0, cz=0, hx=100, hy=100, hz=100)
    tree = Octree(boundary=world, capacity=4)

    pts = [
        Point3D(-10, 20, 5, "A"),
        Point3D(15, 25, -12, "B"),
        Point3D(30, -40, 10, "C"),
        Point3D(-50, -60, 30, "D"),
        Point3D(70, 80, -70, "E"),
        Point3D(5, 5, 5, "F"),
        Point3D(8, 7, 6, "G"),
        Point3D(9, 6, 4, "H"),
    ]

    print("=== INSERT ===")
    for p in pts:
        print(f"insert({p}) -> {tree.insert(p)}")

    nodes, count = tree.stats()
    print(f"\nTree stats: nodes={nodes}, points={count}, len={len(tree)}")

    print("\n=== BOX QUERY ===")
    region = Box(cx=0, cy=0, cz=0, hx=20, hy=30, hz=20)
    found = tree.query_box(region)
    print(f"query_box(center=(0,0,0), half=(20,30,20)) -> {len(found)} point(s)")
    for p in found:
        print(" ", p)

    print("\n=== RADIUS QUERY ===")
    near = tree.query_radius(0, 0, 0, 15)
    print(f"query_radius((0,0,0), r=15) -> {len(near)} point(s)")
    for p in near:
        print(" ", p)

    print("\n=== REMOVE ===")
    target = Point3D(5, 5, 5, "F")
    print(f"remove({target}) -> {tree.remove(target)}")
    print(f"remove({target}) again -> {tree.remove(target)}")

    nodes, count = tree.stats()
    print(f"\nAfter remove: nodes={nodes}, points={count}, len={len(tree)}")


if __name__ == "__main__":
    main()