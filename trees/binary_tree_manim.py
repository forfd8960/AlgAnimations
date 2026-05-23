from __future__ import annotations

from manim import *

from binary_tree import BinaryTree
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


class BinaryTreeAnim(Scene):
    def construct(self):
        self.camera.background_color = BG_DARK
        self.subtitle_font = SUBTITLE_FONT

        insert_step_run_time = 1.35
        insert_pause = 0.75
        traversal_visit_run_time = 1.05
        traversal_between_pause = 1.0

        title = Text("Binary Tree", font_size=48, color=NODE_ACTIVE).to_edge(UP)
        self.play(Write(title))

        subtitle_group = self.make_subtitle_group(
            "We start with an empty binary tree and insert values level by level."
        )
        self.play(FadeIn(subtitle_group, shift=UP * 0.15), run_time=0.6)

        bt = BinaryTree()
        values_to_insert = [1, 2, 3, 4, 5, 6, 7]

        mode_text = Text("Insert (level-order)", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)
        sequence_text = Text(
            f"Input sequence: {values_to_insert}", font_size=24, color=TEXT_MUTED
        ).next_to(mode_text, DOWN)
        self.play(FadeIn(mode_text), FadeIn(sequence_text))

        tree_group = None
        node_groups = {}

        for value in values_to_insert:
            insert_caption = (
                f"Insert {value}: scan each level from left to right and place it in the first empty spot."
            )
            self.play(
                Transform(subtitle_group, self.make_subtitle_group(insert_caption)),
                run_time=0.4,
            )
            bt.insert(value)
            step_text = Text(f"Insert {value}", font_size=26).to_corner(UR)
            new_tree_group, new_node_groups = self.build_tree_group(
                bt.root, highlight_value=value
            )

            if tree_group is None:
                self.play(FadeIn(new_tree_group), FadeIn(step_text), run_time=insert_step_run_time)
            else:
                self.play(
                    FadeOut(tree_group),
                    FadeIn(new_tree_group),
                    Transform(mode_text, step_text),
                    run_time=insert_step_run_time,
                )
            tree_group = new_tree_group
            node_groups = new_node_groups
            self.wait(insert_pause)

        self.play(mode_text.animate.become(Text("Traversal Demo", font_size=30).next_to(title, DOWN)))
        self.play(
            Transform(
                subtitle_group,
                self.make_subtitle_group(
                    "Now the tree is built. Next, we visit nodes in three traversal orders."
                ),
            ),
            run_time=0.5,
        )

        traversals = [
            ("Inorder", self.inorder_values(bt.root), NODE_LEAF),
            ("Preorder", self.preorder_values(bt.root), EDGE_ACTIVE),
            ("Postorder", self.postorder_values(bt.root), NODE_ACTIVE),
        ]

        order_text = Text("", font_size=24).next_to(mode_text, DOWN)
        visited_text = Text("Visited: ", font_size=28).to_edge(DOWN).shift(UP * 0.8)
        self.play(FadeIn(order_text), FadeIn(visited_text))

        for name, order, color in traversals:
            self.reset_node_colors(node_groups)
            if name == "Inorder":
                traversal_caption = "Inorder means Left, then Root, then Right."
            elif name == "Preorder":
                traversal_caption = "Preorder means Root, then Left, then Right."
            else:
                traversal_caption = "Postorder means Left, then Right, then Root."

            self.play(
                Transform(
                    order_text,
                    Text(
                        f"{name}: {' '.join(map(str, order))}",
                        font_size=24,
                    ).next_to(mode_text, DOWN),
                ),
                Transform(
                    visited_text,
                    Text("Visited: ", font_size=28).to_edge(DOWN).shift(UP * 0.8),
                ),
                Transform(
                    subtitle_group,
                    self.make_subtitle_group(
                        f"{traversal_caption} Full order: {' '.join(map(str, order))}."
                    ),
                ),
            )

            visited = []
            for value in order:
                visited.append(str(value))
                circle = node_groups[value][0]
                self.play(
                    circle.animate.set_fill(color, opacity=1.0),
                    Indicate(node_groups[value], color=color),
                    Transform(
                        visited_text,
                        Text(
                            f"Visited: {' '.join(visited)}",
                            font_size=28,
                        ).to_edge(DOWN).shift(UP * 0.8),
                    ),
                    Transform(
                        subtitle_group,
                        self.make_subtitle_group(
                            f"{name}: visit node {value}. Current visited sequence: {' '.join(visited)}."
                        ),
                    ),
                    run_time=traversal_visit_run_time,
                )
            self.wait(traversal_between_pause)

        self.play(
            Transform(
                subtitle_group,
                self.make_subtitle_group(
                    "Traversal demo complete. You can pause the video to compare all three orders."
                ),
            ),
            run_time=0.5,
        )
        self.wait(1.2)

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

    def build_tree_group(self, root, highlight_value=None):
        positions = {}
        self.assign_positions(root, x=0.0, y=1.8, gap=3.0, positions=positions)

        edges = VGroup()
        nodes = VGroup()
        node_groups = {}

        for node, (x, y) in positions.items():
            if node.left:
                lx, ly = positions[node.left]
                edges.add(Line([x, y, 0], [lx, ly, 0], stroke_width=3, color=TEXT_MUTED))
            if node.right:
                rx, ry = positions[node.right]
                edges.add(Line([x, y, 0], [rx, ry, 0], stroke_width=3, color=TEXT_MUTED))

        for node, (x, y) in positions.items():
            fill_color = NODE_ACTIVE if node.value == highlight_value else NODE_NEUTRAL
            circle = Circle(radius=0.35, color=WHITE)
            circle.set_fill(fill_color, opacity=1.0)
            label = Text(str(node.value), font_size=24)
            group = VGroup(circle, label).move_to([x, y, 0])
            nodes.add(group)
            node_groups[node.value] = group

        return VGroup(edges, nodes).shift(DOWN * 0.5), node_groups

    def assign_positions(self, node, x, y, gap, positions):
        if node is None:
            return
        positions[node] = (x, y)
        next_gap = max(gap * 0.55, 0.6)
        self.assign_positions(node.left, x - gap, y - 1.1, next_gap, positions)
        self.assign_positions(node.right, x + gap, y - 1.1, next_gap, positions)

    def reset_node_colors(self, node_groups):
        for group in node_groups.values():
            group[0].set_fill(NODE_NEUTRAL, opacity=1.0)

    def inorder_values(self, node):
        if not node:
            return []
        return self.inorder_values(node.left) + [node.value] + self.inorder_values(node.right)

    def preorder_values(self, node):
        if not node:
            return []
        return [node.value] + self.preorder_values(node.left) + self.preorder_values(node.right)

    def postorder_values(self, node):
        if not node:
            return []
        return self.postorder_values(node.left) + self.postorder_values(node.right) + [node.value]
