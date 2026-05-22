import random
from typing import Tuple, Optional

class TreapNode:
    def __init__(self, key: int):
        self.key = key
        # Assign a random floating priority between 0 and 1
        self.priority = random.random()
        self.left = None
        self.right = None


class Treap:
    def __init__(self):
        self.root = None

    # --- Heap Balancing Rotations ---

    def _rotate_right(self, y: TreapNode) -> TreapNode:
        """
        Rotates the subtree to the right.
        Used when the left child has a higher priority than parent 'y'.
        """
        x = y.left
        T2 = x.right

        # Perform rotation
        x.right = y
        y.left = T2

        # Return new root of this subtree
        return x

    def _rotate_left(self, x: TreapNode) -> TreapNode:
        """
        Rotates the subtree to the left.
        Used when the right child has a higher priority than parent 'x'.
        """
        y = x.right
        T2 = y.left

        # Perform rotation
        y.left = x
        x.right = T2

        # Return new root of this subtree
        return y

    # --- Public API Methods ---
    def insert(self, key: int) -> None:
        """Inserts a key by splitting the tree, making a new node, and merging."""
        new_node = TreapNode(key)
        # Split the current tree at the target key value
        left, right = self.split(self.root, key)
        # Merge left side with the new single node, then merge back the right side
        self.root = self.merge(self.merge(left, new_node), right)

    def _insert(self, root: TreapNode, key: int) -> TreapNode:
        """Recursive helper for insertion."""
        # 1. Base Case: standard leaf position found
        if not root:
            return TreapNode(key)

        # 2. Traditional BST routing logic
        if key < root.key:
            root.left = self._insert(root.left, key)
            # Check Max-Heap property: if left child priority is higher, rotate right
            if root.left.priority > root.priority:
                root = self._rotate_right(root)
        elif key > root.key:
            root.right = self._insert(root.right, key)
            # Check Max-Heap property: if right child priority is higher, rotate left
            if root.right.priority > root.priority:
                root = self._rotate_left(root)
        
        return root

    def search(self, key: int) -> bool:
        """
        Searches for a key in the Treap.
        Because it tracks standard BST sorting rules, priority is completely ignored here.
        Time Complexity: O(log n) average.
        """
        current = self.root
        while current:
            if key == current.key:
                return True
            elif key < current.key:
                current = current.left
            else:
                current = current.right
        return False

    def split(self, root: Optional[TreapNode], x: int) -> Tuple[Optional[TreapNode], Optional[TreapNode]]:
        """
        Splits the treap rooted at 'root' into two treaps based on key 'x'.
        Returns a tuple: (left_treap, right_treap)
        Time Complexity: O(log n)
        """
        # Base case: an empty tree splits into two empty trees
        if not root:
            return None, None

        # If the current root's key is less than or equal to x,
        # then the root and its entire left subtree belong in the Left Treap.
        # We recursively split its right subtree.
        if root.key <= x:
            left_child, right_child = self.split(root.right, x)
            root.right = left_child
            return root, right_child
        
        # Otherwise, the root and its entire right subtree belong in the Right Treap.
        # We recursively split its left subtree.
        else:
            left_child, right_child = self.split(root.left, x)
            root.left = right_child
            return left_child, root

    def merge(self, left: Optional[TreapNode], right: Optional[TreapNode]) -> Optional[TreapNode]:
        """
        Merges two treaps 'left' and 'right' into a single valid Treap.
        Requirement: Max key in 'left' < Min key in 'right'.
        Time Complexity: O(log n)
        """
        # Base cases: if one side is empty, return the other side
        if not left or not right:
            return left or right

        # We must preserve the Max-Heap property based on randomized priority
        if left.priority > right.priority:
            # 'left' node wins the root spot. Its left subtree stays intact.
            # We recursively merge its right subtree with the 'right' treap.
            left.right = self.merge(left.right, right)
            return left
        else:
            # 'right' node wins the root spot. Its right subtree stays intact.
            # We recursively merge the 'left' treap with its left subtree.
            right.left = self.merge(left, right.left)
            return right

    def delete(self, key: int) -> None:
        """Deletes a key by isolating it via splits, dropping it, and merging."""
        # Split into elements < key, and elements >= key
        left, right = self.split(self.root, key - 1)
        # Split right side into elements == key, and elements > key
        middle, right = self.split(right, key)
        # By not doing anything with 'middle', the node is deleted.
        # Merge the outer remnants back together.
        self.root = self.merge(left, right)

    def inorder(self, root: Optional[TreapNode], res=None) -> list:
        if res is None: res = []
        if root:
            self.inorder(root.left, res)
            res.append(root.key)
            self.inorder(root.right, res)
        return res

    # --- Debug Printing Visualization ---

    def display(self, root: TreapNode, indent: str = "", last: bool = True) -> None:
        """Prints a visual layout mapping out keys and priorities."""
        if root:
            print(indent, end="")
            if last:
                print("└── ", end="")
                indent += "    "
            else:
                print("├── ", end="")
                indent += "│   "
            
            print(f"Key: {root.key} [P: {root.priority:.3f}]")
            self.display(root.left, indent, False)
            self.display(root.right, indent, True)



if __name__ == '__main__':
    treap = Treap()
    for val in [10, 20, 30, 40, 50]:
        treap.insert(val)
        print("Original Treap Elements:", treap.inorder(treap.root))
        # Output: [10, 20, 30, 40, 50]

        # Split the tree at key 30
        left_tree, right_tree = treap.split(treap.root, 30)

        print("Left Tree (<= 30):", treap.inorder(left_tree))
        # Output: [10, 20, 30]

        print("Right Tree (> 30):", treap.inorder(right_tree))
        # Output: [40, 50]

        # Merge them back together
        treap.root = treap.merge(left_tree, right_tree)
        print("Re-merged Treap Elements:", treap.inorder(treap.root))
        # Output: [10, 20, 30, 40, 50]