from __future__ import annotations

from manim import *

from radix_tree import RadixTree, _Node, _lcp
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


class RadixTreeAnim(Scene):
    def construct(self):
        self.camera.background_color = BG_DARK
        self.subtitle_font = SUBTITLE_FONT

        pace = 1.15

        def t(seconds: float) -> float:
            return seconds * pace

        tree = RadixTree[int]()

        title = Text("Radix Tree", font_size=46, color=NODE_ACTIVE).to_edge(UP)
        self.play(Write(title))

        subtitle = self.make_subtitle_group(
            "Radix tree compresses chains of single-child nodes into labeled edges."
        )
        self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=t(0.55))

        mode_text = Text("Insert", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)
        info_text = Text(
            "insert(key, value): split edge when only part of the label matches",
            font_size=24,
            color=TEXT_MUTED,
        ).next_to(mode_text, DOWN)
        result_text = self.make_result_text("")
        self.play(FadeIn(mode_text), FadeIn(info_text), FadeIn(result_text))

        tree_group, node_views = self.build_tree_group(tree)
        self.play(FadeIn(tree_group), run_time=t(0.8))

        words = [
            "car", "card", "care", "careful", "cargo",
            "cat", "cater", "dog", "dove"
        ]

        for i, word in enumerate(words, start=1):
            self.play(
                Transform(
                    subtitle,
                    self.make_subtitle_group(
                        f"insert({word!r}, {i}): follow common prefix and split edge when only part matches."
                    ),
                ),
                run_time=t(0.45),
            )

            tree.insert(word, i)
            path_ids = self.trace_key_path(tree, word)
            highlight_ids = set(path_ids)

            new_tree_group, new_node_views = self.build_tree_group(tree, highlight_ids=highlight_ids)
            self.play(ReplacementTransform(tree_group, new_tree_group), run_time=t(0.95))
            tree_group = new_tree_group
            node_views = new_node_views

            for nid in path_ids:
                group = node_views.get(nid)
                if group is not None:
                    self.play(Indicate(group, color=EDGE_ACTIVE), run_time=t(0.28))

            self.play(
                Transform(result_text, self.make_result_text(f"size={len(tree)}")),
                run_time=t(0.35),
            )
            self.wait(t(0.2))

        self.play(
            Transform(mode_text, Text("Search", font_size=30).next_to(title, DOWN)),
            Transform(info_text, Text("search(key): traverse by first char and full edge match", font_size=24).next_to(mode_text, DOWN)),
            Transform(result_text, self.make_result_text("")),
            Transform(
                subtitle,
                self.make_subtitle_group(
                    "Search succeeds only when each traversed edge label fully matches the remaining suffix."
                ),
            ),
            run_time=t(0.55),
        )

        tests = ["car", "care", "cater", "can", "doge", "dove"]
        for word in tests:
            path_ids = self.trace_key_path(tree, word)
            val = tree.search(word)
            hit = val is not None

            self.play(
                Transform(
                    subtitle,
                    self.make_subtitle_group(
                        f"search({word!r}): walk compressed edges by longest common prefix checks."
                    ),
                ),
                run_time=t(0.38),
            )

            new_tree_group, new_node_views = self.build_tree_group(
                tree,
                highlight_ids=set(path_ids),
                failed=not hit,
            )
            self.play(ReplacementTransform(tree_group, new_tree_group), run_time=t(0.8))
            tree_group = new_tree_group
            node_views = new_node_views

            for nid in path_ids:
                group = node_views.get(nid)
                if group is not None:
                    self.play(Indicate(group, color=NODE_ACTIVE if hit else RED), run_time=t(0.25))

            self.play(
                Transform(result_text, self.make_result_text(f"search({word!r}) -> {val}")),
                run_time=t(0.4),
            )
            self.wait(t(0.25))

        self.play(
            Transform(mode_text, Text("Delete", font_size=30).next_to(title, DOWN)),
            Transform(info_text, Text("delete(key): remove terminal mark, then compress", font_size=24).next_to(mode_text, DOWN)),
            Transform(result_text, self.make_result_text("")),
            Transform(
                subtitle,
                self.make_subtitle_group(
                    "After deletion, radix tree removes empty leaves and compresses unary non-terminal nodes."
                ),
            ),
            run_time=t(0.55),
        )

        to_delete = ["care", "cat", "dog", "not-there"]
        for word in to_delete:
            path_before = self.trace_key_path(tree, word)
            deleted = tree.delete(word)
            path_after = self.trace_key_path(tree, word)
            highlight_ids = set(path_before + path_after)

            self.play(
                Transform(
                    subtitle,
                    self.make_subtitle_group(
                        f"delete({word!r}): clear terminal node and compress if a single-child chain remains."
                    ),
                ),
                run_time=t(0.35),
            )

            new_tree_group, new_node_views = self.build_tree_group(
                tree,
                highlight_ids=highlight_ids,
                failed=not deleted,
            )
            self.play(ReplacementTransform(tree_group, new_tree_group), run_time=t(0.9))
            tree_group = new_tree_group
            node_views = new_node_views

            for nid in path_before:
                group = node_views.get(nid)
                if group is not None:
                    self.play(Indicate(group, color=EDGE_ACTIVE if deleted else RED), run_time=t(0.25))

            self.play(
                Transform(result_text, self.make_result_text(f"delete({word!r}) -> {deleted}; size={len(tree)}")),
                run_time=t(0.42),
            )
            self.wait(t(0.28))

        self.play(
            Transform(
                subtitle,
                self.make_subtitle_group(
                    "Done: insert splits edges, search matches labels, delete cleans and compresses paths."
                ),
            ),
            run_time=t(0.5),
        )
        self.wait(t(1.0))

    def trace_key_path(self, tree: RadixTree[int], key: str):
        cur = tree.root
        rest = key
        path = [id(cur)]

        while rest:
            child = cur.children.get(rest[0])
            if child is None:
                break

            common = _lcp(child.label, rest)
            path.append(id(child))

            if common != len(child.label):
                break

            rest = rest[common:]
            cur = child

        return path

    def collect_structure(self, root: _Node[int]):
        layout = {}
        leaves = []
        node_by_id = {}

        def dfs(node: _Node[int], depth: int):
            node_id = id(node)
            node_by_id[node_id] = node
            child_ids = []
            for child in sorted(node.children.values(), key=lambda n: n.label):
                cid = id(child)
                child_ids.append(cid)
                dfs(child, depth + 1)

            layout[node_id] = {"depth": depth, "children": child_ids}
            if len(child_ids) == 0:
                leaves.append(node_id)

        dfs(root, 0)
        return layout, leaves, node_by_id

    def assign_positions(self, root: _Node[int]):
        layout, leaves, node_by_id = self.collect_structure(root)
        positions = {}

        if len(leaves) == 1:
            positions[leaves[0]] = (0.0, 0)
        else:
            left = -5.7
            right = 5.7
            step = (right - left) / max(1, len(leaves) - 1)
            for i, leaf_id in enumerate(leaves):
                positions[leaf_id] = (left + i * step, layout[leaf_id]["depth"])

        def place(node_id: int):
            children = layout[node_id]["children"]
            if not children:
                return positions[node_id][0]

            child_xs = [place(cid) for cid in children]
            x = sum(child_xs) / len(child_xs)
            positions[node_id] = (x, layout[node_id]["depth"])
            return x

        place(id(root))
        max_depth = max(meta["depth"] for meta in layout.values())
        return positions, layout, node_by_id, max_depth

    def build_tree_group(self, tree: RadixTree[int], highlight_ids=None, failed=False):
        highlight_ids = highlight_ids or set()
        positions, layout, node_by_id, max_depth = self.assign_positions(tree.root)

        top_y = 1.6
        bottom_y = -2.0
        level_gap = (top_y - bottom_y) / max(1, max_depth)

        def y_of(depth: int):
            return top_y - depth * level_gap

        edges = VGroup()
        edge_labels = VGroup()
        nodes = VGroup()
        node_views = {}

        for node_id, meta in layout.items():
            x, depth = positions[node_id]
            for child_id in meta["children"]:
                cx, cdepth = positions[child_id]
                child = node_by_id[child_id]

                edge_color = RED_D if failed and child_id in highlight_ids else TEXT_MUTED
                line = Line([x, y_of(depth), 0], [cx, y_of(cdepth), 0], color=edge_color, stroke_width=3)
                edges.add(line)

                label = Text(child.label, font_size=18, color=WHITE)
                label_bg = RoundedRectangle(
                    corner_radius=0.06,
                    width=min(label.width + 0.2, 2.2),
                    height=label.height + 0.12,
                    stroke_width=0,
                )
                label_bg.set_fill(BLACK, opacity=0.75)
                if label.width > 2.0:
                    label.scale_to_fit_width(2.0)
                label.move_to(label_bg.get_center())
                edge_tag = VGroup(label_bg, label)
                edge_tag.move_to((line.get_start() + line.get_end()) / 2 + DOWN * 0.05)
                edge_labels.add(edge_tag)

        for node_id, (x, depth) in positions.items():
            node = node_by_id[node_id]
            is_root = node is tree.root
            is_highlight = node_id in highlight_ids

            if failed and is_highlight:
                fill = RED_D
            elif is_highlight:
                fill = NODE_ACTIVE
            elif node.is_terminal:
                fill = NODE_LEAF
            else:
                fill = NODE_NEUTRAL

            radius = 0.24 if is_root else 0.2
            circle = Circle(radius=radius, color=WHITE, stroke_width=2)
            circle.set_fill(fill, opacity=1.0)

            text = "*" if is_root else ""
            label = Text(text, font_size=18).move_to(ORIGIN)

            group = VGroup(circle, label).move_to([x, y_of(depth), 0])

            if node.is_terminal and not is_root:
                terminal_dot = Dot(point=[0.13, 0.13, 0], radius=0.038, color=EDGE_ACTIVE)
                group.add(terminal_dot)

            nodes.add(group)
            node_views[node_id] = group

        return VGroup(edges, edge_labels, nodes), node_views

    def make_subtitle_group(self, content):
        text = Text(content, font_size=23)
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
        max_width = config.frame_width * 0.45
        if text.width > max_width:
            text.scale_to_fit_width(max_width)
        text.to_corner(UR).shift(LEFT * 0.35 + DOWN * 1.2)
        return text
