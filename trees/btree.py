from bisect import bisect_left, bisect_right
from typing import Any, List, Optional, Tuple


class BPlusTreeNode:
    def __init__(self, leaf: bool = False):
        self.leaf = leaf
        self.keys: List[Any] = []
        # Leaf: values aligned with keys
        # Internal: children count = len(keys) + 1
        self.values: List[Any] = []
        # For leaf-level linked list
        self.next: Optional["BPlusTreeNode"] = None


class BPlusTree:
    """
    order = max number of children in internal nodes
    max keys per node = order - 1
    min children (non-root internal) = ceil(order/2)
    min keys:
      - internal (non-root): ceil(order/2) - 1
      - leaf (non-root): ceil((order-1)/2)
    """

    def __init__(self, order: int = 4):
        if order < 3:
            raise ValueError("order must be >= 3")
        self.order = order
        self.max_keys = order - 1
        self.root = BPlusTreeNode(leaf=True)

    # ---------- Public API ----------

    def get(self, key: Any) -> Optional[Any]:
        leaf = self._find_leaf(key)
        i = bisect_left(leaf.keys, key)
        if i < len(leaf.keys) and leaf.keys[i] == key:
            return leaf.values[i]
        return None

    def insert(self, key: Any, value: Any) -> None:
        promoted = self._insert_recursive(self.root, key, value)
        if promoted is not None:
            k, left, right = promoted
            new_root = BPlusTreeNode(leaf=False)
            new_root.keys = [k]
            new_root.values = [left, right]
            self.root = new_root

    def delete(self, key: Any) -> bool:
        deleted = self._delete_recursive(self.root, key)
        if not deleted:
            return False

        # Root shrink
        if not self.root.leaf and len(self.root.values) == 1:
            self.root = self.root.values[0]
        # Keep root as leaf if it becomes empty internal
        if not self.root.leaf and len(self.root.values) == 0:
            self.root = BPlusTreeNode(leaf=True)
        return True

    # ---------- Insert ----------

    def _insert_recursive(
        self, node: BPlusTreeNode, key: Any, value: Any
    ) -> Optional[Tuple[Any, BPlusTreeNode, BPlusTreeNode]]:
        if node.leaf:
            i = bisect_left(node.keys, key)
            if i < len(node.keys) and node.keys[i] == key:
                node.values[i] = value  # overwrite
                return None
            node.keys.insert(i, key)
            node.values.insert(i, value)

            if len(node.keys) <= self.max_keys:
                return None
            return self._split_leaf(node)

        # internal
        i = bisect_right(node.keys, key)
        promoted = self._insert_recursive(node.values[i], key, value)
        if promoted is None:
            return None

        k, left, right = promoted
        node.keys.insert(i, k)
        node.values[i] = left
        node.values.insert(i + 1, right)

        if len(node.keys) <= self.max_keys:
            return None
        return self._split_internal(node)

    def _split_leaf(
        self, leaf: BPlusTreeNode
    ) -> Tuple[Any, BPlusTreeNode, BPlusTreeNode]:
        right = BPlusTreeNode(leaf=True)
        mid = (len(leaf.keys) + 1) // 2  # right-biased split for leaf
        right.keys = leaf.keys[mid:]
        right.values = leaf.values[mid:]
        leaf.keys = leaf.keys[:mid]
        leaf.values = leaf.values[:mid]

        right.next = leaf.next
        leaf.next = right

        promoted_key = right.keys[0]
        return promoted_key, leaf, right

    def _split_internal(
        self, node: BPlusTreeNode
    ) -> Tuple[Any, BPlusTreeNode, BPlusTreeNode]:
        right = BPlusTreeNode(leaf=False)
        mid = len(node.keys) // 2

        promoted_key = node.keys[mid]
        right.keys = node.keys[mid + 1 :]
        right.values = node.values[mid + 1 :]

        node.keys = node.keys[:mid]
        node.values = node.values[: mid + 1]

        return promoted_key, node, right

    # ---------- Delete ----------

    def _delete_recursive(self, node: BPlusTreeNode, key: Any) -> bool:
        if node.leaf:
            i = bisect_left(node.keys, key)
            if i >= len(node.keys) or node.keys[i] != key:
                return False
            node.keys.pop(i)
            node.values.pop(i)
            return True

        # internal
        i = bisect_right(node.keys, key)
        child = node.values[i]
        deleted = self._delete_recursive(child, key)
        if not deleted:
            return False

        # If child underflows, rebalance
        self._fix_child_underflow(node, i)

        # Refresh separator keys around i
        self._refresh_separators(node)
        return True

    def _fix_child_underflow(self, parent: BPlusTreeNode, i: int) -> None:
        child = parent.values[i]
        if not self._is_underflow(child, is_root=(child is self.root)):
            return

        left_sib = parent.values[i - 1] if i - 1 >= 0 else None
        right_sib = parent.values[i + 1] if i + 1 < len(parent.values) else None

        # Try borrow from left
        if left_sib and self._can_lend(left_sib):
            if child.leaf:
                child.keys.insert(0, left_sib.keys.pop(-1))
                child.values.insert(0, left_sib.values.pop(-1))
                parent.keys[i - 1] = child.keys[0]
            else:
                # bring separator down, move left's last child
                child.keys.insert(0, parent.keys[i - 1])
                parent.keys[i - 1] = left_sib.keys.pop(-1)
                child.values.insert(0, left_sib.values.pop(-1))
            return

        # Try borrow from right
        if right_sib and self._can_lend(right_sib):
            if child.leaf:
                child.keys.append(right_sib.keys.pop(0))
                child.values.append(right_sib.values.pop(0))
                parent.keys[i] = right_sib.keys[0]
            else:
                child.keys.append(parent.keys[i])
                parent.keys[i] = right_sib.keys.pop(0)
                child.values.append(right_sib.values.pop(0))
            return

        # Merge
        if left_sib:
            self._merge_children(parent, i - 1)  # merge left and child
        elif right_sib:
            self._merge_children(parent, i)      # merge child and right

    def _merge_children(self, parent: BPlusTreeNode, left_index: int) -> None:
        left = parent.values[left_index]
        right = parent.values[left_index + 1]

        if left.leaf:
            left.keys.extend(right.keys)
            left.values.extend(right.values)
            left.next = right.next
        else:
            sep = parent.keys[left_index]
            left.keys.append(sep)
            left.keys.extend(right.keys)
            left.values.extend(right.values)

        parent.keys.pop(left_index)
        parent.values.pop(left_index + 1)

    # ---------- Helpers ----------

    def _find_leaf(self, key: Any) -> BPlusTreeNode:
        node = self.root
        while not node.leaf:
            i = bisect_right(node.keys, key)
            node = node.values[i]
        return node

    def _refresh_separators(self, node: BPlusTreeNode) -> None:
        if node.leaf:
            return
        # For B+ tree, internal key i should be min key of child i+1
        for j in range(len(node.keys)):
            node.keys[j] = self._leftmost_key(node.values[j + 1])

    def _leftmost_key(self, node: BPlusTreeNode) -> Any:
        cur = node
        while not cur.leaf:
            cur = cur.values[0]
        return cur.keys[0] if cur.keys else None

    def _is_underflow(self, node: BPlusTreeNode, is_root: bool = False) -> bool:
        if is_root:
            if node.leaf:
                return False
            return len(node.values) < 2

        if node.leaf:
            return len(node.keys) < self._min_leaf_keys()
        return len(node.keys) < self._min_internal_keys()

    def _can_lend(self, node: BPlusTreeNode) -> bool:
        if node.leaf:
            return len(node.keys) > self._min_leaf_keys()
        return len(node.keys) > self._min_internal_keys()

    def _min_internal_keys(self) -> int:
        # ceil(order/2) - 1
        return ((self.order + 1) // 2) - 1

    def _min_leaf_keys(self) -> int:
        # ceil((order-1)/2)
        return (self.max_keys + 1) // 2

    # Optional utility
    def scan(self) -> List[Tuple[Any, Any]]:
        out = []
        node = self.root
        while not node.leaf:
            node = node.values[0]
        while node:
            out.extend(zip(node.keys, node.values))
            node = node.next
        return out


if __name__ == "__main__":
    t = BPlusTree(order=4)
    for k in [10, 20, 5, 6, 12, 30, 7, 17]:
        t.insert(k, str(k))

    print("get(12) =", t.get(12))   # "12"
    print("get(99) =", t.get(99))   # None
    print("scan    =", t.scan())

    t.delete(6)
    t.delete(7)
    t.delete(5)
    print("after delete scan =", t.scan())