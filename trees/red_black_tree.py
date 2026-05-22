"""
1. The Core Rules
For a binary tree to qualify as a valid Red-Black Tree, it must respect these five constraints at all times:

Every node is either RED or BLACK.

The root node is always BLACK.

All empty leaf slots (represented as None or NIL pointers) are treated as BLACK.

If a node is RED, both of its children must be BLACK (No consecutive RED nodes allowed!).

Every path from a node to any of its descendant empty leaf slots must contain the exact same number of BLACK nodes.
"""

from enum import Enum

class Color(Enum):
    RED = 1
    BLACK = 2

class RBTNode:
    def __init__(self, key: int, color: Color = Color.RED):
        self.key = key
        self.color = color
        self.left = None
        self.right = None
        self.parent = None

class RedBlackTree:
    def __init__(self):
        # In a robust implementation, we use a single dedicated T.nil sentinel node 
        # to represent empty leaf slots. This simplifies boundary checks.
        self.NIL = RBTNode(key=0, color=Color.BLACK)
        self.root = self.NIL

    # --- Structural Rotations ---

    def _left_rotate(self, x: RBTNode) -> None:
        """Performs a structural left rotation around node 'x'."""
        y = x.right
        x.right = y.left
        
        if y.left != self.NIL:
            y.left.parent = x
            
        y.parent = x.parent
        
        if x.parent == None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
            
        y.left = x
        x.parent = y

    def _right_rotate(self, y: RBTNode) -> None:
        """Performs a structural right rotation around node 'y'."""
        x = y.left
        y.left = x.right
        
        if x.right != self.NIL:
            x.right.parent = y
            
        x.parent = y.parent
        
        if y.parent == None:
            self.root = x
        elif y == y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x
            
        x.right = y
        y.parent = x

    # --- Public Insertion API ---

    def insert(self, key: int) -> None:
        """Inserts a new key into the tree and triggers RBT correction."""
        new_node = RBTNode(key=key, color=Color.RED)  # New nodes always start out RED
        new_node.left = self.NIL
        new_node.right = self.NIL
        
        y = None
        x = self.root
        
        # Standard BST Insertion logic to find the slot
        while x != self.NIL:
            y = x
            if new_node.key < x.key:
                x = x.left
            elif new_node.key > x.key:
                x = x.right
            else:
                return # Duplicate keys ignored in this example

        new_node.parent = y
        
        if y == None:
            self.root = new_node
        elif new_node.key < y.key:
            y.left = new_node
        else:
            y.right = new_node
            
        # If the new node is the root, fix rule #2 immediately
        if new_node.parent == None:
            new_node.color = Color.BLACK
            return

        # If the parent is the root, it's black, meaning no rules are violated
        if new_node.parent.parent == None:
            return

        # Fix up the structural coloring rules
        self._fix_insert(new_node)

    # --- Fixing Color Rule Violations ---

    def _fix_insert(self, k: RBTNode) -> None:
        """Fixes consecutive RED node violations upward through the tree."""
        # Loop continues if there's a parent-child double-RED violation
        while k.parent.color == Color.RED:
            if k.parent == k.parent.parent.right:
                uncle = k.parent.parent.left
                
                # Case 1: Uncle is RED -> Recolor parent, uncle, and grandparent
                if uncle.color == Color.RED:
                    uncle.color = Color.BLACK
                    k.parent.color = Color.BLACK
                    k.parent.parent.color = Color.RED
                    k = k.parent.parent  # Move up to evaluate grandparent
                else:
                    # Case 2: Uncle is BLACK & node forms a triangle shape (RL)
                    if k == k.parent.left:
                        k = k.parent
                        self._right_rotate(k)
                    
                    # Case 3: Uncle is BLACK & node forms a straight line shape (RR)
                    k.parent.color = Color.BLACK
                    k.parent.parent.color = Color.RED
                    self._left_rotate(k.parent.parent)
            else:
                # Mirror logic for when parent is a left child
                uncle = k.parent.parent.right
                
                # Case 1 (Mirror)
                if uncle.color == Color.RED:
                    uncle.color = Color.BLACK
                    k.parent.color = Color.BLACK
                    k.parent.parent.color = Color.RED
                    k = k.parent.parent
                else:
                    # Case 2 (Mirror): Triangle shape (LR)
                    if k == k.parent.right:
                        k = k.parent
                        self._left_rotate(k)
                    
                    # Case 3 (Mirror): Straight line shape (LL)
                    k.parent.color = Color.BLACK
                    k.parent.parent.color = Color.RED
                    self._right_rotate(k.parent.parent)
                    
            if k == self.root:
                break
                
        # Rule 2 insurance: The root must remain black
        self.root.color = Color.BLACK

    # --- Utility Visualizer ---

    def debug_print(self, node: RBTNode, indent: str = "", last: bool = True) -> None:
        """Prints structural layouts along with node coloring information."""
        if node != self.NIL:
            print(indent, end="")
            if last:
                print("└── ", end="")
                indent += "    "
            else:
                print("├── ", end="")
                indent += "│   "
            
            color_str = "R" if node.color == Color.RED else "B"
            print(f"{node.key}({color_str})")
            self.debug_print(node.left, indent, False)
            self.debug_print(node.right, indent, True)