from __future__ import annotations

from pathlib import Path
import sys

from manim import *

try:
    from common.color import BG_DARK, EDGE_ACTIVE, NODE_ACTIVE, NODE_LEAF, NODE_NEUTRAL, TEXT_MUTED
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from common.color import BG_DARK, EDGE_ACTIVE, NODE_ACTIVE, NODE_LEAF, NODE_NEUTRAL, TEXT_MUTED

from r_tree import RTree, Rectangle as RRect


class RTreeAnim(Scene):
    def construct(self):
        self.camera.background_color = BG_DARK
        self.subtitle_font = "Arial"

        pace = 1.12

        def t(seconds: float) -> float:
            return seconds * pace

        spatial_index = RTree(max_entries=4)

        entries = [
            (RRect(1, 1, 2, 2), "Downtown Coffee Shop"),
            (RRect(5, 5, 6, 6), "Suburban Gas Station"),
            (RRect(2, 1, 3, 2), "Central Park Pizzeria"),
            (RRect(10, 12, 11, 13), "Airport Terminal"),
        ]

        query_window = RRect(0, 0, 4, 3)

        title = Text("R-Tree", font_size=46, color=NODE_ACTIVE).to_edge(UP)
        self.play(Write(title))

        subtitle = self.make_subtitle_group(
            "R-Tree stores objects inside bounding rectangles (MBBs) for spatial search."
        )
        self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=t(0.55))

        mode_text = Text("Insert", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)
        info_text = Text("max_entries=4", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN)
        result_text = self.make_result_text("")
        self.play(FadeIn(mode_text), FadeIn(info_text), FadeIn(result_text))

        scene_group = self.build_scene_group(spatial_index)
        self.play(FadeIn(scene_group), run_time=t(0.8))

        for rect, name in entries:
            self.play(
                Transform(
                    subtitle,
                    self.make_subtitle_group(
                        f"insert({name}): choose best subtree, then enlarge node MBB to include new rectangle."
                    ),
                ),
                run_time=t(0.35),
            )

            spatial_index.insert(rect, name)

            new_group = self.build_scene_group(
                spatial_index,
                active_names={name},
            )
            self.play(ReplacementTransform(scene_group, new_group), run_time=t(0.9))
            scene_group = new_group

            self.play(
                Transform(result_text, self.make_result_text(f"inserted: {name}")),
                run_time=t(0.4),
            )
            self.wait(t(0.2))

        self.play(
            Transform(mode_text, Text("Search", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info_text, Text("query window: x[0,4], y[0,3]", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN)),
            Transform(
                subtitle,
                self.make_subtitle_group("Search prunes branches whose MBB does not intersect the query rectangle."),
            ),
            run_time=t(0.55),
        )

        if spatial_index.root.mbb and spatial_index.root.mbb.intersects(query_window):
            self.play(
                Transform(
                    subtitle,
                    self.make_subtitle_group("Root MBB intersects query, so we evaluate each leaf entry."),
                ),
                run_time=t(0.35),
            )

        hits = set()
        misses = set()

        # This main() example produces a single leaf root, so we can step entries directly.
        for box, name in spatial_index.root.entries:
            intersects = box.intersects(query_window)
            if intersects:
                hits.add(name)
            else:
                misses.add(name)

            new_group = self.build_scene_group(
                spatial_index,
                query_rect=query_window,
                active_names={name},
                hit_names=hits,
                miss_names=misses,
            )
            self.play(ReplacementTransform(scene_group, new_group), run_time=t(0.65))
            scene_group = new_group

            check_msg = "intersects" if intersects else "no intersection"
            self.play(
                Transform(result_text, self.make_result_text(f"check {name}: {check_msg}")),
                run_time=t(0.35),
            )

        found_places = spatial_index.search(query_window)

        new_group = self.build_scene_group(
            spatial_index,
            query_rect=query_window,
            hit_names=set(found_places),
            miss_names=set(name for _, name in entries if name not in found_places),
        )
        self.play(ReplacementTransform(scene_group, new_group), run_time=t(0.8))
        scene_group = new_group

        self.play(
            Transform(
                result_text,
                self.make_result_text(f"Places visible in map view: {found_places}"),
            ),
            run_time=t(0.45),
        )

        self.play(
            Transform(
                subtitle,
                self.make_subtitle_group("Done: R-Tree speeds up map queries by filtering with bounding rectangles first."),
            ),
            run_time=t(0.5),
        )
        self.wait(t(1.0))

    def build_scene_group(
        self,
        tree: RTree,
        active_names=None,
        hit_names=None,
        miss_names=None,
        query_rect: RRect | None = None,
    ):
        active_names = active_names or set()
        hit_names = hit_names or set()
        miss_names = miss_names or set()

        left_panel = self.build_map_panel(tree, active_names, hit_names, miss_names, query_rect)
        right_panel = self.build_tree_panel(tree, active_names, hit_names, miss_names)
        return VGroup(left_panel, right_panel)

    def build_map_panel(self, tree: RTree, active_names, hit_names, miss_names, query_rect):
        panel = RoundedRectangle(corner_radius=0.1, width=7.0, height=6.1, stroke_color=NODE_NEUTRAL, stroke_width=1.5)
        panel.set_fill(BLACK, opacity=0.22)
        panel.to_edge(LEFT).shift(RIGHT * 0.15 + DOWN * 0.35)

        caption = Text("Map Space", font_size=18, color=TEXT_MUTED).next_to(panel, UP, buff=0.08)

        axes = Axes(
            x_range=[0, 12, 2],
            y_range=[0, 14, 2],
            x_length=5.9,
            y_length=4.85,
            axis_config={"color": TEXT_MUTED, "stroke_width": 2},
            tips=False,
        )
        axes.move_to(panel)

        rects = VGroup()
        labels = VGroup()

        for box, name in tree.root.entries:
            if name in active_names:
                col = NODE_ACTIVE
            elif name in hit_names:
                col = NODE_LEAF
            elif name in miss_names:
                col = NODE_NEUTRAL
            else:
                col = TEXT_MUTED

            r = self.rect_to_axes(axes, box, col)
            fill_opacity = 0.22 if name in hit_names else 0.12
            r.set_fill(col, opacity=fill_opacity)
            rects.add(r)

            short = self.short_name(name)
            lbl = Text(short, font_size=13, color=TEXT_MUTED).move_to(r.get_center())
            labels.add(lbl)

        overlays = VGroup()
        if tree.root.mbb is not None:
            mbb_rect = self.rect_to_axes(axes, tree.root.mbb, EDGE_ACTIVE)
            mbb_rect.set_stroke(width=2.2)
            mbb_rect.set_fill(EDGE_ACTIVE, opacity=0.0)
            overlays.add(mbb_rect)

        if query_rect is not None:
            qr = self.rect_to_axes(axes, query_rect, EDGE_ACTIVE)
            qr.set_fill(EDGE_ACTIVE, opacity=0.08)
            qr.set_stroke(width=2.4)
            overlays.add(qr)

        x_lab = Text("x", font_size=14, color=TEXT_MUTED).next_to(axes.x_axis.get_end(), RIGHT, buff=0.05)
        y_lab = Text("y", font_size=14, color=TEXT_MUTED).next_to(axes.y_axis.get_end(), UP, buff=0.05)

        return VGroup(panel, caption, axes, x_lab, y_lab, rects, overlays, labels)

    def build_tree_panel(self, tree: RTree, active_names, hit_names, miss_names):
        panel = RoundedRectangle(corner_radius=0.1, width=6.4, height=6.1, stroke_color=NODE_NEUTRAL, stroke_width=1.5)
        panel.set_fill(BLACK, opacity=0.22)
        panel.to_edge(RIGHT).shift(LEFT * 0.12 + DOWN * 0.35)

        caption = Text("R-Tree Node", font_size=18, color=TEXT_MUTED).next_to(panel, UP, buff=0.08)

        node_box = RoundedRectangle(corner_radius=0.08, width=5.6, height=1.0, stroke_color=WHITE, stroke_width=2)
        node_box.set_fill(NODE_NEUTRAL, opacity=0.9)
        node_box.move_to(panel.get_top() + DOWN * 1.1)

        node_kind = "Leaf" if tree.root.is_leaf else "Internal"
        mbb_text = "None"
        if tree.root.mbb is not None:
            b = tree.root.mbb
            mbb_text = f"[{self.fmt_num(b.x_min)}, {self.fmt_num(b.y_min)}] - [{self.fmt_num(b.x_max)}, {self.fmt_num(b.y_max)}]"

        header = Text(f"{node_kind} | MBB {mbb_text}", font_size=16, color=TEXT_MUTED)
        if header.width > 5.2:
            header.scale_to_fit_width(5.2)
        header.move_to(node_box.get_center())

        rows = VGroup()
        y0 = node_box.get_bottom()[1] - 0.35
        row_h = 0.78

        for i, (box, name) in enumerate(tree.root.entries):
            row = RoundedRectangle(corner_radius=0.06, width=5.6, height=0.62, stroke_color=WHITE, stroke_width=1.5)
            row.move_to([panel.get_center()[0], y0 - i * row_h, 0])

            if name in active_names:
                fill = NODE_ACTIVE
                text_color = BG_DARK
            elif name in hit_names:
                fill = NODE_LEAF
                text_color = WHITE
            elif name in miss_names:
                fill = NODE_NEUTRAL
                text_color = WHITE
            else:
                fill = NODE_NEUTRAL
                text_color = WHITE
            row.set_fill(fill, opacity=0.85)

            meta = f"[{self.fmt_num(box.x_min)},{self.fmt_num(box.y_min)}]-[{self.fmt_num(box.x_max)},{self.fmt_num(box.y_max)}]"
            text = Text(f"{name}  {meta}", font_size=15, color=text_color, weight=BOLD)
            if text.width > 5.1:
                text.scale_to_fit_width(5.1)
            text.move_to(row.get_center())

            rows.add(VGroup(row, text))

        return VGroup(panel, caption, node_box, header, rows)

    def rect_to_axes(self, axes: Axes, r: RRect, color):
        x0, y0 = axes.c2p(r.x_min, r.y_min)[:2]
        x1, y1 = axes.c2p(r.x_max, r.y_max)[:2]
        rect = Rectangle(width=x1 - x0, height=y1 - y0, color=color)
        rect.move_to(axes.c2p((r.x_min + r.x_max) / 2, (r.y_min + r.y_max) / 2))
        return rect

    def short_name(self, name: str):
        words = name.split()
        if len(words) == 1:
            return words[0][:8]
        return " ".join(w[:4] for w in words[:2])

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
        text = Text(content, font_size=18, color=NODE_ACTIVE)
        max_width = config.frame_width * 0.42
        if text.width > max_width:
            text.scale_to_fit_width(max_width)
        text.to_corner(UR).shift(LEFT * 0.3 + DOWN * 1.95)
        return text
