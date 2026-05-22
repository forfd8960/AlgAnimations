class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BinaryTree:
    def __init__(self):
        self.root = None

    def insert(self, value):
        """Insert value into tree (level-order for simplicity)."""
        new_node = Node(value)
        if not self.root:
            self.root = new_node
            return

        queue = [self.root]
        while queue:
            current = queue.pop(0)
            if not current.left:
                current.left = new_node
                return
            else:
                queue.append(current.left)

            if not current.right:
                current.right = new_node
                return
            else:
                queue.append(current.right)

    def inorder(self, node):
        """Left -> Root -> Right"""
        if node:
            self.inorder(node.left)
            print(node.value, end=" ")
            self.inorder(node.right)

    def preorder(self, node):
        """Root -> Left -> Right"""
        if node:
            print(node.value, end=" ")
            self.preorder(node.left)
            self.preorder(node.right)

    def postorder(self, node):
        """Left -> Right -> Root"""
        if node:
            self.postorder(node.left)
            self.postorder(node.right)
            print(node.value, end=" ")


# Example usage
if __name__ == "__main__":
    bt = BinaryTree()
    for v in [1, 2, 3, 4, 5, 6, 7]:
        bt.insert(v)

    print("Inorder:")
    bt.inorder(bt.root)      # 4 2 5 1 6 3 7
    print("\nPreorder:")
    bt.preorder(bt.root)     # 1 2 4 5 3 6 7
    print("\nPostorder:")
    bt.postorder(bt.root)    # 4 5 2 6 7 3 1