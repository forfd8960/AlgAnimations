from __future__ import annotations

from manim import *

from red_black_tree import Color, EXAMPLE_INSERT_KEYS, RBTNode, RedBlackTree

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


RED_NODE = "#D64B4B"
BLACK_NODE = NODE_NEUTRAL


class RedBlackTreeAnim(Scene):
    def construct(self):
        self.camera.background_color = BG_DARK
        self.subtitle_font = SUBTITLE_FONT

        pace = 1.12

        def t(seconds: float) -> float:
            return seconds * pace

        tree = RedBlackTree()

        title = Text("Red-Black Tree", font_size=46, color=NODE_ACTIVE).to_edge(UP)
        self.play(Write(title))

        subtitle = self.make_subtitle_group(
            "Insertions preserve balance using recoloring and rotations."
        )
        self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=t(0.55))

        mode_text = Text("Insert Demo", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)
        info_text = Text(
            f"main() keys: {EXAMPLE_INSERT_KEYS}",
            font_size=22,
            color=TEXT_MUTED,
        ).next_to(mode_text, DOWN)
        result_text = self.make_result_text("")
        legend = self.make_legend().to_corner(UL).shift(RIGHT * 0.3 + DOWN * 0.75)

        self.play(FadeIn(mode_text), FadeIn(info_text), FadeIn(result_text), FadeIn(legend))

        tree_group, node_views = self.build_tree_group(tree)
        self.play(FadeIn(tree_group), run_time=t(0.8))

        for key in EXAMPLE_INSERT_KEYS:
            path_keys = self.trace_insert_path(tree, key)
            if path_keys:
                pre_group, pre_views = self.build_tree_group(tree, path_keys=set(path_keys))
                self.play(ReplacementTransform(tree_group, pre_group), run_time=t(0.55))
                tree_group = pre_group
                node_views = pre_views
                for node_key in path_keys:
                    node_group = node_views.get(node_key)
                    if node_group is not None:
                        self.play(Indicate(node_group, color=EDGE_ACTIVE), run_time=t(0.23))

            self.play(
                Transform(
                    subtitle,
                    self.make_subtitle_group(
                        f"insert({key}): add as BST node, then fix red-red violations upward."
                    ),
                ),
                run_time=t(0.35),
            )

            tree.insert(key)

            post_group, post_views = self.build_tree_group(tree, active_key=key)
            self.play(ReplacementTransform(tree_group, post_group), run_time=t(0.95))
            tree_group = post_group
            node_views = post_views

            active_group = node_views.get(key)
            if active_group is not None:
                self.play(Indicate(active_group, color=NODE_ACTIVE), run_time=t(0.28))

            root_state = f"root={tree.root.key}({'B' if tree.root.color == Color.BLACK else 'R'})"
            bh = self.black_height(tree.root, tree.NIL)
            self.play(
                Transform(result_text, self.make_result_text(f"inserted {key} | {root_state} | black-height={bh}")),
                run_time=t(0.42),
            )
            self.wait(t(0.2))

        self.play(
            Transform(
                subtitle,
                self.make_subtitle_group(
                    "Done: root is black, no adjacent red nodes, and all root-to-NIL paths share equal black-height."
                ),
            ),
            run_time=t(0.5),
        )
        self.wait(t(1.0))

    def trace_insert_path(self, tree: RedBlackTree, key: int):
        path = []
        node = tree.root
        while node != tree.NIL:
            path.append(node.key)
            if key < node.key:
                node = node.left
            elif key > node.key:
                node = node.right
            else:
                break
        return path

    def collect_layout(self, node: RBTNode, nil: RBTNode):
        layout = {}

        def dfs(cur: RBTNode, depth: int, x_ref: list[float]):
            if cur == nil:
                return
            dfs(cur.left, depth + 1, x_ref)
            x = x_ref[0]
            x_ref[0] += 1.0
            layout[cur] = (x, depth)
            dfs(cur.right, depth + 1, x_ref)

        dfs(node, 0, [0.0])
        return layout

    def build_tree_group(self, tree: RedBlackTree, active_key=None, path_keys=None):
        path_keys = path_keys or set()
        layout = self.collect_layout(tree.root, tree.NIL)

        if not layout:
            empty = Text("(empty)", font_size=28, color=TEXT_MUTED).move_to([0, 0.15, 0])
            return VGroup(empty), {}

        xs = [pos[0] for pos in layout.values()]
        min_x, max_x = min(xs), max(xs)
        span = max(1.0, max_x - min_x)

        max_depth = max(depth for _, depth in layout.values())
        top_y = 1.45
        bottom_y = -2.0
        level_gap = (top_y - bottom_y) / max(1, max_depth)

        def to_scene(p):
            x, depth = p
            sx = ((x - min_x) / span) * 10.6 - 5.3
            sy = top_y - depth * level_gap
            return np.array([sx, sy, 0.0])

        edges = VGroup()
        nodes = VGroup()
        node_views = {}

        for node in layout.keys():
            p = to_scene(layout[node])
            if node.left != tree.NIL:
                q = to_scene(layout[node.left])
                edge_color = EDGE_ACTIVE if (node.key in path_keys or node.left.key in path_keys) else TEXT_MUTED
                edges.add(Line(p, q, color=edge_color, stroke_width=3))
            if node.right != tree.NIL:
                q = to_scene(layout[node.right])
                edge_color = EDGE_ACTIVE if (node.key in path_keys or node.right.key in path_keys) else TEXT_MUTED
                edges.add(Line(p, q, color=edge_color, stroke_width=3))

        for node, pos in layout.items():
            center = to_scene(pos)
            if node.key == active_key:
                fill = NODE_ACTIVE
            elif node.color == Color.RED:
                fill = RED_NODE
            else:
                fill = BLACK_NODE

            circle = Circle(radius=0.26, color=WHITE, stroke_width=2).set_fill(fill, opacity=1.0)
            label = Text(str(node.key), font_size=20, color=WHITE).move_to(circle.get_center())
            group = VGroup(circle, label).move_to(center)
            nodes.add(group)
            node_views[node.key] = group

        return VGroup(edges, nodes), node_views

    def black_height(self, node: RBTNode, nil: RBTNode) -> int:
        count = 0
        cur = node
        while cur != nil:
            if cur.color == Color.BLACK:
                count += 1
            cur = cur.left
        return count + 1  # count NIL

    def make_legend(self):
        red_dot = Dot(radius=0.08, color=WHITE).set_fill(RED_NODE, opacity=1.0)
        red_text = Text("Red node", font_size=18, color=TEXT_MUTED)
        black_dot = Dot(radius=0.08, color=WHITE).set_fill(BLACK_NODE, opacity=1.0)
        black_text = Text("Black node", font_size=18, color=TEXT_MUTED)
        active_dot = Dot(radius=0.08, color=WHITE).set_fill(NODE_ACTIVE, opacity=1.0)
        active_text = Text("Current insert", font_size=18, color=TEXT_MUTED)

        row1 = VGroup(red_dot, red_text).arrange(RIGHT, buff=0.12)
        row2 = VGroup(black_dot, black_text).arrange(RIGHT, buff=0.12)
        row3 = VGroup(active_dot, active_text).arrange(RIGHT, buff=0.12)
        rows = VGroup(row1, row2, row3).arrange(DOWN, aligned_edge=LEFT, buff=0.12)

        bg = RoundedRectangle(
            corner_radius=0.08,
            width=rows.width + 0.32,
            height=rows.height + 0.26,
            stroke_color=TEXT_MUTED,
            stroke_width=1.2,
        ).set_fill(BLACK, opacity=0.58)
        rows.move_to(bg.get_center())
        return VGroup(bg, rows)

    def make_subtitle_group(self, content: str):
        text = Text(content, font_size=23, font=self.subtitle_font)
        max_width = config.frame_width - 1.2
        if text.width > max_width:
            text.scale_to_fit_width(max_width)

        bg = RoundedRectangle(
            corner_radius=0.12,
            width=min(text.width + 0.7, config.frame_width - 0.4),
            height=text.height + 0.35,
            stroke_width=0,
        ).set_fill(BLACK, opacity=0.72)

        text.move_to(bg.get_center())
        group = VGroup(bg, text)
        group.to_edge(DOWN, buff=0.2)
        return group

    def make_result_text(self, content: str):
        text = Text(content, font_size=22, color=TEXT_MUTED)
        max_width = config.frame_width * 0.54
        if text.width > max_width:
            text.scale_to_fit_width(max_width)
        text.to_corner(UR).shift(LEFT * 0.35 + DOWN * 1.15)
        return text
