from __future__ import annotations

from manim import *

from kd_tree import KDNode, KDTree
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


class KDTreeAnim(Scene):
    def construct(self):
        self.camera.background_color = BG_DARK
        self.subtitle_font = SUBTITLE_FONT

        pace = 1.15

        def t(seconds: float) -> float:
            return seconds * pace

        points = [
            ((2, 3), "A"),
            ((5, 4), "B"),
            ((9, 6), "C"),
            ((4, 7), "D"),
            ((8, 1), "E"),
            ((7, 2), "F"),
        ]

        tree = KDTree(points=points, k=2)

        title = Text("KD-Tree", font_size=46, color=NODE_ACTIVE).to_edge(UP)
        self.play(Write(title))

        subtitle = self.make_subtitle_group(
            "KD-Tree splits space by alternating axes (x, y, x, y ...) and stores points in a binary tree."
        )
        self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=t(0.55))

        mode_text = Text("Build", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)
        info_text = Text("points from kd_tree.main()", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN)
        result_text = self.make_result_text("")
        self.play(FadeIn(mode_text), FadeIn(info_text), FadeIn(result_text))

        viz_group, node_views = self.build_scene_group(tree)
        self.play(FadeIn(viz_group), run_time=t(0.85))

        self.play(
            Transform(
                subtitle,
                self.make_subtitle_group("The initial tree is built from points list with k=2 dimensions."),
            ),
            Transform(result_text, self.make_result_text(f"initial points: {[p for p, _ in points]}")),
            run_time=t(0.6),
        )
        self.wait(t(0.3))

        # Contains examples from main()
        for q in [(5, 4), (1, 1)]:
            path_ids = self.trace_path(tree, q)
            ok = tree.contains(q)
            self.play(
                Transform(
                    subtitle,
                    self.make_subtitle_group(f"contains({q}): compare query on current axis and descend left/right."),
                ),
                run_time=t(0.35),
            )

            new_group, new_views = self.build_scene_group(
                tree,
                active_node_ids=set(path_ids),
                query_point=q,
                failed=not ok,
            )
            self.play(ReplacementTransform(viz_group, new_group), run_time=t(0.75))
            viz_group = new_group
            node_views = new_views

            for nid in path_ids:
                group = node_views.get(nid)
                if group is not None:
                    self.play(Indicate(group, color=EDGE_ACTIVE if ok else RED_D), run_time=t(0.22))

            self.play(
                Transform(result_text, self.make_result_text(f"contains({q}) -> {ok}")),
                run_time=t(0.4),
            )
            self.wait(t(0.2))

        # Insert + contains
        self.play(
            Transform(mode_text, Text("Insert", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info_text, Text("Insert (1,1) with value 'G'", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN)),
            Transform(
                subtitle,
                self.make_subtitle_group("insert((1,1),'G'): descend by axis rules until an empty child slot."),
            ),
            run_time=t(0.55),
        )

        path_ids = self.trace_path(tree, (1, 1))
        tree.insert((1, 1), "G")
        new_group, new_views = self.build_scene_group(tree, active_node_ids=set(path_ids), query_point=(1, 1))
        self.play(ReplacementTransform(viz_group, new_group), run_time=t(0.95))
        viz_group = new_group
        node_views = new_views
        self.play(Transform(result_text, self.make_result_text("after insert: contains((1,1)) -> True")), run_time=t(0.45))
        self.wait(t(0.25))

        # nearest
        q = (6, 3)
        nearest = tree.nearest(q)
        nearest_pt = nearest[0] if nearest else None
        self.play(
            Transform(mode_text, Text("Nearest", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info_text, Text("query = (6,3)", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN)),
            Transform(
                subtitle,
                self.make_subtitle_group("nearest(query): recurse near branch first, then far branch only if needed."),
            ),
            run_time=t(0.55),
        )

        new_group, new_views = self.build_scene_group(
            tree,
            query_point=q,
            highlighted_points={nearest_pt} if nearest_pt is not None else set(),
        )
        self.play(ReplacementTransform(viz_group, new_group), run_time=t(0.85))
        viz_group = new_group
        node_views = new_views
        self.play(
            Transform(result_text, self.make_result_text(f"nearest({q}) -> {nearest}")),
            run_time=t(0.45),
        )
        self.wait(t(0.25))

        # k_nearest
        knn = tree.k_nearest(q, k=3)
        knn_points = {item[0] for item in knn}
        self.play(
            Transform(mode_text, Text("K-Nearest", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info_text, Text("k_nearest((6,3), k=3)", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN)),
            Transform(
                subtitle,
                self.make_subtitle_group("k_nearest keeps a bounded heap of best candidates while pruning subtrees."),
            ),
            run_time=t(0.55),
        )

        new_group, new_views = self.build_scene_group(tree, query_point=q, highlighted_points=knn_points)
        self.play(ReplacementTransform(viz_group, new_group), run_time=t(0.85))
        viz_group = new_group
        node_views = new_views
        self.play(
            Transform(result_text, self.make_result_text(f"3 nearest: {[(p, round(d, 3)) for p, _, d in knn]}")),
            run_time=t(0.5),
        )
        self.wait(t(0.25))

        # range search
        lo, hi = (3, 2), (9, 6)
        inside = tree.range_search(lo, hi)
        inside_points = {p for p, _ in inside}

        self.play(
            Transform(mode_text, Text("Range Search", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info_text, Text("box: [(3,2) .. (9,6)]", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN)),
            Transform(
                subtitle,
                self.make_subtitle_group("range_search visits only branches that can intersect the query rectangle."),
            ),
            run_time=t(0.55),
        )

        new_group, new_views = self.build_scene_group(
            tree,
            highlighted_points=inside_points,
            range_box=(lo, hi),
        )
        self.play(ReplacementTransform(viz_group, new_group), run_time=t(0.9))
        viz_group = new_group
        node_views = new_views
        self.play(
            Transform(result_text, self.make_result_text(f"inside box: {sorted(list(inside_points))}")),
            run_time=t(0.45),
        )
        self.wait(t(0.3))

        # delete + contains
        deleted = tree.delete((5, 4))
        contains_after = tree.contains((5, 4))

        self.play(
            Transform(mode_text, Text("Delete", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info_text, Text("delete((5,4))", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN)),
            Transform(
                subtitle,
                self.make_subtitle_group("delete removes one matching point, then tree links are adjusted."),
            ),
            run_time=t(0.55),
        )

        new_group, _new_views = self.build_scene_group(tree, query_point=(5, 4), failed=not deleted)
        self.play(ReplacementTransform(viz_group, new_group), run_time=t(0.9))
        viz_group = new_group
        self.play(
            Transform(result_text, self.make_result_text(f"delete((5,4)) -> {deleted}; contains((5,4)) -> {contains_after}")),
            run_time=t(0.5),
        )

        self.play(
            Transform(
                subtitle,
                self.make_subtitle_group("Done: KD-Tree supports fast point lookup, nearest neighbors, and box queries."),
            ),
            run_time=t(0.5),
        )
        self.wait(t(1.1))

    def trace_path(self, tree: KDTree[str], point):
        pt = tuple(float(x) for x in point)
        cur = tree.root
        depth = 0
        path = []

        while cur is not None:
            path.append(id(cur))
            if cur.point == pt:
                return path
            axis = depth % (tree.k or 1)
            if pt[axis] < cur.point[axis]:
                cur = cur.left
            else:
                cur = cur.right
            depth += 1
        return path

    def collect_nodes(self, root: KDNode[str] | None):
        nodes = []

        def dfs(n: KDNode[str] | None):
            if n is None:
                return
            nodes.append(n)
            dfs(n.left)
            dfs(n.right)

        dfs(root)
        return nodes

    def assign_tree_positions(self, root: KDNode[str] | None):
        positions = {}

        def place(node: KDNode[str] | None, x: float, y: float, gap: float):
            if node is None:
                return
            node_id = id(node)
            positions[node_id] = (x, y)
            next_gap = max(gap * 0.55, 0.45)
            place(node.left, x - gap, y - 0.8, next_gap)
            place(node.right, x + gap, y - 0.8, next_gap)

        place(root, 3.25, 1.45, 1.35)
        return positions

    def build_plane_group(self, tree: KDTree[str], active_node_ids=None, highlighted_points=None, query_point=None, range_box=None):
        active_node_ids = active_node_ids or set()
        highlighted_points = highlighted_points or set()

        ax = Axes(
            x_range=[0, 10, 2],
            y_range=[0, 10, 2],
            x_length=5.6,
            y_length=5.2,
            axis_config={"color": TEXT_MUTED, "stroke_width": 2},
            tips=False,
        ).to_corner(UL).shift(DOWN * 0.45 + RIGHT * 0.2)

        x_lab = Text("x", font_size=16, color=TEXT_MUTED).next_to(ax.x_axis.get_end(), RIGHT, buff=0.08)
        y_lab = Text("y", font_size=16, color=TEXT_MUTED).next_to(ax.y_axis.get_end(), UP, buff=0.08)

        splits = VGroup()

        def draw_splits(node: KDNode[str] | None, xmin: float, xmax: float, ymin: float, ymax: float):
            if node is None:
                return
            active = id(node) in active_node_ids
            line_color = EDGE_ACTIVE if active else TEXT_MUTED
            if node.axis == 0:
                x = node.point[0]
                splits.add(Line(ax.c2p(x, ymin), ax.c2p(x, ymax), color=line_color, stroke_width=2.2 if active else 1.6))
                draw_splits(node.left, xmin, x, ymin, ymax)
                draw_splits(node.right, x, xmax, ymin, ymax)
            else:
                y = node.point[1]
                splits.add(Line(ax.c2p(xmin, y), ax.c2p(xmax, y), color=line_color, stroke_width=2.2 if active else 1.6))
                draw_splits(node.left, xmin, xmax, ymin, y)
                draw_splits(node.right, xmin, xmax, y, ymax)

        draw_splits(tree.root, 0, 10, 0, 10)

        points_group = VGroup()
        labels = VGroup()

        for node in self.collect_nodes(tree.root):
            pt = tuple(node.point)
            nid = id(node)

            if pt in highlighted_points:
                fill = NODE_LEAF
            elif nid in active_node_ids:
                fill = NODE_ACTIVE
            else:
                fill = NODE_NEUTRAL

            dot = Dot(ax.c2p(pt[0], pt[1]), radius=0.065, color=fill)
            points_group.add(dot)

            vtxt = node.value if node.value is not None else ""
            lbl = Text(vtxt, font_size=14, color=TEXT_MUTED).next_to(dot, UR, buff=0.06)
            labels.add(lbl)

        overlays = VGroup()
        if query_point is not None:
            qx, qy = float(query_point[0]), float(query_point[1])
            qdot = Dot(ax.c2p(qx, qy), radius=0.07, color=EDGE_ACTIVE)
            qlbl = Text("Q", font_size=15, color=EDGE_ACTIVE).next_to(qdot, UP, buff=0.07)
            overlays.add(qdot, qlbl)

        if range_box is not None:
            lo, hi = range_box
            x0, y0 = lo
            x1, y1 = hi
            rect = Rectangle(
                width=ax.c2p(x1, y0)[0] - ax.c2p(x0, y0)[0],
                height=ax.c2p(x0, y1)[1] - ax.c2p(x0, y0)[1],
                stroke_color=EDGE_ACTIVE,
                stroke_width=2,
            )
            rect.move_to(ax.c2p((x0 + x1) / 2, (y0 + y1) / 2))
            rect.set_fill(EDGE_ACTIVE, opacity=0.08)
            overlays.add(rect)

        panel = RoundedRectangle(corner_radius=0.1, width=6.25, height=5.95, stroke_color=NODE_NEUTRAL, stroke_width=1.5)
        panel.set_fill(BLACK, opacity=0.22)
        panel.move_to(ax)

        caption = Text("2D Space Partitions", font_size=18, color=TEXT_MUTED).next_to(panel, UP, buff=0.1)
        return VGroup(panel, caption, ax, x_lab, y_lab, splits, points_group, labels, overlays)

    def build_tree_panel(self, tree: KDTree[str], active_node_ids=None, failed=False):
        active_node_ids = active_node_ids or set()

        positions = self.assign_tree_positions(tree.root)
        edges = VGroup()
        nodes = VGroup()
        node_views = {}

        for node in self.collect_nodes(tree.root):
            nid = id(node)
            x, y = positions[nid]
            if node.left is not None:
                lx, ly = positions[id(node.left)]
                col = EDGE_ACTIVE if id(node.left) in active_node_ids else TEXT_MUTED
                edges.add(Line([x, y, 0], [lx, ly, 0], color=col, stroke_width=2.8))
            if node.right is not None:
                rx, ry = positions[id(node.right)]
                col = EDGE_ACTIVE if id(node.right) in active_node_ids else TEXT_MUTED
                edges.add(Line([x, y, 0], [rx, ry, 0], color=col, stroke_width=2.8))

        for node in self.collect_nodes(tree.root):
            nid = id(node)
            x, y = positions[nid]
            if failed and nid in active_node_ids:
                fill = RED_D
            elif nid in active_node_ids:
                fill = NODE_ACTIVE
            else:
                fill = NODE_NEUTRAL

            c = Circle(radius=0.24, color=WHITE, stroke_width=2)
            c.set_fill(fill, opacity=1.0)

            axis_name = "x" if node.axis == 0 else "y"
            px = self.fmt_num(node.point[0])
            py = self.fmt_num(node.point[1])
            lbl = Text(f"({px},{py})|{axis_name}", font_size=14, color=TEXT_MUTED).move_to(ORIGIN)
            g = VGroup(c, lbl).move_to([x, y, 0])
            nodes.add(g)
            node_views[nid] = g

        panel = RoundedRectangle(corner_radius=0.1, width=6.05, height=5.95, stroke_color=NODE_NEUTRAL, stroke_width=1.5)
        panel.set_fill(BLACK, opacity=0.22)
        panel.move_to([3.25, -0.55, 0])
        caption = Text("KD-Tree Structure", font_size=18, color=TEXT_MUTED).next_to(panel, UP, buff=0.1)
        return VGroup(panel, caption, edges, nodes), node_views

    def build_scene_group(self, tree: KDTree[str], active_node_ids=None, highlighted_points=None, query_point=None, range_box=None, failed=False):
        plane = self.build_plane_group(tree, active_node_ids, highlighted_points, query_point, range_box)
        tree_panel, node_views = self.build_tree_panel(tree, active_node_ids, failed=failed)
        return VGroup(plane, tree_panel), node_views

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
        max_width = config.frame_width * 0.54
        if text.width > max_width:
            text.scale_to_fit_width(max_width)
        text.to_corner(UR).shift(LEFT * 0.3 + DOWN * 1.15)
        return text
