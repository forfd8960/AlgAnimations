from __future__ import annotations

from pathlib import Path
import sys

from manim import *

try:
    from common.color import BG_DARK, EDGE_ACTIVE, NODE_ACTIVE, NODE_LEAF, NODE_NEUTRAL, TEXT_MUTED
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from common.color import BG_DARK, EDGE_ACTIVE, NODE_ACTIVE, NODE_LEAF, NODE_NEUTRAL, TEXT_MUTED

from fenwick_tree import FenwickTree


class FenwickTreeAnim(Scene):
    def construct(self):
        self.camera.background_color = BG_DARK
        self.subtitle_font = "Arial"

        arr = [2, 1, 5, 3, 4, 7, 6, 8]
        ft = FenwickTree(arr)

        title = Text("Fenwick Tree", font_size=44, color=NODE_ACTIVE).to_edge(UP)
        mode = Text("Build", font_size=28, color=TEXT_MUTED).next_to(title, DOWN)
        info = Text(f"arr={arr}", font_size=20, color=TEXT_MUTED).next_to(mode, DOWN)
        subtitle = self.make_subtitle("Fenwick tree stores partial prefix sums using lowbit jumps.")
        result = self.make_result("")

        self.play(Write(title), FadeIn(mode), FadeIn(info), FadeIn(subtitle), FadeIn(result))

        g = self.build_view(ft, arr)
        self.play(FadeIn(g), run_time=0.8)

        q1 = ft.range_sum(2, 6)
        self.play(
            Transform(subtitle, self.make_subtitle("range_sum(l,r) = prefix_sum(r) - prefix_sum(l-1).")),
            Transform(result, self.make_result(f"Fenwick sum[2..6] = {q1}")),
            run_time=0.6,
        )

        g2 = self.build_view(ft, arr, query_range=(2, 6))
        self.play(ReplacementTransform(g, g2), run_time=0.75)
        g = g2

        self.play(
            Transform(mode, Text("Range Add Loop", font_size=28, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info, Text("for i in [3..5]: add(i, +10)", font_size=20, color=TEXT_MUTED).next_to(mode, DOWN)),
            Transform(subtitle, self.make_subtitle("Each add updates indices i += i&-i in BIT array.")),
            run_time=0.6,
        )

        arr2 = arr[:]
        for i in range(3, 6):
            before = ft.bit[:]
            ft.add(i, 10)
            arr2[i] += 10
            path = self.add_path(i, len(arr))
            g3 = self.build_view(ft, arr2, active_bit_idxs=set(path), changed_idx=i)
            self.play(ReplacementTransform(g, g3), run_time=0.72)
            g = g3
            self.play(Transform(result, self.make_result(f"add({i},+10), update path(bit idx): {path}")), run_time=0.35)

        q2 = ft.range_sum(2, 6)
        self.play(
            Transform(mode, Text("Query Again", font_size=28, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info, Text("after updates on [3..5]", font_size=20, color=TEXT_MUTED).next_to(mode, DOWN)),
            Transform(subtitle, self.make_subtitle("Updated partial sums now yield a larger range sum.")),
            Transform(result, self.make_result(f"Fenwick sum[2..6] = {q2}")),
            run_time=0.6,
        )

        g4 = self.build_view(ft, arr2, query_range=(2, 6))
        self.play(ReplacementTransform(g, g4), run_time=0.8)
        self.wait(1.0)

    def add_path(self, idx, n):
        i = idx + 1
        path = []
        while i <= n:
            path.append(i)
            i += i & -i
        return path

    def build_view(self, ft, arr, active_bit_idxs=None, query_range=None, changed_idx=None):
        active_bit_idxs = active_bit_idxs or set()
        array = self.build_array(arr, query_range, changed_idx)
        bit = self.build_bit(ft, active_bit_idxs)
        return VGroup(array, bit)

    def build_array(self, arr, query_range=None, changed_idx=None):
        g = VGroup()
        start_x = -5.3
        y = -2.95
        for i, v in enumerate(arr):
            x = start_x + i * 1.35
            in_q = query_range is not None and query_range[0] <= i <= query_range[1]
            fill = NODE_LEAF if i == changed_idx else (NODE_ACTIVE if in_q else NODE_NEUTRAL)
            b = RoundedRectangle(corner_radius=0.05, width=1.15, height=0.58, stroke_color=WHITE, stroke_width=1.5)
            b.set_fill(fill, opacity=0.9)
            b.move_to([x, y, 0])
            t = Text(str(v), font_size=18, color=WHITE).move_to(b.get_center())
            idx = Text(str(i), font_size=12, color=TEXT_MUTED).next_to(b, DOWN, buff=0.05)
            g.add(VGroup(b, t, idx))
        cap = Text("Array (0-based)", font_size=16, color=TEXT_MUTED).next_to(g, UP, buff=0.12)
        return VGroup(cap, g)

    def build_bit(self, ft, active_bit_idxs):
        g = VGroup()
        n = ft.n
        start_x = -5.3
        y = 0.8
        for i in range(1, n + 1):
            x = start_x + (i - 1) * 1.35
            fill = NODE_ACTIVE if i in active_bit_idxs else NODE_NEUTRAL
            b = RoundedRectangle(corner_radius=0.05, width=1.15, height=0.58, stroke_color=WHITE, stroke_width=1.5)
            b.set_fill(fill, opacity=0.9)
            b.move_to([x, y, 0])
            t = Text(str(ft.bit[i]), font_size=17, color=WHITE).move_to(b.get_center())
            idx = Text(str(i), font_size=12, color=TEXT_MUTED).next_to(b, DOWN, buff=0.05)
            rng_l = i - (i & -i) + 1
            rng = Text(f"[{rng_l}..{i}]", font_size=11, color=TEXT_MUTED).next_to(b, UP, buff=0.03)
            g.add(VGroup(b, t, idx, rng))
        cap = Text("BIT internal array (1-based)", font_size=16, color=TEXT_MUTED).move_to([0, 1.75, 0])
        return VGroup(cap, g)

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
