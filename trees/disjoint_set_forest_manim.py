from __future__ import annotations

from pathlib import Path
import sys

from manim import *

try:
    from common.color import BG_DARK, EDGE_ACTIVE, NODE_ACTIVE, NODE_LEAF, NODE_NEUTRAL, TEXT_MUTED
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from common.color import BG_DARK, EDGE_ACTIVE, NODE_ACTIVE, NODE_LEAF, NODE_NEUTRAL, TEXT_MUTED

from disjoint_set_forest import DisjointSetForest


class DisjointSetForestAnim(Scene):
    def construct(self):
        self.camera.background_color = BG_DARK
        self.subtitle_font = "Arial"

        dsu = DisjointSetForest(7)

        title = Text("Disjoint Set Forest", font_size=42, color=NODE_ACTIVE).to_edge(UP)
        mode = Text("Union", font_size=28, color=TEXT_MUTED).next_to(title, DOWN)
        info = Text("n=7, parent pointers + path compression", font_size=20, color=TEXT_MUTED).next_to(mode, DOWN)
        subtitle = self.make_subtitle("Each set is a rooted tree. find() returns representative root.")
        result = self.make_result("")
        self.play(Write(title), FadeIn(mode), FadeIn(info), FadeIn(subtitle), FadeIn(result))

        g = self.build_view(dsu)
        self.play(FadeIn(g), run_time=0.8)

        for a, b in [(0, 1), (1, 2), (3, 4)]:
            dsu.union(a, b)
            g2 = self.build_view(dsu, active={a, b})
            self.play(
                Transform(subtitle, self.make_subtitle(f"union({a},{b}) merges two components by rank.")),
                ReplacementTransform(g, g2),
                Transform(result, self.make_result(f"components={dsu.components}")),
                run_time=0.8,
            )
            g = g2

        c1 = dsu.connected(0, 2)
        c2 = dsu.connected(0, 4)
        self.play(
            Transform(mode, Text("Connected", font_size=28, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info, Text("connected(a,b) compares roots", font_size=20, color=TEXT_MUTED).next_to(mode, DOWN)),
            Transform(subtitle, self.make_subtitle("0 and 2 are connected, but 0 and 4 are not yet.")),
            Transform(result, self.make_result(f"connected(0,2)={c1}, connected(0,4)={c2}")),
            run_time=0.8,
        )

        dsu.union(2, 4)
        g3 = self.build_view(dsu, active={2, 4})
        c3 = dsu.connected(0, 4)
        size3 = dsu.component_size(3)
        self.play(
            Transform(mode, Text("Merge + Size", font_size=28, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info, Text("union(2,4) joins both groups", font_size=20, color=TEXT_MUTED).next_to(mode, DOWN)),
            Transform(subtitle, self.make_subtitle("After merging, {0,1,2,3,4} becomes one component.")),
            ReplacementTransform(g, g3),
            Transform(result, self.make_result(f"connected(0,4)={c3}, size(3)={size3}, components={dsu.components}")),
            run_time=0.9,
        )
        self.wait(1.0)

    def build_view(self, dsu, active=None):
        active = active or set()
        pos = {
            0: (-4.2, 0.8), 1: (-2.8, 0.8), 2: (-1.4, 0.8),
            3: (1.4, 0.8), 4: (2.8, 0.8),
            5: (-0.8, -1.4), 6: (0.8, -1.4),
        }
        edges = VGroup()
        nodes = VGroup()

        roots = {i: dsu.find(i) for i in range(len(dsu.parent))}

        for i, p in enumerate(dsu.parent):
            if i != p:
                x1, y1 = pos[i]
                x2, y2 = pos[p]
                col = EDGE_ACTIVE if i in active or p in active else TEXT_MUTED
                edges.add(Arrow([x1, y1, 0], [x2, y2 + 0.18, 0], buff=0.24, stroke_width=2.4, color=col, max_stroke_width_to_length_ratio=6))

        for i in range(len(dsu.parent)):
            x, y = pos[i]
            root = roots[i]
            is_root = i == root
            fill = NODE_ACTIVE if i in active else (NODE_LEAF if is_root else NODE_NEUTRAL)
            c = Circle(radius=0.28, color=WHITE, stroke_width=2)
            c.set_fill(fill, opacity=0.92)
            t = Text(str(i), font_size=18, color=WHITE).move_to(c.get_center())
            r = Text(f"r={root}", font_size=11, color=TEXT_MUTED).next_to(c, DOWN, buff=0.03)
            nodes.add(VGroup(c, t, r).move_to([x, y, 0]))

        cap = Text("Parent-pointer forest", font_size=16, color=TEXT_MUTED).move_to([0, 2.2, 0])
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
        if txt.width > config.frame_width * 0.46:
            txt.scale_to_fit_width(config.frame_width * 0.46)
        txt.to_corner(UL).shift(RIGHT * 0.25 + DOWN * 1.8)
        return txt
