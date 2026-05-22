from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class Node:
    children: Dict[str, "Edge"] = field(default_factory=dict)
    suffix_index: int = -1  # >=0 for leaves


@dataclass
class Edge:
    start: int
    end: int
    dest: Node


class SuffixTree:
    """
    Naive O(n^2) suffix tree construction (compressed trie of all suffixes),
    suitable for learning and moderate input sizes.

    - Uses a unique terminal symbol ('$' by default) appended if absent.
    - Supports:
        * contains(pattern) -> bool
        * find_all(pattern) -> List[int]
        * count(pattern) -> int
    """

    def __init__(self, text: str, terminal: str = "$") -> None:
        if terminal in text:
            raise ValueError(
                f"Terminal symbol {terminal!r} already exists in text; "
                f"choose a different unique terminal."
            )
        self.terminal = terminal
        self.text = text + terminal
        self.n = len(self.text)
        self.root = Node()
        self._build()

    # ---------------- Build ----------------

    def _build(self) -> None:
        for i in range(self.n):
            self._insert_suffix(i)

    def _insert_suffix(self, suffix_start: int) -> None:
        cur = self.root
        i = suffix_start  # index in self.text for current suffix walk

        while i < self.n:
            ch = self.text[i]
            edge = cur.children.get(ch)

            if edge is None:
                # no edge starting with this char -> create a new leaf edge
                leaf = Node(suffix_index=suffix_start)
                cur.children[ch] = Edge(start=i, end=self.n - 1, dest=leaf)
                return

            # Walk along existing edge and find mismatch position
            e_start, e_end = edge.start, edge.end
            k = 0
            while e_start + k <= e_end and i + k < self.n and self.text[e_start + k] == self.text[i + k]:
                k += 1

            edge_len = e_end - e_start + 1

            if k == edge_len:
                # Entire edge matched; continue from child node
                cur = edge.dest
                i += k
                continue

            # Mismatch within edge -> split edge
            split_node = Node()

            # Existing tail edge (old continuation)
            old_tail_start = e_start + k
            old_tail_ch = self.text[old_tail_start]
            split_node.children[old_tail_ch] = Edge(
                start=old_tail_start,
                end=e_end,
                dest=edge.dest
            )

            # New tail edge (remaining suffix)
            new_tail_start = i + k
            new_leaf = Node(suffix_index=suffix_start)
            new_tail_ch = self.text[new_tail_start]
            split_node.children[new_tail_ch] = Edge(
                start=new_tail_start,
                end=self.n - 1,
                dest=new_leaf
            )

            # Replace original edge with prefix part to split node
            cur.children[ch] = Edge(
                start=e_start,
                end=e_start + k - 1,
                dest=split_node
            )
            return

        # If we ever exactly end at an internal node, mark as leaf-ish suffix end.
        # (Rare here due to terminal symbol uniqueness, but harmless.)
        if cur.suffix_index == -1:
            cur.suffix_index = suffix_start

    # ---------------- Query ----------------

    def contains(self, pattern: str) -> bool:
        return self._match_node(pattern) is not None

    def find_all(self, pattern: str) -> List[int]:
        """
        Return all start indices where pattern occurs in original text
        (excluding terminal-only artifacts).
        """
        res = self._match_node(pattern)
        if res is None:
            return []
        node, matched_edge, matched_len = res

        # If pattern ended in the middle of an edge, occurrences are in that edge's dest subtree.
        if matched_edge is not None:
            start_node = matched_edge.dest
        else:
            start_node = node

        out: List[int] = []
        self._collect_suffix_indices(start_node, out)

        # Filter out terminal-only suffix index if needed and sort
        original_len = self.n - 1
        out = [idx for idx in out if idx < original_len]
        out.sort()
        return out

    def count(self, pattern: str) -> int:
        return len(self.find_all(pattern))

    def _match_node(self, pattern: str) -> Optional[Tuple[Node, Optional[Edge], int]]:
        """
        Try matching pattern from root.
        Returns:
          (node, edge, consumed_on_edge)
          - if pattern ends at a node: edge=None
          - if pattern ends inside an edge: edge=that edge
        """
        cur = self.root
        i = 0
        m = len(pattern)

        if m == 0:
            return (self.root, None, 0)

        while i < m:
            ch = pattern[i]
            edge = cur.children.get(ch)
            if edge is None:
                return None

            e_start, e_end = edge.start, edge.end
            j = 0
            while e_start + j <= e_end and i + j < m:
                if self.text[e_start + j] != pattern[i + j]:
                    return None
                j += 1

            i += j
            edge_len = e_end - e_start + 1

            if i == m:
                # pattern fully matched; may end at node or inside edge
                if j == edge_len:
                    return (edge.dest, None, 0)
                return (cur, edge, j)

            if j < edge_len:
                # edge ended mismatch before pattern finished
                return None

            cur = edge.dest

        return (cur, None, 0)

    def _collect_suffix_indices(self, node: Node, out: List[int]) -> None:
        if node.suffix_index >= 0:
            out.append(node.suffix_index)
        for e in node.children.values():
            self._collect_suffix_indices(e.dest, out)

    # ---------------- Debug helpers ----------------

    def dump_edges(self) -> List[str]:
        """
        Return readable list of edges for debugging.
        Format: "parent_id -> child_id : text[start:end+1]"
        """
        lines: List[str] = []

        def dfs(n: Node) -> None:
            for e in n.children.values():
                label = self.text[e.start:e.end + 1]
                lines.append(f"{id(n)} -> {id(e.dest)} : {label!r}")
                dfs(e.dest)

        dfs(self.root)
        return lines
    

def main():
    text = "banana"
    st = SuffixTree(text)

    print(f"Text: {text!r}")
    patterns = ["ana", "na", "ban", "nana", "apple", "a", ""]

    for p in patterns:
        print(f"\nPattern: {p!r}")
        print("contains:", st.contains(p))
        print("count   :", st.count(p))
        print("find_all:", st.find_all(p))

    print("\nSome edges (debug):")
    for line in st.dump_edges()[:20]:
        print(line)


if __name__ == "__main__":
    main()