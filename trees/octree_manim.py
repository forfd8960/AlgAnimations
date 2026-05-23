from __future__ import annotations

from pathlib import Path
import sys

from manim import *

try:
    from common.color import BG_DARK, EDGE_ACTIVE, NODE_ACTIVE, NODE_LEAF, NODE_NEUTRAL, TEXT_MUTED
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from common.color import BG_DARK, EDGE_ACTIVE, NODE_ACTIVE, NODE_LEAF, NODE_NEUTRAL, TEXT_MUTED

from octree import Box, Octree, Point3D


class OctreeAnim(Scene):
    def construct(self):
        self.camera.background_color = BG_DARK
        self.subtitle_font = "Arial"

        pace = 1.12

        def t(seconds: float) -> float:
            return seconds * pace

        world = Box(cx=0, cy=0, cz=0, hx=100, hy=100, hz=100)
        tree = Octree(boundary=world, capacity=4)

        pts = [
            Point3D(-10, 20, 5, "A"),
            Point3D(15, 25, -12, "B"),
            Point3D(30, -40, 10, "C"),
            Point3D(-50, -60, 30, "D"),
            Point3D(70, 80, -70, "E"),
            Point3D(5, 5, 5, "F"),
            Point3D(8, 7, 6, "G"),
            Point3D(9, 6, 4, "H"),
        ]

        title = Text("Octree", font_size=46, color=NODE_ACTIVE).to_edge(UP)
        self.play(Write(title))

        subtitle = self.make_subtitle_group(
            "Octree recursively subdivides 3D space into 8 octants when node capacity is exceeded."
        )
        self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=t(0.55))

        mode_text = Text("Insert", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)
        info_text = Text("capacity=4, world center=(0,0,0), half=(100,100,100)", font_size=24, color=TEXT_MUTED)
        info_text.next_to(mode_text, DOWN)
        result_text = self.make_result_text("")
        self.play(FadeIn(mode_text), FadeIn(info_text), FadeIn(result_text))

        scene_group = self.build_scene_group(tree)
        self.play(FadeIn(scene_group), run_time=t(0.8))

        for p in pts:
            self.play(
                Transform(
                    subtitle,
                    self.make_subtitle_group(
                        f"insert({p.data} at ({self.fmt_num(p.x)},{self.fmt_num(p.y)},{self.fmt_num(p.z)})): descend to one octant and split if full."
                    ),
                ),
                run_time=t(0.35),
            )

            ok = tree.insert(p)
            nodes, count = tree.stats()

            new_group = self.build_scene_group(tree, active_points={(p.x, p.y, p.z)})
            self.play(ReplacementTransform(scene_group, new_group), run_time=t(0.85))
            scene_group = new_group

            self.play(
                Transform(
                    result_text,
                    self.make_result_text(f"insert({p.data}) -> {ok}; nodes={nodes}, points={count}"),
                ),
                run_time=t(0.42),
            )
            self.wait(t(0.2))

        nodes, count = tree.stats()
        self.play(
            Transform(mode_text, Text("Box Query", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info_text, Text("region center=(0,0,0), half=(20,30,20)", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN)),
            Transform(
                subtitle,
                self.make_subtitle_group("query_box prunes octants whose boxes do not intersect the query box."),
            ),
            Transform(result_text, self.make_result_text(f"Tree stats: nodes={nodes}, points={count}, len={len(tree)}")),
            run_time=t(0.6),
        )

        region = Box(cx=0, cy=0, cz=0, hx=20, hy=30, hz=20)
        found = tree.query_box(region)
        found_set = {(p.x, p.y, p.z) for p in found}

        new_group = self.build_scene_group(tree, highlighted_points=found_set, query_box=region)
        self.play(ReplacementTransform(scene_group, new_group), run_time=t(0.9))
        scene_group = new_group

        self.play(
            Transform(
                result_text,
                self.make_result_text(
                    "query_box -> "
                    + str([(p.data, (self.fmt_num(p.x), self.fmt_num(p.y), self.fmt_num(p.z))) for p in found])
                ),
            ),
            run_time=t(0.45),
        )
        self.wait(t(0.25))

        self.play(
            Transform(mode_text, Text("Radius Query", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info_text, Text("center=(0,0,0), r=15", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN)),
            Transform(
                subtitle,
                self.make_subtitle_group("query_radius first applies box filter, then exact 3D distance check."),
            ),
            run_time=t(0.55),
        )

        near = tree.query_radius(0, 0, 0, 15)
        near_set = {(p.x, p.y, p.z) for p in near}

        new_group = self.build_scene_group(tree, highlighted_points=near_set, query_sphere=(0, 0, 0, 15))
        self.play(ReplacementTransform(scene_group, new_group), run_time=t(0.9))
        scene_group = new_group

        self.play(
            Transform(
                result_text,
                self.make_result_text(
                    "query_radius -> "
                    + str([(p.data, (self.fmt_num(p.x), self.fmt_num(p.y), self.fmt_num(p.z))) for p in near])
                ),
            ),
            run_time=t(0.45),
        )
        self.wait(t(0.25))

        self.play(
            Transform(mode_text, Text("Remove", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info_text, Text("target: Point3D(5,5,5,'F')", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN)),
            Transform(
                subtitle,
                self.make_subtitle_group("remove deletes one exact point and may merge children if they fit capacity."),
            ),
            run_time=t(0.55),
        )

        target = Point3D(5, 5, 5, "F")
        first = tree.remove(target)
        second = tree.remove(target)
        nodes, count = tree.stats()

        new_group = self.build_scene_group(tree, query_point=(5, 5, 5), failed=not first)
        self.play(ReplacementTransform(scene_group, new_group), run_time=t(0.95))
        scene_group = new_group

        self.play(
            Transform(
                result_text,
                self.make_result_text(
                    f"remove(F) -> {first}; remove(F) again -> {second}; nodes={nodes}, points={count}, len={len(tree)}"
                ),
            ),
            run_time=t(0.5),
        )

        self.play(
            Transform(
                subtitle,
                self.make_subtitle_group("Done: octree speeds up 3D spatial queries by pruning entire subspaces early."),
            ),
            run_time=t(0.5),
        )
        self.wait(t(1.0))

    def build_scene_group(
        self,
        tree: Octree,
        active_points=None,
        highlighted_points=None,
        query_box: Box | None = None,
        query_sphere=None,
        query_point=None,
        failed: bool = False,
    ):
        active_points = active_points or set()
        highlighted_points = highlighted_points or set()

        left = self.build_projection_panel(
            tree,
            active_points,
            highlighted_points,
            query_box,
            query_sphere,
            query_point,
            failed,
        )
        right = self.build_octants_panel(tree, active_points, highlighted_points)
        return VGroup(left, right)

    def build_projection_panel(self, tree, active_points, highlighted_points, query_box, query_sphere, query_point, failed):
        panel = RoundedRectangle(corner_radius=0.1, width=7.3, height=6.25, stroke_color=NODE_NEUTRAL, stroke_width=1.5)
        panel.set_fill(BLACK, opacity=0.22)
        panel.to_edge(LEFT).shift(RIGHT * 0.12 + DOWN * 0.35)

        caption = Text("3D Projection (x-y, color by z)", font_size=18, color=TEXT_MUTED).next_to(panel, UP, buff=0.08)

        axes = Axes(
            x_range=[-100, 100, 50],
            y_range=[-100, 100, 50],
            x_length=5.9,
            y_length=5.15,
            axis_config={"color": TEXT_MUTED, "stroke_width": 2},
            tips=False,
        )
        axes.move_to(panel)

        splits = VGroup()
        self.collect_split_lines(tree, axes, splits)

        pts = VGroup()
        labels = VGroup()
        for p in self.collect_points(tree):
            key = (p.x, p.y, p.z)
            if key in active_points:
                col = NODE_ACTIVE
            elif key in highlighted_points:
                col = NODE_LEAF
            else:
                col = self.z_to_color(p.z)

            dot = Dot(axes.c2p(p.x, p.y), radius=0.06, color=col)
            pts.add(dot)
            labels.add(Text(str(p.data), font_size=14, color=TEXT_MUTED).next_to(dot, UR, buff=0.05))

        overlays = VGroup()
        if query_box is not None:
            r = self.box_xy_rect(axes, query_box, EDGE_ACTIVE)
            r.set_fill(EDGE_ACTIVE, opacity=0.1)
            overlays.add(r)

        if query_sphere is not None:
            x, y, _z, r = query_sphere
            c = Circle(radius=self.scale_x(axes, r), color=EDGE_ACTIVE, stroke_width=2.2)
            c.move_to(axes.c2p(x, y))
            c.set_fill(EDGE_ACTIVE, opacity=0.08)
            overlays.add(c)

        if query_point is not None:
            x, y, _z = query_point
            q = Dot(axes.c2p(x, y), radius=0.07, color=RED_D if failed else EDGE_ACTIVE)
            overlays.add(q)

        x_lab = Text("x", font_size=14, color=TEXT_MUTED).next_to(axes.x_axis.get_end(), RIGHT, buff=0.05)
        y_lab = Text("y", font_size=14, color=TEXT_MUTED).next_to(axes.y_axis.get_end(), UP, buff=0.05)

        return VGroup(panel, caption, axes, x_lab, y_lab, splits, overlays, pts, labels)

    def build_octants_panel(self, tree: Octree, active_points, highlighted_points):
        panel = RoundedRectangle(corner_radius=0.1, width=5.95, height=6.25, stroke_color=NODE_NEUTRAL, stroke_width=1.5)
        panel.set_fill(BLACK, opacity=0.22)
        panel.to_edge(RIGHT).shift(LEFT * 0.12 + DOWN * 0.35)

        caption = Text("Root Octants", font_size=18, color=TEXT_MUTED).next_to(panel, UP, buff=0.08)

        octant_names = ["LDB", "RDB", "LUB", "RUB", "LDF", "RDF", "LUF", "RUF"]
        rows = VGroup()

        counts = {name: 0 for name in octant_names}
        for p in self.collect_points(tree):
            counts[self.point_octant(tree.boundary, p)] += 1

        top = panel.get_top()[1] - 0.85
        for i, name in enumerate(octant_names):
            row = RoundedRectangle(corner_radius=0.06, width=5.15, height=0.55, stroke_color=WHITE, stroke_width=1.5)
            row.move_to([panel.get_center()[0], top - i * 0.66, 0])

            is_active_oct = False
            for key in active_points.union(highlighted_points):
                px, py, pz = key
                if self.point_octant(tree.boundary, Point3D(px, py, pz, None)) == name:
                    is_active_oct = True
                    break

            if is_active_oct:
                fill = NODE_ACTIVE
                txt_col = BG_DARK
            elif counts[name] > 0:
                fill = NODE_LEAF
                txt_col = WHITE
            else:
                fill = NODE_NEUTRAL
                txt_col = WHITE

            row.set_fill(fill, opacity=0.85)
            text = Text(f"{name}: {counts[name]} point(s)", font_size=15, color=txt_col, weight=BOLD)
            text.move_to(row.get_center())
            rows.add(VGroup(row, text))

        nodes, count = tree.stats()
        stats = Text(f"nodes={nodes} | points={count} | len={len(tree)}", font_size=15, color=TEXT_MUTED)
        stats.next_to(panel, DOWN, buff=0.1)

        return VGroup(panel, caption, rows, stats)

    def collect_split_lines(self, node: Octree, axes: Axes, out: VGroup):
        if not node.divided:
            return

        b = node.boundary
        x_min, x_max = b.cx - b.hx, b.cx + b.hx
        y_min, y_max = b.cy - b.hy, b.cy + b.hy

        out.add(Line(axes.c2p(b.cx, y_min), axes.c2p(b.cx, y_max), color=TEXT_MUTED, stroke_width=1.7))
        out.add(Line(axes.c2p(x_min, b.cy), axes.c2p(x_max, b.cy), color=TEXT_MUTED, stroke_width=1.7))

        if node.children is None:
            return
        for ch in node.children:
            self.collect_split_lines(ch, axes, out)

    def collect_points(self, node: Octree):
        if not node.divided:
            return list(node.points)
        if node.children is None:
            return []
        out = []
        for ch in node.children:
            out.extend(self.collect_points(ch))
        return out

    def box_xy_rect(self, axes: Axes, b: Box, color):
        x0, y0 = axes.c2p(b.cx - b.hx, b.cy - b.hy)[:2]
        x1, y1 = axes.c2p(b.cx + b.hx, b.cy + b.hy)[:2]
        rect = Rectangle(width=x1 - x0, height=y1 - y0, color=color)
        rect.move_to(axes.c2p(b.cx, b.cy))
        return rect

    def scale_x(self, axes: Axes, d: float):
        x0 = axes.c2p(0, 0)[0]
        x1 = axes.c2p(d, 0)[0]
        return abs(x1 - x0)

    def z_to_color(self, z: float):
        # Negative z -> neutral, positive z -> leaf tone.
        if z > 10:
            return NODE_LEAF
        if z < -10:
            return NODE_NEUTRAL
        return EDGE_ACTIVE

    def point_octant(self, b: Box, p: Point3D):
        lr = "L" if p.x < b.cx else "R"
        du = "D" if p.y < b.cy else "U"
        bf = "B" if p.z < b.cz else "F"
        return lr + du + bf

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
        text = Text(content, font_size=19, color=NODE_ACTIVE)
        max_width = config.frame_width * 0.42
        if text.width > max_width:
            text.scale_to_fit_width(max_width)
        # Keep result text on the left side so it does not overlap the right panel.
        text.to_corner(UL).shift(RIGHT * 0.35 + DOWN * 1.9)
        return text
