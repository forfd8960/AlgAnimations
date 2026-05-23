from __future__ import annotations

from pathlib import Path
import sys

from manim import *

try:
    from common.color import BG_DARK, EDGE_ACTIVE, NODE_ACTIVE, NODE_LEAF, NODE_NEUTRAL, TEXT_MUTED
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from common.color import BG_DARK, EDGE_ACTIVE, NODE_ACTIVE, NODE_LEAF, NODE_NEUTRAL, TEXT_MUTED

from finger_tree import FingerTree


class FingerTreeAnim(Scene):
    def construct(self):
        self.camera.background_color = BG_DARK
        self.subtitle_font = "Arial"

        ft = FingerTree.empty()

        title = Text("Finger Tree", font_size=44, color=NODE_ACTIVE).to_edge(UP)
        mode = Text("Build", font_size=28, color=TEXT_MUTED).next_to(title, DOWN)
        info = Text("front / mid / back buffers", font_size=20, color=TEXT_MUTED).next_to(mode, DOWN)
        subtitle = self.make_subtitle("Persistent sequence with efficient operations near both ends.")
        result = self.make_result("")
        self.play(Write(title), FadeIn(mode), FadeIn(info), FadeIn(subtitle), FadeIn(result))

        g = self.draw_buffers(ft)
        self.play(FadeIn(g), run_time=0.8)

        ops = [
            ("append", 10),
            ("append", 20),
            ("prepend", 5),
            ("append", 30),
            ("prepend", 1),
        ]
        for op, x in ops:
            if op == "append":
                ft = ft.append(x)
                msg = f"append({x})"
            else:
                ft = ft.prepend(x)
                msg = f"prepend({x})"

            g2 = self.draw_buffers(ft, active=op)
            self.play(
                Transform(subtitle, self.make_subtitle(f"{msg}: element is added near one finger and structure rebalances if needed.")),
                ReplacementTransform(g, g2),
                Transform(result, self.make_result(f"contents={ft.to_list()}")),
                run_time=0.75,
            )
            g = g2

        left = ft.peek_left()
        right = ft.peek_right()
        self.play(
            Transform(mode, Text("Peek", font_size=28, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info, Text("peek_left / peek_right", font_size=20, color=TEXT_MUTED).next_to(mode, DOWN)),
            Transform(subtitle, self.make_subtitle("Peeking reads both ends without removing.")),
            Transform(result, self.make_result(f"peek_left={left}, peek_right={right}")),
            run_time=0.7,
        )

        x, ft = ft.pop_left()
        y, ft = ft.pop_right()
        g3 = self.draw_buffers(ft, active="both")
        self.play(
            Transform(mode, Text("Pop", font_size=28, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info, Text("pop_left + pop_right", font_size=20, color=TEXT_MUTED).next_to(mode, DOWN)),
            Transform(subtitle, self.make_subtitle("Pops remove from both fingers; middle stays persistent structure.")),
            ReplacementTransform(g, g3),
            Transform(result, self.make_result(f"pop_left={x}, pop_right={y}, after={ft.to_list()}")),
            run_time=0.85,
        )

        self.wait(1.0)

    def draw_buffers(self, ft, active=None):
        front = list(ft._front)
        mid = list(ft._mid)
        back = list(ft._back)

        front_g = self.draw_buffer("Front", front, [-4.1, 0.35, 0], NODE_ACTIVE if active in {"prepend", "both"} else NODE_NEUTRAL)
        mid_g = self.draw_buffer("Middle", mid, [0.0, 0.35, 0], NODE_NEUTRAL)
        back_g = self.draw_buffer("Back", back, [4.1, 0.35, 0], NODE_ACTIVE if active in {"append", "both"} else NODE_NEUTRAL)

        arrows = VGroup(
            Arrow([-2.2, 0.35, 0], [-0.95, 0.35, 0], color=TEXT_MUTED, buff=0.1, stroke_width=2.2),
            Arrow([0.95, 0.35, 0], [2.2, 0.35, 0], color=TEXT_MUTED, buff=0.1, stroke_width=2.2),
        )

        seq = Text(f"to_list() = {ft.to_list()}", font_size=18, color=TEXT_MUTED).move_to([0, -2.15, 0])
        return VGroup(front_g, mid_g, back_g, arrows, seq)

    def draw_buffer(self, name, items, center, panel_color):
        panel = RoundedRectangle(corner_radius=0.1, width=3.3, height=3.2, stroke_color=WHITE, stroke_width=1.5)
        panel.set_fill(panel_color, opacity=0.25)
        panel.move_to(center)

        title = Text(name, font_size=18, color=TEXT_MUTED).next_to(panel, UP, buff=0.07)

        cells = VGroup()
        y0 = center[1] + 1.0
        for i, v in enumerate(items[:7]):
            row = RoundedRectangle(corner_radius=0.05, width=2.65, height=0.34, stroke_color=WHITE, stroke_width=1.2)
            row.set_fill(NODE_LEAF if i < 2 else NODE_NEUTRAL, opacity=0.9)
            row.move_to([center[0], y0 - i * 0.42, 0])
            txt = Text(str(v), font_size=14, color=WHITE).move_to(row.get_center())
            cells.add(VGroup(row, txt))

        if len(items) > 7:
            more = Text(f"... +{len(items)-7}", font_size=13, color=TEXT_MUTED).move_to([center[0], y0 - 7 * 0.42, 0])
            cells.add(more)

        return VGroup(panel, title, cells)

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
        if txt.width > config.frame_width * 0.52:
            txt.scale_to_fit_width(config.frame_width * 0.52)
        txt.to_corner(UL).shift(RIGHT * 0.25 + DOWN * 1.8)
        return txt
