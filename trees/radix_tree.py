from dataclasses import dataclass, field
from typing import Dict, Generic, Optional, TypeVar, List, Tuple

V = TypeVar("V")


def _lcp(a: str, b: str) -> int:
    """Longest common prefix length."""
    i = 0
    m = min(len(a), len(b))
    while i < m and a[i] == b[i]:
        i += 1
    return i


@dataclass
class _Node(Generic[V]):
    label: str = ""                          # edge label from parent -> this node
    children: Dict[str, "_Node[V]"] = field(default_factory=dict)  # keyed by first char of child.label
    is_terminal: bool = False
    value: Optional[V] = None


class RadixTree(Generic[V]):
    """
    Compressed prefix tree (Radix Tree) for string keys.

    Operations:
      - insert(key, value)
      - search(key) -> Optional[value]
      - delete(key) -> bool
      - starts_with(prefix) -> list[(key, value)]
    """

    def __init__(self) -> None:
        self.root: _Node[V] = _Node("")
        self._size = 0

    def __len__(self) -> int:
        return self._size

    # ---------------- Public API ----------------

    def insert(self, key: str, value: V) -> None:
        if not isinstance(key, str):
            raise TypeError("RadixTree keys must be strings")
        self._insert(self.root, key, value)

    def search(self, key: str) -> Optional[V]:
        if not isinstance(key, str):
            raise TypeError("RadixTree keys must be strings")
        node = self._find_node(key)
        if node is not None and node.is_terminal:
            return node.value
        return None

    def delete(self, key: str) -> bool:
        if not isinstance(key, str):
            raise TypeError("RadixTree keys must be strings")
        deleted = self._delete(self.root, key)
        return deleted

    def starts_with(self, prefix: str) -> List[Tuple[str, V]]:
        if not isinstance(prefix, str):
            raise TypeError("RadixTree keys must be strings")
        found = self._locate_prefix_node(prefix)
        if found is None:
            return []
        node, consumed_prefix = found
        out: List[Tuple[str, V]] = []
        self._collect(node, consumed_prefix, out)
        return out

    # ---------------- Internal insert ----------------

    def _insert(self, parent: _Node[V], key: str, value: V) -> None:
        if key == "":
            # terminal at current node
            if not parent.is_terminal:
                self._size += 1
            parent.is_terminal = True
            parent.value = value
            return

        first = key[0]
        child = parent.children.get(first)

        if child is None:
            # no edge with this starting char
            n = _Node[V](label=key, is_terminal=True, value=value)
            parent.children[first] = n
            self._size += 1
            return

        common = _lcp(child.label, key)

        if common == len(child.label):
            # full child label matched, continue downward
            rest = key[common:]
            self._insert(child, rest, value)
            return

        # need split existing child at `common`
        # existing child label = X + Y, new key = X + Z where X is common
        x = child.label[:common]
        y = child.label[common:]     # old remainder
        z = key[common:]             # new remainder

        # intermediate node with label X replaces old child
        mid = _Node[V](label=x)

        # reattach old child under mid with label Y
        child.label = y
        mid.children[y[0]] = child

        if z == "":
            # key ends exactly at split point
            mid.is_terminal = True
            mid.value = value
            self._size += 1
        else:
            # add new leaf for Z
            new_leaf = _Node[V](label=z, is_terminal=True, value=value)
            mid.children[z[0]] = new_leaf
            self._size += 1

        # replace parent link
        parent.children[first] = mid

    # ---------------- Internal search helpers ----------------

    def _find_node(self, key: str) -> Optional[_Node[V]]:
        cur = self.root
        rest = key
        while True:
            if rest == "":
                return cur
            child = cur.children.get(rest[0])
            if child is None:
                return None
            common = _lcp(child.label, rest)
            if common != len(child.label):
                return None
            rest = rest[common:]
            cur = child

    def _locate_prefix_node(self, prefix: str) -> Optional[Tuple[_Node[V], str]]:
        """
        Returns (node, full_string_to_node) where node is where prefix ends
        or inside an edge. For inside-edge case, build a virtual traversal by
        returning the child and consumed string to that child.
        """
        cur = self.root
        built = ""
        rest = prefix

        while rest:
            child = cur.children.get(rest[0])
            if child is None:
                return None
            common = _lcp(child.label, rest)

            if common == 0:
                return None

            # prefix ends in middle of child label
            if common < len(child.label) and common == len(rest):
                built += rest
                return child, built

            # mismatch in the middle => no prefix match
            if common < len(child.label) and common < len(rest):
                return None

            built += child.label
            rest = rest[common:]
            cur = child

        return cur, built

    def _collect(self, node: _Node[V], built_key: str, out: List[Tuple[str, V]]) -> None:
        # For exact node path, built_key should already include node.label in caller logic.
        # Here we treat node as corresponding to built_key endpoint.
        if node.is_terminal and node.value is not None:
            out.append((built_key, node.value))

        for child in node.children.values():
            self._collect(child, built_key + child.label, out)

    # ---------------- Internal delete ----------------

    def _delete(self, parent: _Node[V], key: str) -> bool:
        if key == "":
            if not parent.is_terminal:
                return False
            parent.is_terminal = False
            parent.value = None
            self._size -= 1
            return True

        first = key[0]
        child = parent.children.get(first)
        if child is None:
            return False

        common = _lcp(child.label, key)
        if common != len(child.label):
            return False

        rest = key[common:]
        deleted = self._delete(child, rest)
        if not deleted:
            return False

        # Cleanup / compression after delete:
        # 1) remove child if it became empty non-terminal leaf
        if not child.is_terminal and len(child.children) == 0:
            del parent.children[first]
            return True

        # 2) compress child if non-terminal and only one child
        if not child.is_terminal and len(child.children) == 1:
            only = next(iter(child.children.values()))
            child.label = child.label + only.label
            child.is_terminal = only.is_terminal
            child.value = only.value
            child.children = only.children

        return True

    # ---------------- Debug / validation ----------------

    def items(self) -> List[Tuple[str, V]]:
        out: List[Tuple[str, V]] = []
        self._collect(self.root, "", out)
        return sorted(out, key=lambda kv: kv[0])

    def validate(self) -> None:
        """
        Basic invariants:
        - children map key equals child.label[0]
        - no non-root node has empty label
        - no non-terminal node has exactly one child (should be compressed)
        """
        def dfs(node: _Node[V], is_root: bool) -> None:
            if not is_root:
                assert node.label != ""
            for ch, child in node.children.items():
                assert child.label != ""
                assert ch == child.label[0]
                dfs(child, False)

            if not is_root and (not node.is_terminal) and len(node.children) == 1:
                raise AssertionError("Uncompressed unary non-terminal node found")

        dfs(self.root, True)



def main():
    tree = RadixTree[int]()

    words = [
        "car", "card", "care", "careful", "cargo",
        "cat", "cater", "dog", "dove"
    ]

    print("=== INSERT ===")
    for i, w in enumerate(words, start=1):
        tree.insert(w, i)
        print(f"insert({w!r}, {i})")

    tree.validate()
    print(f"\nTree validated. Size = {len(tree)}")

    print("\n=== SEARCH ===")
    tests = ["car", "care", "cater", "can", "doge", "dove"]
    for w in tests:
        print(f"search({w!r}) -> {tree.search(w)}")

    print("\n=== PREFIX QUERY ===")
    for p in ["car", "cat", "do", "z"]:
        matches = tree.starts_with(p)
        print(f"starts_with({p!r}) -> {matches}")

    print("\n=== DELETE ===")
    to_delete = ["care", "cat", "dog", "not-there"]
    for w in to_delete:
        ok = tree.delete(w)
        print(f"delete({w!r}) -> {ok}")

    tree.validate()
    print(f"\nTree validated after deletes. Size = {len(tree)}")

    print("\n=== FINAL ITEMS ===")
    for k, v in tree.items():
        print(f"{k} -> {v}")


if __name__ == "__main__":
    main()