from __future__ import annotations

from pathlib import Path
import sys

from manim import *

try:
    from common.color import BG_DARK, EDGE_ACTIVE, NODE_ACTIVE, NODE_LEAF, NODE_NEUTRAL, TEXT_MUTED
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from common.color import BG_DARK, EDGE_ACTIVE, NODE_ACTIVE, NODE_LEAF, NODE_NEUTRAL, TEXT_MUTED

from link_cut_tree import LinkCutTree


class LinkCutTreeAnim(Scene):
    def construct(self):
        self.camera.background_color = BG_DARK
        self.subtitle_font = "Arial"

        lct = LinkCutTree()
        a = lct.make_tree(5)
        b = lct.make_tree(2)
        c = lct.make_tree(7)
        d = lct.make_tree(1)
        vals = {a: 5, b: 2, c: 7, d: 1}
        edges = set()

        title = Text("Link-Cut Tree", font_size=42, color=NODE_ACTIVE).to_edge(UP)
        mode = Text("Link", font_size=28, color=TEXT_MUTED).next_to(title, DOWN)
        info = Text("Dynamic forest: link/cut/connect/path aggregate", font_size=20, color=TEXT_MUTED).next_to(mode, DOWN)
        subtitle = self.make_subtitle("Concept view: dynamic-tree operations on the represented forest.")
        result = self.make_result("")
        self.play(Write(title), FadeIn(mode), FadeIn(info), FadeIn(subtitle), FadeIn(result))

        g = self.draw_forest(vals, edges)
        self.play(FadeIn(g), run_time=0.8)

        for u, v, label in [(a, b, "a-b"), (b, c, "a-b-c"), (c, d, "a-b-c-d")]:
            lct.link(u, v)
            edges.add(tuple(sorted((u, v))))
            g2 = self.draw_forest(vals, edges, active={u, v})
            self.play(
                Transform(subtitle, self.make_subtitle(f"link({u},{v}) connects roots of two trees.")),
                ReplacementTransform(g, g2),
                Transform(result, self.make_result(f"linked {label}")),
                run_time=0.85,
            )
            g = g2

        conn_ad = lct.connected(a, d)
        ps = lct.path_sum(a, d)
        path_nodes = {a, b, c, d}
        g3 = self.draw_forest(vals, edges, active=path_nodes)
        self.play(
            Transform(mode, Text("Path Query", font_size=28, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info, Text("connected + path_sum", font_size=20, color=TEXT_MUTED).next_to(mode, DOWN)),
            Transform(subtitle, self.make_subtitle("path_sum(a,d)=5+2+7+1 across current preferred path.")),
            ReplacementTransform(g, g3),
            Transform(result, self.make_result(f"connected(a,d)={conn_ad}, path_sum(a,d)={ps}")),
            run_time=0.9,
        )
        g = g3

        lct.cut(c, d)
        edges.remove(tuple(sorted((c, d))))
        conn1 = lct.connected(a, d)
        conn2 = lct.connected(c, d)
        g4 = self.draw_forest(vals, edges, active={c, d})
        self.play(
            Transform(mode, Text("Cut", font_size=28, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info, Text("cut(c,d) removes one edge", font_size=20, color=TEXT_MUTED).next_to(mode, DOWN)),
            Transform(subtitle, self.make_subtitle("After cut, the forest splits into two trees.")),
            ReplacementTransform(g, g4),
            Transform(result, self.make_result(f"connected(a,d)={conn1}, connected(c,d)={conn2}")),
            run_time=0.9,
        )
        self.wait(1.0)

    def draw_forest(self, vals, edges, active=None):
        active = active or set()
        pos = {
            0: (-3.8, 0.2),
            1: (-1.7, 0.2),
            2: (0.4, 0.2),
            3: (2.5, 0.2),
        }
        ed = VGroup()
        nd = VGroup()

        for u, v in edges:
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            col = EDGE_ACTIVE if u in active or v in active else TEXT_MUTED
            ed.add(Line([x1, y1, 0], [x2, y2, 0], color=col, stroke_width=4))

        for i, val in vals.items():
            x, y = pos[i]
            fill = NODE_ACTIVE if i in active else NODE_NEUTRAL
            c = Circle(radius=0.34, color=WHITE, stroke_width=2)
            c.set_fill(fill, opacity=0.92)
            t = Text(f"{i}\n{val}", font_size=16, color=WHITE).move_to(c.get_center())
            nd.add(VGroup(c, t).move_to([x, y, 0]))

        cap = Text("Node label: id / value", font_size=16, color=TEXT_MUTED).move_to([0, 1.7, 0])
        return VGroup(cap, ed, nd)

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
        if txt.width > config.frame_width * 0.5:
            txt.scale_to_fit_width(config.frame_width * 0.5)
        txt.to_corner(UL).shift(RIGHT * 0.25 + DOWN * 1.8)
        return txt
