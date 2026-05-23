from __future__ import annotations

from pathlib import Path
import sys

from manim import *

try:
    from common.color import BG_DARK, EDGE_ACTIVE, NODE_ACTIVE, NODE_LEAF, NODE_NEUTRAL, TEXT_MUTED
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from common.color import BG_DARK, EDGE_ACTIVE, NODE_ACTIVE, NODE_LEAF, NODE_NEUTRAL, TEXT_MUTED

from segment_tree import SegmentTree


class SegmentTreeAnim(Scene):
    def construct(self):
        self.camera.background_color = BG_DARK
        self.subtitle_font = "Arial"

        arr = [2, 1, 5, 3, 4, 7, 6, 8]
        st = SegmentTree(arr)

        title = Text("Segment Tree", font_size=44, color=NODE_ACTIVE).to_edge(UP)
        mode = Text("Build", font_size=28, color=TEXT_MUTED).next_to(title, DOWN)
        info = Text(f"arr={arr}", font_size=20, color=TEXT_MUTED).next_to(mode, DOWN)
        subtitle = self.make_subtitle("Each node stores the sum of an interval.")
        result = self.make_result("")

        self.play(Write(title), FadeIn(mode), FadeIn(info), FadeIn(subtitle), FadeIn(result))

        g = self.build_view(st, arr)
        self.play(FadeIn(g), run_time=0.8)

        q1 = st.range_sum(2, 6)
        self.play(
            Transform(subtitle, self.make_subtitle("range_sum(2,6) combines only nodes that intersect [2,6].")),
            Transform(result, self.make_result(f"Segment sum[2..6] = {q1}")),
            run_time=0.6,
        )

        g2 = self.build_view(st, arr, range_highlight=(2, 6))
        self.play(ReplacementTransform(g, g2), run_time=0.8)
        g = g2

        st.range_add(3, 5, 10)
        arr2 = arr[:]
        for i in range(3, 6):
            arr2[i] += 10
        q2 = st.range_sum(2, 6)

        self.play(
            Transform(mode, Text("Range Add", font_size=28, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info, Text("range_add(3,5,+10)", font_size=20, color=TEXT_MUTED).next_to(mode, DOWN)),
            Transform(subtitle, self.make_subtitle("Lazy propagation marks covered segments and updates sums efficiently.")),
            run_time=0.7,
        )

        g3 = self.build_view(st, arr2, range_highlight=(3, 5), changed_range=(3, 5))
        self.play(ReplacementTransform(g, g3), run_time=0.9)
        g = g3

        self.play(
            Transform(mode, Text("Query Again", font_size=28, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info, Text("after add +10 to [3..5]", font_size=20, color=TEXT_MUTED).next_to(mode, DOWN)),
            Transform(subtitle, self.make_subtitle("Now range_sum(2,6) reflects the update.")),
            Transform(result, self.make_result(f"Segment sum[2..6] = {q2}")),
            run_time=0.7,
        )

        g4 = self.build_view(st, arr2, range_highlight=(2, 6))
        self.play(ReplacementTransform(g, g4), run_time=0.8)
        self.wait(1.0)

    def build_view(self, st: SegmentTree, arr, range_highlight=None, changed_range=None):
        arr_group = self.build_array(arr, range_highlight, changed_range)
        tree_group = self.build_tree(st, len(arr), range_highlight)
        return VGroup(arr_group, tree_group)

    def build_array(self, arr, range_highlight=None, changed_range=None):
        boxes = VGroup()
        labels = VGroup()
        idxs = VGroup()
        n = len(arr)
        start_x = -5.3
        y = -3.05
        for i, v in enumerate(arr):
            x = start_x + i * 1.35
            in_q = range_highlight is not None and range_highlight[0] <= i <= range_highlight[1]
            changed = changed_range is not None and changed_range[0] <= i <= changed_range[1]
            fill = NODE_LEAF if changed else (NODE_ACTIVE if in_q else NODE_NEUTRAL)
            b = RoundedRectangle(corner_radius=0.05, width=1.15, height=0.58, stroke_color=WHITE, stroke_width=1.5)
            b.set_fill(fill, opacity=0.9)
            b.move_to([x, y, 0])
            t = Text(str(v), font_size=18, color=WHITE).move_to(b.get_center())
            idx = Text(str(i), font_size=12, color=TEXT_MUTED).next_to(b, DOWN, buff=0.05)
            boxes.add(b)
            labels.add(t)
            idxs.add(idx)
        cap = Text("Array", font_size=16, color=TEXT_MUTED).next_to(boxes, UP, buff=0.12)
        return VGroup(cap, boxes, labels, idxs)

    def build_tree(self, st: SegmentTree, n: int, range_highlight=None):
        nodes = VGroup()
        edges = VGroup()
        pos = {}
        data = []

        def dfs(node, l, r, depth, x):
            val = st.range_sum(l, r)
            data.append((node, l, r, val, depth, x))
            pos[node] = (x, 1.65 - depth * 1.02)
            if l == r:
                return
            m = (l + r) // 2
            gap = max(2.6 / (2 ** depth), 0.52)
            dfs(node * 2, l, m, depth + 1, x - gap)
            dfs(node * 2 + 1, m + 1, r, depth + 1, x + gap)

        dfs(1, 0, n - 1, 0, 0)

        for node, l, r, _, _, _ in data:
            if l == r:
                continue
            for child in (node * 2, node * 2 + 1):
                x1, y1 = pos[node]
                x2, y2 = pos[child]
                edges.add(Line([x1, y1, 0], [x2, y2, 0], color=TEXT_MUTED, stroke_width=2.1))

        for _, l, r, val, _, x in data:
            y = 1.65 - (len(bin(int(abs(x * 10)) + 1)) - 3) * 0  # keep deterministic expression-free style
            # real y from lookup
        for node, l, r, val, _, _ in data:
            x, y = pos[node]
            in_q = range_highlight is not None and not (r < range_highlight[0] or l > range_highlight[1])
            fill = NODE_ACTIVE if in_q else NODE_NEUTRAL
            b = RoundedRectangle(corner_radius=0.06, width=1.22, height=0.55, stroke_color=WHITE, stroke_width=1.5)
            b.set_fill(fill, opacity=0.9)
            b.move_to([x, y, 0])
            t = Text(f"{val}", font_size=16, color=WHITE).move_to(b.get_center())
            seg = Text(f"[{l},{r}]", font_size=12, color=TEXT_MUTED).next_to(b, DOWN, buff=0.03)
            nodes.add(VGroup(b, t, seg))

        cap = Text("Segment Tree (sum)", font_size=16, color=TEXT_MUTED).move_to([0, 2.35, 0])
        return VGroup(cap, edges, nodes)

    def make_subtitle(self, s):
        txt = Text(s, font=self.subtitle_font, font_size=21, color=TEXT_MUTED)
        if txt.width > config.frame_width - 1.0:
            txt.scale_to_fit_width(config.frame_width - 1.0)
        bg = RoundedRectangle(corner_radius=0.1, width=min(txt.width + 0.55, config.frame_width - 0.35), height=txt.height + 0.3, stroke_width=0)
        bg.set_fill(BLACK, opacity=0.72)
        txt.move_to(bg.get_center())
        g = VGroup(bg, txt)
        g.to_edge(DOWN, buff=0.2)
        return g

    def make_result(self, s):
        txt = Text(s, font_size=18, color=NODE_ACTIVE)
        if txt.width > config.frame_width * 0.45:
            txt.scale_to_fit_width(config.frame_width * 0.45)
        txt.to_corner(UL).shift(RIGHT * 0.25 + DOWN * 1.78)
        return txt
