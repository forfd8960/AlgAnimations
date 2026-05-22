from __future__ import annotations

from bisect import bisect_left

from manim import *

from bstar_tree import BStarTree, Node


class BStarTreeAnim(Scene):
    def construct(self):
        pace = 1.2

        def t(seconds: float) -> float:
            return seconds * pace

        tree = BStarTree[int, int](max_keys=5)

        title = Text("B* Tree", font_size=48).to_edge(UP)
        self.play(Write(title))

        subtitle = self.make_subtitle_group(
            "B* tree keeps nodes highly occupied and rebalances on insert/delete."
        )
        self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=t(0.55))

        mode_text = Text("Insert", font_size=30).next_to(title, DOWN)
        info_text = Text("Demonstrating insert, search, delete", font_size=24).next_to(mode_text, DOWN)
        stats_group = self.make_stats_group(tree.max_keys, tree.min_keys, tree.target_min_keys)
        result_text = self.make_result_text("")
        self.play(FadeIn(mode_text), FadeIn(info_text), FadeIn(stats_group), FadeIn(result_text))

        tree_group, node_views = self.build_tree_group(tree)
        self.play(FadeIn(tree_group), run_time=t(0.75))

        insert_keys = [10, 20, 5, 6, 12, 30, 7, 17, 3, 4, 2, 8, 9, 11, 13, 14]
        for key in insert_keys:
            self.play(
                Transform(
                    subtitle,
                    self.make_subtitle_group(
                        f"insert({key}): descend to a target leaf, insert key, then split/rebalance if full."
                    ),
                ),
                run_time=t(0.4),
            )

            tree.insert(key, key)
            path_nodes = self.trace_path(tree.root, key)
            highlight_ids = {id(node) for node in path_nodes}

            new_tree_group, new_node_views = self.build_tree_group(tree, highlight_ids=highlight_ids)
            self.play(ReplacementTransform(tree_group, new_tree_group), run_time=t(0.9))
            tree_group = new_tree_group
            node_views = new_node_views

            for node in path_nodes:
                group = node_views.get(id(node))
                if group is not None:
                    self.play(Indicate(group, color=YELLOW), run_time=t(0.3))

            self.play(
                Transform(result_text, self.make_result_text(f"inserted {key}")),
                run_time=t(0.4),
            )
            self.wait(t(0.25))

        self.play(
            Transform(mode_text, Text("Search", font_size=30).next_to(title, DOWN)),
            Transform(info_text, Text("search(key): compare separators and descend", font_size=24).next_to(mode_text, DOWN)),
            Transform(result_text, self.make_result_text("")),
            Transform(
                subtitle,
                self.make_subtitle_group(
                    "Search follows separator keys to one leaf, then checks exact key match."
                ),
            ),
            run_time=t(0.55),
        )

        for key in [12, 99, 17, 4]:
            path_nodes = self.trace_path(tree.root, key)
            found_value = tree.search(key)
            hit = found_value is not None

            self.play(
                Transform(
                    subtitle,
                    self.make_subtitle_group(
                        f"search({key}): walk down one path and verify key in the final leaf."
                    ),
                ),
                run_time=t(0.35),
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
                    self.play(Indicate(group, color=TEAL if hit else RED), run_time=t(0.28))

            msg = f"search({key}) -> {found_value}" if hit else f"search({key}) -> None"
            self.play(Transform(result_text, self.make_result_text(msg)), run_time=t(0.4))
            self.wait(t(0.3))

        self.play(
            Transform(mode_text, Text("Delete", font_size=30).next_to(title, DOWN)),
            Transform(info_text, Text("delete(key): remove and fix underflow", font_size=24).next_to(mode_text, DOWN)),
            Transform(result_text, self.make_result_text("")),
            Transform(
                subtitle,
                self.make_subtitle_group(
                    "Delete may borrow from siblings or merge nodes to restore minimum occupancy."
                ),
            ),
            run_time=t(0.55),
        )

        delete_keys = [6, 20, 10, 2, 14]
        for key in delete_keys:
            path_before = self.trace_path(tree.root, key)
            deleted = tree.delete(key)
            path_after = self.trace_path(tree.root, key)

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
                        f"delete({key}): remove key, then rebalance by borrow or merge if needed."
                    ),
                ),
                run_time=t(0.35),
            )
            self.play(ReplacementTransform(tree_group, new_tree_group), run_time=t(0.9))
            tree_group = new_tree_group
            node_views = new_node_views

            for node in path_before:
                group = node_views.get(id(node))
                if group is not None:
                    self.play(Indicate(group, color=ORANGE if deleted else RED), run_time=t(0.28))

            msg = "deleted" if deleted else "not found"
            self.play(
                Transform(result_text, self.make_result_text(f"delete({key}) -> {msg}")),
                run_time=t(0.42),
            )
            self.wait(t(0.3))

        self.play(
            Transform(
                subtitle,
                self.make_subtitle_group(
                    "Done: insert builds structure, search finds path, and delete restores balance."
                ),
            ),
            run_time=t(0.5),
        )
        self.wait(t(1.0))

    def trace_path(self, root: Node[int, int], key: int):
        path = []
        node = root
        while node is not None:
            path.append(node)
            if node.leaf:
                break
            idx = bisect_left(node.keys, key)
            if idx < len(node.keys) and node.keys[idx] == key:
                idx += 1
            node = node.children[idx]
        return path

    def collect_structure(self, root: Node[int, int]):
        layout = {}
        ordered_leaves = []
        node_by_id = {}

        def dfs(node: Node[int, int], depth: int):
            node_id = id(node)
            node_by_id[node_id] = node

            if node.leaf:
                ordered_leaves.append(node_id)
                layout[node_id] = {"depth": depth, "children": []}
                return

            child_ids = []
            for child in node.children:
                child_id = id(child)
                child_ids.append(child_id)
                dfs(child, depth + 1)

            layout[node_id] = {"depth": depth, "children": child_ids}

        dfs(root, 0)
        return layout, ordered_leaves, node_by_id

    def assign_positions(self, root: Node[int, int]):
        layout, leaves, node_by_id = self.collect_structure(root)
        positions = {}

        if len(leaves) == 1:
            positions[leaves[0]] = (0.0, 0)
        else:
            left = -5.4
            right = 5.4
            step = (right - left) / max(1, len(leaves) - 1)
            for i, leaf_id in enumerate(leaves):
                positions[leaf_id] = (left + i * step, layout[leaf_id]["depth"])

        def assign_internal(node_id: int):
            node = node_by_id[node_id]
            if node.leaf:
                return positions[node_id][0]

            xs = [assign_internal(child_id) for child_id in layout[node_id]["children"]]
            x = sum(xs) / len(xs)
            positions[node_id] = (x, layout[node_id]["depth"])
            return x

        assign_internal(id(root))
        max_depth = max(meta["depth"] for meta in layout.values())
        return positions, layout, leaves, node_by_id, max_depth

    def node_width(self, node: Node[int, int]):
        key_count = max(1, len(node.keys))
        base = 0.82 if node.leaf else 0.75
        return base + key_count * 0.47

    def key_string(self, node: Node[int, int]):
        if not node.keys:
            return "-"
        return " | ".join(str(k) for k in node.keys)

    def build_tree_group(self, tree: BStarTree[int, int], highlight_ids=None, failed=False):
        highlight_ids = highlight_ids or set()
        positions, layout, _leaves, node_by_id, max_depth = self.assign_positions(tree.root)

        top_y = 1.55
        bottom_y = -2.0
        level_gap = (top_y - bottom_y) / max(1, max_depth)

        def y_of(depth: int):
            return top_y - depth * level_gap

        edges = VGroup()
        nodes = VGroup()
        node_views = {}

        for node_id, meta in layout.items():
            node = node_by_id[node_id]
            x, depth = positions[node_id]
            if node.leaf:
                continue
            for child_id in meta["children"]:
                cx, cdepth = positions[child_id]
                edge_color = RED_E if failed and child_id in highlight_ids else GRAY_B
                edges.add(Line([x, y_of(depth), 0], [cx, y_of(cdepth), 0], color=edge_color, stroke_width=3))

        for node_id, (x, depth) in positions.items():
            node = node_by_id[node_id]
            is_highlight = node_id in highlight_ids
            if failed and is_highlight:
                fill = RED_D
            elif is_highlight:
                fill = TEAL_D
            elif node.leaf:
                fill = GREEN_E
            else:
                fill = BLUE_E

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

            # Tiny marker helps viewers distinguish leaves from internal nodes.
            if node.leaf:
                marker = Dot(point=[-0.33, 0.16, 0], color=YELLOW_E, radius=0.035)
                group.add(marker)

            nodes.add(group)
            node_views[node_id] = group

        return VGroup(edges, nodes), node_views

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

    def make_stats_group(self, max_keys: int, min_keys: int, target_min_keys: int):
        lines = VGroup(
            Text(f"max keys: {max_keys}", font_size=20),
            Text(f"min keys: {min_keys}", font_size=20),
            Text(f"target min (B*): {target_min_keys}", font_size=20),
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
