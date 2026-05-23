from __future__ import annotations

from bisect import bisect_right

from manim import *

from btree import BPlusTree, BPlusTreeNode
try:
    from common.color import (
        BG_DARK,
        EDGE_ACTIVE,
        NODE_ACTIVE,
        NODE_LEAF,
        NODE_NEUTRAL,
        SUBTITLE_FONT,
        TEXT_MUTED,
    )
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from common.color import (
        BG_DARK,
        EDGE_ACTIVE,
        NODE_ACTIVE,
        NODE_LEAF,
        NODE_NEUTRAL,
        SUBTITLE_FONT,
        TEXT_MUTED,
    )


class BPlusTreeAnim(Scene):
    def construct(self):
        self.camera.background_color = BG_DARK
        self.subtitle_font = SUBTITLE_FONT

        pace = 1.25

        def t(seconds: float) -> float:
            return seconds * pace

        title = Text("B+ Tree", font_size=48, color=NODE_ACTIVE).to_edge(UP)
        self.play(Write(title))

        subtitle = self.make_subtitle_group(
            "A B+ tree keeps all records in leaves and links leaves for fast range scans."
        )
        self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=t(0.6))

        tree = BPlusTree(order=4)
        min_leaf_keys = (tree.max_keys + 1) // 2
        min_internal_keys = ((tree.order + 1) // 2) - 1

        mode_text = Text("Insert", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)
        info_text = Text("order=4 (max 3 keys per node)", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN)
        stats_group = self.make_stats_group(
            tree.order,
            tree.max_keys,
            min_leaf_keys,
            min_internal_keys,
        )
        result_text = self.make_result_text("")
        self.play(FadeIn(mode_text), FadeIn(info_text), FadeIn(stats_group), FadeIn(result_text))

        tree_group, node_views = self.build_tree_group(tree)
        self.play(FadeIn(tree_group), run_time=t(0.8))

        insert_keys = [10, 20, 5, 6, 12, 30, 7, 17, 3, 4, 2, 8, 9, 11, 13, 14]
        for key in insert_keys:
            self.play(
                Transform(
                    subtitle,
                    self.make_subtitle_group(
                        f"insert({key}): descend to a leaf, insert key, and split upward if needed."
                    ),
                ),
                run_time=t(0.45),
            )

            tree.insert(key, f"v{key}")
            path_nodes = self.trace_path(tree.root, key)
            highlight_ids = {id(node) for node in path_nodes}

            new_tree_group, new_node_views = self.build_tree_group(tree, highlight_ids=highlight_ids)
            self.play(ReplacementTransform(tree_group, new_tree_group), run_time=t(0.9))
            tree_group = new_tree_group
            node_views = new_node_views

            for node in path_nodes:
                group = node_views.get(id(node))
                if group is not None:
                    self.play(Indicate(group, color=EDGE_ACTIVE), run_time=t(0.35))

            self.play(
                Transform(result_text, self.make_result_text(f"scan: {self.format_scan(tree.scan())}")),
                run_time=t(0.45),
            )
            self.wait(t(0.35))

        self.play(
            Transform(mode_text, Text("Get", font_size=30).next_to(title, DOWN)),
            Transform(info_text, Text("get(key): follow separators to one leaf", font_size=24).next_to(mode_text, DOWN)),
            Transform(result_text, self.make_result_text("")),
            Transform(
                subtitle,
                self.make_subtitle_group(
                    "Point lookup uses internal separators to locate one target leaf."
                ),
            ),
            run_time=t(0.6),
        )

        for key in [12, 99, 17]:
            path_nodes = self.trace_path(tree.root, key)
            found_value = tree.get(key)
            hit = found_value is not None

            self.play(
                Transform(
                    subtitle,
                    self.make_subtitle_group(
                        f"get({key}): walk root-to-leaf and check whether key exists in that leaf."
                    ),
                ),
                run_time=t(0.4),
            )

            highlight_ids = {id(node) for node in path_nodes}
            new_tree_group, new_node_views = self.build_tree_group(
                tree,
                highlight_ids=highlight_ids,
                failed=not hit,
            )
            self.play(ReplacementTransform(tree_group, new_tree_group), run_time=t(0.75))
            tree_group = new_tree_group
            node_views = new_node_views

            for node in path_nodes:
                group = node_views.get(id(node))
                if group is not None:
                    self.play(Indicate(group, color=NODE_ACTIVE if hit else RED), run_time=t(0.3))

            msg = f"get({key}) -> {found_value}" if hit else f"get({key}) -> None"
            self.play(Transform(result_text, self.make_result_text(msg)), run_time=t(0.45))
            self.wait(t(0.4))

        self.play(
            Transform(mode_text, Text("Delete", font_size=30).next_to(title, DOWN)),
            Transform(info_text, Text("delete(key): remove from leaf, then rebalance", font_size=24).next_to(mode_text, DOWN)),
            Transform(result_text, self.make_result_text("")),
            Transform(
                subtitle,
                self.make_subtitle_group(
                    "Deletion may trigger borrow/merge and separator refresh to keep the tree balanced."
                ),
            ),
            run_time=t(0.6),
        )

        for key in [6, 7, 5, 20]:
            path_before = self.trace_path(tree.root, key)
            deleted = tree.delete(key)
            path_after = self.trace_path(tree.root, key) if tree.root else []

            highlight_ids = {id(node) for node in path_before + path_after}
            new_tree_group, new_node_views = self.build_tree_group(
                tree,
                highlight_ids=highlight_ids,
                failed=not deleted,
            )

            self.play(
                Transform(
                    subtitle,
                    self.make_subtitle_group(
                        f"delete({key}): remove key from leaf, then fix underflow by borrow or merge."
                    ),
                ),
                run_time=t(0.4),
            )
            self.play(ReplacementTransform(tree_group, new_tree_group), run_time=t(0.9))
            tree_group = new_tree_group
            node_views = new_node_views

            for node in path_before:
                group = node_views.get(id(node))
                if group is not None:
                    self.play(Indicate(group, color=EDGE_ACTIVE if deleted else RED), run_time=t(0.28))

            msg = "deleted" if deleted else "not found"
            self.play(
                Transform(
                    result_text,
                    self.make_result_text(f"delete({key}) -> {msg}"),
                ),
                run_time=t(0.5),
            )
            self.wait(t(0.4))

        self.play(
            Transform(
                subtitle,
                self.make_subtitle_group(
                    "Done: insert builds levels, get follows separators, and delete rebalances the B+ tree."
                ),
            ),
            run_time=t(0.5),
        )
        self.wait(t(1.2))

    def trace_path(self, root: BPlusTreeNode, key: int):
        path = []
        node = root
        while node is not None:
            path.append(node)
            if node.leaf:
                break
            idx = bisect_right(node.keys, key)
            node = node.values[idx]
        return path

    def collect_structure(self, root: BPlusTreeNode):
        layout = {}
        ordered_leaves = []

        def dfs(node: BPlusTreeNode, depth: int):
            if node.leaf:
                ordered_leaves.append(node)
                layout[node] = {"depth": depth, "children": []}
                return

            children = list(node.values)
            layout[node] = {"depth": depth, "children": children}
            for child in children:
                dfs(child, depth + 1)

        dfs(root, 0)
        return layout, ordered_leaves

    def assign_positions(self, root: BPlusTreeNode):
        layout, leaves = self.collect_structure(root)
        positions = {}

        if len(leaves) == 1:
            positions[leaves[0]] = (0.0, 0)
        else:
            left = -5.4
            right = 5.4
            step = (right - left) / max(1, len(leaves) - 1)
            for i, leaf in enumerate(leaves):
                positions[leaf] = (left + i * step, layout[leaf]["depth"])

        def assign_internal(node: BPlusTreeNode):
            if node.leaf:
                return positions[node][0]

            xs = [assign_internal(child) for child in layout[node]["children"]]
            x = sum(xs) / len(xs)
            positions[node] = (x, layout[node]["depth"])
            return x

        assign_internal(root)
        max_depth = max(meta["depth"] for meta in layout.values())
        return positions, layout, leaves, max_depth

    def node_width(self, node: BPlusTreeNode):
        key_count = max(1, len(node.keys))
        base = 0.8 if node.leaf else 0.75
        return base + key_count * 0.5

    def key_string(self, node: BPlusTreeNode):
        if not node.keys:
            return "-"
        return " | ".join("None" if k is None else str(k) for k in node.keys)

    def build_tree_group(self, tree: BPlusTree, highlight_ids=None, failed=False):
        highlight_ids = highlight_ids or set()
        positions, layout, leaves, max_depth = self.assign_positions(tree.root)

        top_y = 1.6
        bottom_y = -2.0
        level_gap = (top_y - bottom_y) / max(1, max_depth)

        def y_of(depth: int):
            return top_y - depth * level_gap

        edges = VGroup()
        nodes = VGroup()
        leaf_links = VGroup()
        node_views = {}

        for node, meta in layout.items():
            x, depth = positions[node]
            if node.leaf:
                continue
            for child in meta["children"]:
                cx, cdepth = positions[child]
                edge_color = RED_D if failed and id(child) in highlight_ids else TEXT_MUTED
                edge = Line([x, y_of(depth), 0], [cx, y_of(cdepth), 0], color=edge_color, stroke_width=3)
                edges.add(edge)

        for i in range(len(leaves) - 1):
            left_leaf = leaves[i]
            right_leaf = leaves[i + 1]
            lx, ldepth = positions[left_leaf]
            rx, rdepth = positions[right_leaf]
            y = y_of(max(ldepth, rdepth)) - 0.35
            link = DashedLine([lx + 0.4, y, 0], [rx - 0.4, y, 0], dash_length=0.12, color=EDGE_ACTIVE)
            leaf_links.add(link)

        for node, (x, depth) in positions.items():
            is_highlight = id(node) in highlight_ids
            if failed and is_highlight:
                fill = RED_D
            elif is_highlight:
                fill = NODE_ACTIVE
            elif node.leaf:
                fill = NODE_LEAF
            else:
                fill = NODE_NEUTRAL

            rect = RoundedRectangle(
                corner_radius=0.1,
                width=self.node_width(node),
                height=0.55,
                stroke_color=WHITE,
                stroke_width=2,
            )
            rect.set_fill(fill, opacity=1.0)

            label = Text(self.key_string(node), font_size=20).move_to(rect.get_center())
            group = VGroup(rect, label).move_to([x, y_of(depth), 0])
            nodes.add(group)
            node_views[id(node)] = group

        leaf_caption = Text("leaf links", font_size=18, color=EDGE_ACTIVE)
        if len(leaves) >= 2:
            first_leaf = leaves[0]
            fx, fdepth = positions[first_leaf]
            leaf_caption.move_to([fx - 1.0, y_of(fdepth) - 0.55, 0])
            leaf_links.add(leaf_caption)

        return VGroup(edges, leaf_links, nodes), node_views

    def format_scan(self, items):
        keys = [k for k, _ in items]
        return str(keys)

    def make_subtitle_group(self, content):
        text = Text(content, font_size=24)
        max_width = config.frame_width - 1.2
        if text.width > max_width:
            text.scale_to_fit_width(max_width)

        bg = RoundedRectangle(
            corner_radius=0.12,
            width=min(text.width + 0.7, config.frame_width - 0.4),
            height=text.height + 0.35,
            stroke_width=0,
        )
        bg.set_fill(BLACK, opacity=0.72)

        text.move_to(bg.get_center())
        subtitle = VGroup(bg, text)
        subtitle.to_edge(DOWN, buff=0.2)
        return subtitle

    def make_result_text(self, content):
        text = Text(content, font_size=22)
        max_width = config.frame_width * 0.5
        if text.width > max_width:
            text.scale_to_fit_width(max_width)
        text.to_corner(UR).shift(LEFT * 0.3 + DOWN * 1.15)
        return text

    def make_stats_group(self, order, max_keys, min_leaf_keys, min_internal_keys):
        lines = VGroup(
            Text(f"order: {order}", font_size=20),
            Text(f"max keys: {max_keys}", font_size=20),
            Text(f"min leaf keys: {min_leaf_keys}", font_size=20),
            Text(f"min internal keys: {min_internal_keys}", font_size=20),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.07)

        bg = RoundedRectangle(
            corner_radius=0.08,
            width=lines.width + 0.35,
            height=lines.height + 0.28,
            stroke_color=GRAY_B,
            stroke_width=1.5,
        )
        bg.set_fill(BLACK, opacity=0.65)

        lines.move_to(bg.get_center())
        panel = VGroup(bg, lines)
        panel.to_corner(UL).shift(RIGHT * 0.28 + DOWN * 0.72)
        return panel
