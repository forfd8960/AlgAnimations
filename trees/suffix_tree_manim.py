from __future__ import annotations

from manim import *

from suffix_tree import Node, SuffixTree

# Define a cohesive, high-end tech color palette
BG_DARK      = "#121317" # Soft dark slate
TEXT_MUTED   = "#8E929D" # For static UI labels like "contains / count"
NODE_NEUTRAL = "#2A3B49" # Muted blue-gray for unvisited nodes
NODE_ACTIVE  = "#00E5FF" # Electric cyan for the node currently being evaluated
EDGE_ACTIVE  = "#FFB000" # Vibrant amber/gold to track the active traversal path
NODE_LEAF    = "#2E7D32" # Deep, highly legible green for matching leaves


class SuffixTreeAnim(Scene):
    def construct(self):
        
        self.camera.background_color = BG_DARK
        self.subtitle_font = "Arial"

        pace = 1.15

        def t(seconds: float) -> float:
            return seconds * pace

        base_text = "banana"

        # Build an empty tree configured for text+terminal, then insert suffixes step by step.
        st = SuffixTree(base_text)
        st.root = Node()

        title = Text("Suffix Tree", font_size=46, color=NODE_ACTIVE).to_edge(UP)
        self.play(Write(title))

        subtitle = self.make_subtitle_group(
            "Suffix tree stores all suffixes of a string in a compressed trie."
        )
        self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=t(0.55))

        mode_text = Text("Build", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)
        info_text = Text(
            f"text = {base_text!r}, stored as {st.text!r}",
            font_size=24,
            color=TEXT_MUTED,
        ).next_to(mode_text, DOWN)
        result_text = self.make_result_text("")
        self.play(FadeIn(mode_text), FadeIn(info_text), FadeIn(result_text))

        tree_group, node_views = self.build_tree_group(st)
        self.play(FadeIn(tree_group), run_time=t(0.8))

        for i in range(st.n):
            suffix = st.text[i:]
            self.play(
                Transform(
                    subtitle,
                    self.make_subtitle_group(
                        f"Insert suffix at index {i}: {suffix!r}. Split edge when mismatch appears."
                    ),
                ),
                run_time=t(0.4),
            )

            st._insert_suffix(i)

            highlight_ids = self.trace_suffix_insertion_path(st, i)
            new_tree_group, new_node_views = self.build_tree_group(st, highlight_ids=set(highlight_ids))
            self.play(ReplacementTransform(tree_group, new_tree_group), run_time=t(0.95))
            tree_group = new_tree_group
            node_views = new_node_views

            for node_id in highlight_ids:
                group = node_views.get(node_id)
                if group is not None:
                    self.play(Indicate(group, color=EDGE_ACTIVE), run_time=t(0.25))

            self.play(
                Transform(result_text, self.make_result_text(f"inserted suffix index {i}")),
                run_time=t(0.35),
            )
            self.wait(t(0.2))

        self.play(
            Transform(mode_text, Text("Query", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(
                info_text,
                Text("contains / count / find_all", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN),
            ),
            Transform(result_text, self.make_result_text("")),
            Transform(
                subtitle,
                self.make_subtitle_group(
                    "Query matches the pattern along edge labels. If matched, collect leaf suffix indices."
                ),
            ),
            run_time=t(0.55),
        )

        patterns = ["ana", "na", "ban", "nana", "apple", "a", ""]
        for pattern in patterns:
            path_ids, ok = self.trace_pattern_path(st, pattern)
            contains = st.contains(pattern)
            count = st.count(pattern)
            indices = st.find_all(pattern)

            self.play(
                Transform(
                    subtitle,
                    self.make_subtitle_group(
                        f"Pattern {pattern!r}: traverse edges using longest matching prefix."
                    ),
                ),
                run_time=t(0.35),
            )

            new_tree_group, new_node_views = self.build_tree_group(
                st,
                highlight_ids=set(path_ids),
                failed=not ok,
            )
            self.play(ReplacementTransform(tree_group, new_tree_group), run_time=t(0.75))
            tree_group = new_tree_group
            node_views = new_node_views

            for node_id in path_ids:
                group = node_views.get(node_id)
                if group is not None:
                    self.play(Indicate(group, color=NODE_ACTIVE if contains else RED_D), run_time=t(0.22))

            msg = f"contains={contains}, count={count}, find_all={indices}"
            self.play(Transform(result_text, self.make_result_text(msg)), run_time=t(0.45))
            self.wait(t(0.25))

        self.play(
            Transform(
                subtitle,
                self.make_subtitle_group(
                    "Done: build inserts all suffixes once, then queries reuse the compressed structure."
                ),
            ),
            run_time=t(0.5),
        )
        self.wait(t(1.0))

    def trace_suffix_insertion_path(self, st: SuffixTree, suffix_start: int):
        path = [id(st.root)]
        cur = st.root
        i = suffix_start

        while i < st.n:
            ch = st.text[i]
            edge = cur.children.get(ch)
            if edge is None:
                break

            path.append(id(edge.dest))
            e_start, e_end = edge.start, edge.end

            k = 0
            while e_start + k <= e_end and i + k < st.n and st.text[e_start + k] == st.text[i + k]:
                k += 1

            edge_len = e_end - e_start + 1
            if k < edge_len:
                break

            i += k
            cur = edge.dest

        return path

    def trace_pattern_path(self, st: SuffixTree, pattern: str):
        if pattern == "":
            return [id(st.root)], True

        cur = st.root
        i = 0
        m = len(pattern)
        path = [id(cur)]

        while i < m:
            ch = pattern[i]
            edge = cur.children.get(ch)
            if edge is None:
                return path, False

            path.append(id(edge.dest))
            e_start, e_end = edge.start, edge.end
            j = 0

            while e_start + j <= e_end and i + j < m:
                if st.text[e_start + j] != pattern[i + j]:
                    return path, False
                j += 1

            i += j
            edge_len = e_end - e_start + 1

            if i == m:
                return path, True

            if j < edge_len:
                return path, False

            cur = edge.dest

        return path, True

    def collect_structure(self, st: SuffixTree):
        layout = {}
        leaves = []
        node_by_id = {}

        def dfs(node: Node, depth: int):
            node_id = id(node)
            node_by_id[node_id] = node

            child_ids = []
            children_sorted = sorted(
                node.children.values(),
                key=lambda edge: st.text[edge.start : edge.end + 1],
            )
            for edge in children_sorted:
                cid = id(edge.dest)
                child_ids.append(cid)
                dfs(edge.dest, depth + 1)

            layout[node_id] = {"depth": depth, "children": child_ids}
            if len(child_ids) == 0:
                leaves.append(node_id)

        dfs(st.root, 0)
        return layout, leaves, node_by_id

    def assign_positions(self, st: SuffixTree):
        layout, leaves, node_by_id = self.collect_structure(st)
        positions = {}

        if len(leaves) == 1:
            positions[leaves[0]] = (0.0, 0)
        else:
            left = -5.7
            right = 5.7
            step = (right - left) / max(1, len(leaves) - 1)
            for i, leaf_id in enumerate(leaves):
                positions[leaf_id] = (left + i * step, layout[leaf_id]["depth"])

        def place(node_id: int):
            children = layout[node_id]["children"]
            if not children:
                return positions[node_id][0]

            xs = [place(cid) for cid in children]
            x = sum(xs) / len(xs)
            positions[node_id] = (x, layout[node_id]["depth"])
            return x

        place(id(st.root))
        max_depth = max(meta["depth"] for meta in layout.values())
        return positions, layout, node_by_id, max_depth

    def build_tree_group(self, st: SuffixTree, highlight_ids=None, failed=False):
        highlight_ids = highlight_ids or set()
        positions, layout, node_by_id, max_depth = self.assign_positions(st)

        top_y = 1.6
        bottom_y = -2.0
        level_gap = (top_y - bottom_y) / max(1, max_depth)

        def y_of(depth: int):
            return top_y - depth * level_gap

        edges = VGroup()
        edge_labels = VGroup()
        nodes = VGroup()
        node_views = {}

        for node_id, meta in layout.items():
            x, depth = positions[node_id]
            node = node_by_id[node_id]

            children_sorted = sorted(
                node.children.values(),
                key=lambda edge: st.text[edge.start : edge.end + 1],
            )

            for edge in children_sorted:
                child_id = id(edge.dest)
                cx, cdepth = positions[child_id]

                edge_color = RED_D if failed and child_id in highlight_ids else NODE_NEUTRAL
                line = Line([x, y_of(depth), 0], [cx, y_of(cdepth), 0], color=edge_color, stroke_width=3)
                edges.add(line)

                label_text = st.text[edge.start : edge.end + 1]
                label = Text(label_text, font_size=17, color=TEXT_MUTED)
                if label.width > 2.2:
                    label.scale_to_fit_width(2.2)

                label_bg = RoundedRectangle(
                    corner_radius=0.06,
                    width=label.width + 0.18,
                    height=label.height + 0.1,
                    stroke_width=0,
                )
                label_bg.set_fill(BLACK, opacity=0.75)
                label.move_to(label_bg.get_center())

                tag = VGroup(label_bg, label)
                tag.move_to((line.get_start() + line.get_end()) / 2 + DOWN * 0.03)
                edge_labels.add(tag)

        for node_id, (x, depth) in positions.items():
            node = node_by_id[node_id]
            is_root = node is st.root
            is_highlight = node_id in highlight_ids

            if failed and is_highlight:
                fill = RED_D
            elif is_highlight:
                fill = NODE_ACTIVE
            elif node.suffix_index >= 0:
                fill = NODE_LEAF
            else:
                fill = NODE_NEUTRAL

            radius = 0.24 if is_root else 0.2
            circle = Circle(radius=radius, color=WHITE, stroke_width=2)
            circle.set_fill(fill, opacity=1.0)

            if is_root:
                text = "*"
            elif node.suffix_index >= 0:
                text = str(node.suffix_index)
            else:
                text = ""

            label = Text(text, font_size=16, color=TEXT_MUTED).move_to(ORIGIN)
            group = VGroup(circle, label).move_to([x, y_of(depth), 0])

            nodes.add(group)
            node_views[node_id] = group

        return VGroup(edges, edge_labels, nodes), node_views

    def make_subtitle_group(self, content):
        text = Text(content, font=self.subtitle_font, font_size=23, color=TEXT_MUTED)
        # text = MarkupText(
        #     'Pattern <span color="#FFB000"><b>\'nana\'</b></span>: traverse edges using longest matching prefix.',
        #     font=self.subtitle_font,
        #     font_size=24
        # )

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
        max_width = config.frame_width * 0.48
        if text.width > max_width:
            text.scale_to_fit_width(max_width)
        text.to_corner(UR).shift(LEFT * 0.35 + DOWN * 1.2)
        return text
