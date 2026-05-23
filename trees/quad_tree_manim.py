from __future__ import annotations

from pathlib import Path
import sys

from manim import *

try:
    from common.color import BG_DARK, EDGE_ACTIVE, NODE_ACTIVE, NODE_LEAF, NODE_NEUTRAL, TEXT_MUTED
except ModuleNotFoundError:
    # Manim may run with only `trees/` on sys.path; add project root for shared modules.
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from common.color import BG_DARK, EDGE_ACTIVE, NODE_ACTIVE, NODE_LEAF, NODE_NEUTRAL, TEXT_MUTED

from quad_tree import Point, Quadtree, Rect


class QuadTreeAnim(Scene):
    def construct(self):
        self.camera.background_color = BG_DARK
        self.subtitle_font = "Arial"

        pace = 1.12

        def t(seconds: float) -> float:
            return seconds * pace

        world = Rect(cx=0, cy=0, hw=100, hh=100)
        qt = Quadtree(boundary=world, capacity=4)

        points = [
            Point(-10, 20, "A"),
            Point(15, 25, "B"),
            Point(30, -40, "C"),
            Point(-50, -60, "D"),
            Point(70, 80, "E"),
            Point(5, 5, "F"),
            Point(8, 7, "G"),
            Point(9, 6, "H"),
        ]

        title = Text("Quadtree", font_size=46, color=NODE_ACTIVE).to_edge(UP)
        self.play(Write(title))

        subtitle = self.make_subtitle_group(
            "Quadtree recursively subdivides 2D space into four quadrants when capacity is exceeded."
        )
        self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=t(0.55))

        mode_text = Text("Insert", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)
        info_text = Text("capacity=4, world=[-100,100] x [-100,100]", font_size=24, color=TEXT_MUTED).next_to(
            mode_text, DOWN
        )
        result_text = self.make_result_text("")
        self.play(FadeIn(mode_text), FadeIn(info_text), FadeIn(result_text))

        tree_group = self.build_quadtree_group(qt)
        self.play(FadeIn(tree_group), run_time=t(0.8))

        for p in points:
            self.play(
                Transform(
                    subtitle,
                    self.make_subtitle_group(
                        f"insert({p.data} at ({self.fmt_num(p.x)}, {self.fmt_num(p.y)})): place point; split node when full."
                    ),
                ),
                run_time=t(0.35),
            )

            ok = qt.insert(p)
            nodes, total_points = qt.stats()
            new_group = self.build_quadtree_group(qt, active_points={(p.x, p.y)})
            self.play(ReplacementTransform(tree_group, new_group), run_time=t(0.85))
            tree_group = new_group
            self.play(
                Transform(
                    result_text,
                    self.make_result_text(f"insert({p.data}) -> {ok}; nodes={nodes}, points={total_points}"),
                ),
                run_time=t(0.42),
            )
            self.wait(t(0.2))

        nodes, total_points = qt.stats()
        self.play(
            Transform(mode_text, Text("Range Query", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info_text, Text("area center=(0,0), hw=20, hh=30", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN)),
            Transform(
                subtitle,
                self.make_subtitle_group("query_range checks only quadrants whose rectangles intersect query area."),
            ),
            Transform(result_text, self.make_result_text(f"Tree stats: nodes={nodes}, points={total_points}, len={len(qt)}")),
            run_time=t(0.6),
        )

        area = Rect(cx=0, cy=0, hw=20, hh=30)
        found = qt.query_range(area)
        found_set = {(p.x, p.y) for p in found}
        new_group = self.build_quadtree_group(qt, highlighted_points=found_set, query_area=area)
        self.play(ReplacementTransform(tree_group, new_group), run_time=t(0.9))
        tree_group = new_group
        self.play(
            Transform(
                result_text,
                self.make_result_text(
                    "query_range -> "
                    + str([(p.data, (self.fmt_num(p.x), self.fmt_num(p.y))) for p in found])
                ),
            ),
            run_time=t(0.45),
        )
        self.wait(t(0.25))

        self.play(
            Transform(mode_text, Text("Radius Query", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info_text, Text("center=(0,0), r=15", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN)),
            Transform(
                subtitle,
                self.make_subtitle_group("query_radius first filters by box, then keeps points whose distance <= r."),
            ),
            run_time=t(0.55),
        )

        near = qt.query_radius(x=0, y=0, r=15)
        near_set = {(p.x, p.y) for p in near}
        new_group = self.build_quadtree_group(qt, highlighted_points=near_set, query_circle=(0, 0, 15))
        self.play(ReplacementTransform(tree_group, new_group), run_time=t(0.9))
        tree_group = new_group
        self.play(
            Transform(
                result_text,
                self.make_result_text(
                    "query_radius -> "
                    + str([(p.data, (self.fmt_num(p.x), self.fmt_num(p.y))) for p in near])
                ),
            ),
            run_time=t(0.45),
        )
        self.wait(t(0.25))

        self.play(
            Transform(mode_text, Text("Remove", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info_text, Text("target: Point(5,5,'F')", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN)),
            Transform(
                subtitle,
                self.make_subtitle_group("remove deletes matching point, then tries to merge child quadrants if possible."),
            ),
            run_time=t(0.55),
        )

        target = Point(5, 5, "F")
        first = qt.remove(target)
        second = qt.remove(target)
        nodes, total_points = qt.stats()

        new_group = self.build_quadtree_group(qt, query_point=(target.x, target.y), failed=not first)
        self.play(ReplacementTransform(tree_group, new_group), run_time=t(0.95))
        tree_group = new_group
        self.play(
            Transform(
                result_text,
                self.make_result_text(
                    f"remove(F) -> {first}; remove(F) again -> {second}; nodes={nodes}, points={total_points}, len={len(qt)}"
                ),
            ),
            run_time=t(0.5),
        )

        self.play(
            Transform(
                subtitle,
                self.make_subtitle_group(
                    "Done: quadtree accelerates spatial queries by pruning whole regions during search."
                ),
            ),
            run_time=t(0.5),
        )
        self.wait(t(1.0))

    def build_quadtree_group(
        self,
        qt: Quadtree,
        active_points=None,
        highlighted_points=None,
        query_area: Rect | None = None,
        query_circle=None,
        query_point=None,
        failed: bool = False,
    ):
        active_points = active_points or set()
        highlighted_points = highlighted_points or set()

        panel = RoundedRectangle(corner_radius=0.1, width=8.8, height=6.35, stroke_color=NODE_NEUTRAL, stroke_width=1.5)
        panel.set_fill(BLACK, opacity=0.22)
        panel.move_to([0, -0.28, 0])

        caption = Text("2D Space + Quadtree Partitions", font_size=18, color=TEXT_MUTED).next_to(panel, UP, buff=0.08)

        boundary_lines = VGroup()
        self.collect_partition_lines(qt, boundary_lines)

        points = VGroup()
        labels = VGroup()
        for p in self.collect_points(qt):
            pos = self.to_scene(p.x, p.y)
            key = (p.x, p.y)

            if key in active_points:
                col = NODE_ACTIVE
            elif key in highlighted_points:
                col = NODE_LEAF
            else:
                col = NODE_NEUTRAL

            dot = Dot(pos, radius=0.065, color=col)
            lbl = Text(str(p.data), font_size=15, color=TEXT_MUTED).next_to(dot, UR, buff=0.05)
            points.add(dot)
            labels.add(lbl)

        overlays = VGroup()
        if query_area is not None:
            rect = self.rect_to_manim(query_area, EDGE_ACTIVE)
            rect.set_fill(EDGE_ACTIVE, opacity=0.1)
            overlays.add(rect)

        if query_circle is not None:
            x, y, r = query_circle
            c = Circle(radius=self.scale_dist(r), color=EDGE_ACTIVE, stroke_width=2)
            c.move_to(self.to_scene(x, y))
            c.set_fill(EDGE_ACTIVE, opacity=0.08)
            overlays.add(c)

        if query_point is not None:
            x, y = query_point
            q = Dot(self.to_scene(x, y), radius=0.07, color=RED_D if failed else EDGE_ACTIVE)
            overlays.add(q)

        world_rect = self.rect_to_manim(qt.boundary, TEXT_MUTED)
        world_rect.set_stroke(width=2)

        return VGroup(panel, caption, world_rect, boundary_lines, overlays, points, labels)

    def collect_partition_lines(self, node: Quadtree, out: VGroup):
        if not node.divided:
            return

        b = node.boundary
        x_min, x_max = b.cx - b.hw, b.cx + b.hw
        y_min, y_max = b.cy - b.hh, b.cy + b.hh

        # Split lines for this node
        v = Line(self.to_scene(b.cx, y_min), self.to_scene(b.cx, y_max), color=TEXT_MUTED, stroke_width=1.8)
        h = Line(self.to_scene(x_min, b.cy), self.to_scene(x_max, b.cy), color=TEXT_MUTED, stroke_width=1.8)
        out.add(v, h)

        self.collect_partition_lines(node.nw, out)  # type: ignore[arg-type]
        self.collect_partition_lines(node.ne, out)  # type: ignore[arg-type]
        self.collect_partition_lines(node.sw, out)  # type: ignore[arg-type]
        self.collect_partition_lines(node.se, out)  # type: ignore[arg-type]

    def collect_points(self, node: Quadtree):
        if not node.divided:
            return list(node.points)

        pts = []
        pts.extend(self.collect_points(node.nw))  # type: ignore[arg-type]
        pts.extend(self.collect_points(node.ne))  # type: ignore[arg-type]
        pts.extend(self.collect_points(node.sw))  # type: ignore[arg-type]
        pts.extend(self.collect_points(node.se))  # type: ignore[arg-type]
        return pts

    def rect_to_manim(self, r: Rect, color):
        w = self.scale_dist(2 * r.hw)
        h = self.scale_dist(2 * r.hh)
        rect = Rectangle(width=w, height=h, color=color)
        rect.move_to(self.to_scene(r.cx, r.cy))
        return rect

    def to_scene(self, x: float, y: float):
        # Map world [-100,100] to panel area roughly [-4,4] x [-2.8,2.8]
        return [x * 0.04, y * 0.028, 0]

    def scale_dist(self, d: float):
        return d * 0.04

    def fmt_num(self, x: float):
        if float(x).is_integer():
            return str(int(x))
        return f"{x:.2f}"

    def make_subtitle_group(self, content):
        text = Text(content, font=self.subtitle_font, font_size=23, color=TEXT_MUTED)
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
        text = Text(content, font_size=20, color=NODE_ACTIVE)
        max_width = config.frame_width * 0.62
        if text.width > max_width:
            text.scale_to_fit_width(max_width)
        text.to_corner(UR).shift(LEFT * 0.3 + DOWN * 1.15)
        return text
