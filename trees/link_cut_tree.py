from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class _Node:
    val: int = 0
    sum: int = 0
    left: Optional["_Node"] = None
    right: Optional["_Node"] = None
    parent: Optional["_Node"] = None
    rev: bool = False

    def __post_init__(self) -> None:
        self.sum = self.val


class LinkCutTree:
    """
    Link-Cut Tree (splay-based) for dynamic forest.

    Supports:
      - make_tree(value=0) -> node_id
      - link(u, v): connect roots of two trees
      - cut(u, v): remove edge (u, v) if it exists
      - connected(u, v)
      - set_value(u, x)
      - path_sum(u, v): sum of node values on path u-v

    Node IDs are integers returned by make_tree().
    """

    def __init__(self) -> None:
        self.nodes: List[_Node] = []

    def make_tree(self, value: int = 0) -> int:
        nd = _Node(val=value)
        self.nodes.append(nd)
        return len(self.nodes) - 1

    # ---------- Public ops ----------

    def connected(self, u: int, v: int) -> bool:
        if u == v:
            return True
        nu, nv = self.nodes[u], self.nodes[v]
        self._access(nu)
        self._access(nv)
        return nu.parent is not None

    def link(self, u: int, v: int) -> None:
        """
        Link root(u) as child of v. Requires u and v in different trees.
        """
        nu, nv = self.nodes[u], self.nodes[v]
        self._make_root(nu)
        if self._find_root(nv) is nu:
            raise ValueError("u and v are already connected")
        nu.parent = nv

    def cut(self, u: int, v: int) -> None:
        """
        Cut edge (u, v) if present.
        """
        nu, nv = self.nodes[u], self.nodes[v]
        self._make_root(nu)
        self._access(nv)
        # Now nu should be nv.left if edge exists directly
        if nv.left is not nu or nu.right is not None or nu.left is not None:
            raise ValueError("edge (u, v) does not exist as a direct link")
        nv.left.parent = None
        nv.left = None
        self._pull(nv)

    def set_value(self, u: int, value: int) -> None:
        n = self.nodes[u]
        self._access(n)
        n.val = value
        self._pull(n)

    def path_sum(self, u: int, v: int) -> int:
        nu, nv = self.nodes[u], self.nodes[v]
        self._make_root(nu)
        self._access(nv)
        return nv.sum

    # ---------- Core LCT internals ----------

    def _is_root(self, x: _Node) -> bool:
        return x.parent is None or (x.parent.left is not x and x.parent.right is not x)

    def _push(self, x: _Node) -> None:
        if x.rev:
            x.left, x.right = x.right, x.left
            if x.left:
                x.left.rev ^= True
            if x.right:
                x.right.rev ^= True
            x.rev = False

    def _pull(self, x: _Node) -> None:
        x.sum = x.val
        if x.left:
            x.sum += x.left.sum
        if x.right:
            x.sum += x.right.sum

    def _rotate(self, x: _Node) -> None:
        p = x.parent
        g = p.parent if p else None
        assert p is not None

        self._push(p)
        self._push(x)

        if p.left is x:
            b = x.right
            x.right = p
            p.left = b
            if b:
                b.parent = p
        else:
            b = x.left
            x.left = p
            p.right = b
            if b:
                b.parent = p

        x.parent = g
        if g:
            if g.left is p:
                g.left = x
            elif g.right is p:
                g.right = x
        p.parent = x

        self._pull(p)
        self._pull(x)

    def _splay(self, x: _Node) -> None:
        # push path top-down
        st = []
        y = x
        st.append(y)
        while not self._is_root(y):
            y = y.parent
            st.append(y)
        for n in reversed(st):
            self._push(n)

        while not self._is_root(x):
            p = x.parent
            g = p.parent if p else None
            if p is not None and not self._is_root(p):
                if (p.left is x) == (g.left is p):  # zig-zig
                    self._rotate(p)
                else:  # zig-zag
                    self._rotate(x)
            self._rotate(x)

    def _access(self, x: _Node) -> None:
        last: Optional[_Node] = None
        cur: Optional[_Node] = x
        while cur is not None:
            self._splay(cur)
            cur.right = last
            self._pull(cur)
            last = cur
            cur = cur.parent
        self._splay(x)

    def _make_root(self, x: _Node) -> None:
        self._access(x)
        x.rev ^= True
        self._push(x)

    def _find_root(self, x: _Node) -> _Node:
        self._access(x)
        while x.left:
            self._push(x)
            x = x.left
        self._splay(x)
        return x
    
    
def main() -> None:
    lct = LinkCutTree()
    a = lct.make_tree(5)
    b = lct.make_tree(2)
    c = lct.make_tree(7)
    d = lct.make_tree(1)

    lct.link(a, b)  # a-b
    lct.link(b, c)  # a-b-c
    lct.link(c, d)  # a-b-c-d

    print("\nLCT connected(a,d):", lct.connected(a, d))
    print("LCT path_sum(a,d):", lct.path_sum(a, d))  # 5+2+7+1 = 15

    lct.cut(c, d)
    print("After cut(c,d), connected(a,d):", lct.connected(a, d))
    print("After cut(c,d), connected(c,d):", lct.connected(c, d))
    
if __name__ == "__main__":
    main()