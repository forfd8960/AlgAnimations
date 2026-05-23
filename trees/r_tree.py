import math

class Rectangle:
    """Represents a 2D bounding box (Minimum Bounding Box)."""
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

    def intersects(self, other):
        """Checks if this rectangle overlaps with another."""
        return not (self.x_max < other.x_min or self.x_min > other.x_max or
                    self.y_max < other.y_min or self.y_min > other.y_max)

    def area(self):
        """Calculates the area of the rectangle."""
        return max(0, self.x_max - self.x_min) * max(0, self.y_max - self.y_min)

    @staticmethod
    def merged(r1, r2):
        """Returns a new bounding box that perfectly encloses both r1 and r2."""
        return Rectangle(
            min(r1.x_min, r2.x_min),
            min(r1.y_min, r2.y_min),
            max(r1.x_max, r2.x_max),
            max(r1.y_max, r2.y_max)
        )


class RTreeNode:
    """A node inside the R-Tree. Can be a leaf or an internal node."""
    def __init__(self, is_leaf=True, max_entries=4):
        self.is_leaf = is_leaf
        self.max_entries = max_entries
        self.entries = []  # Holds tuples of (Rectangle, data/child_node)
        self.mbb = None    # Bounding box enclosing all entries inside this node

    def update_mbb(self):
        """Recalculates the Minimum Bounding Box for this entire node."""
        if not self.entries:
            self.mbb = None
            return
        current_mbb = self.entries[0][0]
        for box, _ in self.entries[1:]:
            current_mbb = Rectangle.merged(current_mbb, box)
        self.mbb = current_mbb


class RTree:
    """The R-Tree Spatial Index."""
    def __init__(self, max_entries=4):
        self.max_entries = max_entries
        self.root = RTreeNode(is_leaf=True, max_entries=self.max_entries)

    def insert(self, rect, data):
        """Inserts a spatial object into the tree."""
        split_node = self._insert(self.root, rect, data)
        
        # If the root split, we must create a new root, growing the tree upwards
        if split_node:
            new_root = RTreeNode(is_leaf=False, max_entries=self.max_entries)
            new_root.entries.append((self.root.mbb, self.root))
            new_root.entries.append((split_node.mbb, split_node))
            new_root.update_mbb()
            self.root = new_root

    def _insert(self, node, rect, data):
        """Recursive insertion helper."""
        if node.is_leaf:
            node.entries.append((rect, data))
            node.update_mbb()
            if len(node.entries) > node.max_entries:
                return self._split_node(node)
            return None
        else:
            # Internal node: Choose the subtree that requires the least area enlargement
            best_idx = 0
            min_enlargement = float('inf')
            
            for i, (box, _) in enumerate(node.entries):
                enlarged_area = Rectangle.merged(box, rect).area()
                enlargement = enlarged_area - box.area()
                if enlargement < min_enlargement:
                    min_enlargement = enlargement
                    best_idx = i
            
            # Recurse down into the best child subtree
            child_node = node.entries[best_idx][1]
            split_child = self._insert(child_node, rect, data)
            
            # Update the bounding box pointer for the path we took down
            node.entries[best_idx] = (child_node.mbb, child_node)
            node.update_mbb()
            
            # If the child node split, handle the new split node entry here
            if split_child:
                node.entries.append((split_child.mbb, split_child))
                node.update_mbb()
                if len(node.entries) > node.max_entries:
                    return self._split_node(node)
            return None

    def _split_node(self, node):
        """A simplified linear/quadratic split heuristic to divide full nodes."""
        # Sort along the X axis as a simple heuristic to distribute items evenly
        node.entries.sort(key=lambda item: item[0].x_min)
        mid = len(node.entries) // 2
        
        # Keep the first half in the original node, move the rest to a sibling node
        sibling = RTreeNode(is_leaf=node.is_leaf, max_entries=self.max_entries)
        sibling.entries = node.entries[mid:]
        node.entries = node.entries[:mid]
        
        # Re-evaluate the bounding envelopes for both nodes
        node.update_mbb()
        sibling.update_mbb()
        return sibling

    def search(self, query_rect):
        """Finds all data objects overlapping with the query area."""
        results = []
        self._search(self.root, query_rect, results)
        return results

    def _search(self, node, query_rect, results):
        """Recursive search helper."""
        if node.mbb is None or not node.mbb.intersects(query_rect):
            return  # Prune search path entirely if it doesn't intersect the node's MBB
        
        for box, item in node.entries:
            if box.intersects(query_rect):
                if node.is_leaf:
                    results.append(item)
                else:
                    self._search(item, query_rect, results)
                    
                    
                    
if __name__ == "__main__":
    # Initialize our geographic index
    spatial_index = RTree(max_entries=4)

    # 1. Populate the tree with data (Points/Rectangles representing properties)
    # Format: Rectangle(x_min, y_min, x_max, y_max), "Name/Data"
    spatial_index.insert(Rectangle(1, 1, 2, 2), "Downtown Coffee Shop")
    spatial_index.insert(Rectangle(5, 5, 6, 6), "Suburban Gas Station")
    spatial_index.insert(Rectangle(2, 1, 3, 2), "Central Park Pizzeria")
    spatial_index.insert(Rectangle(10, 12, 11, 13), "Airport Terminal")

    # 2. Define a map viewing area (Query window)
    # Looking for anything in the box bounded by X(0 to 4) and Y(0 to 3)
    map_view_window = Rectangle(0, 0, 4, 3)
    found_places = spatial_index.search(map_view_window)

    print(f"Places visible in map view: {found_places}")
    # Output: Places visible in map view: ['Downtown Coffee Shop', 'Central Park Pizzeria']