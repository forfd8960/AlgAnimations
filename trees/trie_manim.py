from __future__ import annotations

from manim import *

from trie import Trie
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


class TrieAnim(Scene):
    def construct(self):
        self.camera.background_color = BG_DARK
        self.subtitle_font = SUBTITLE_FONT

        insert_step_time = 1.1
        walk_step_time = 0.7

        title = Text("Trie", font_size=44, color=NODE_ACTIVE).to_edge(UP)
        self.play(Write(title))

        subtitle = self.make_subtitle_group(
            "A Trie stores words character by character, sharing common prefixes."
        )
        self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=0.6)

        trie = Trie()
        words = ["apple", "app", "apricot", "banana", "bat"]

        mode_text = Text("Insert", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)
        info_text = Text(f"Words: {words}", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN)
        result_text = self.make_result_text("")
        self.play(FadeIn(mode_text), FadeIn(info_text), FadeIn(result_text))

        tree_group, node_views = self.build_trie_group(trie.root)
        self.play(FadeIn(tree_group), run_time=0.8)

        for word in words:
            exists_before = trie.search(word)
            missing_idx = self.first_missing_index(trie.root, word)

            self.play(
                Transform(
                    subtitle,
                    self.make_subtitle_group(
                        f"Insert '{word}': follow existing prefix, then create nodes for missing characters."
                    ),
                ),
                Transform(result_text, self.make_result_text("")),
                run_time=0.45,
            )

            trie.insert(word)
            path_nodes, missing_char, terminal = self.trace_path(trie.root, word)
            _ = missing_char
            _ = terminal
            highlight_ids = {id(n) for n in path_nodes}
            new_ids = set()
            if missing_idx is not None:
                for node in path_nodes[missing_idx + 1 :]:
                    new_ids.add(id(node))

            new_tree_group, new_node_views = self.build_trie_group(
                trie.root,
                highlight_ids=highlight_ids,
                new_ids=new_ids,
            )
            self.play(ReplacementTransform(tree_group, new_tree_group), run_time=insert_step_time)
            tree_group = new_tree_group
            node_views = new_node_views

            for node in path_nodes:
                group = node_views[id(node)]
                self.play(Indicate(group, color=NODE_ACTIVE), run_time=walk_step_time)

            if exists_before:
                msg = f"'{word}' was already in the trie. End flag stays True."
            else:
                msg = f"'{word}' inserted. Final node is marked as end-of-word."
            self.play(
                Transform(result_text, self.make_result_text(msg)),
                run_time=0.45,
            )
            self.wait(0.45)

        self.play(
            Transform(mode_text, Text("Search", font_size=30).next_to(title, DOWN)),
            Transform(info_text, Text("search(word) returns True only for a full word", font_size=24).next_to(mode_text, DOWN)),
            Transform(result_text, self.make_result_text("")),
            Transform(
                subtitle,
                self.make_subtitle_group(
                    "Search checks each character path, then verifies the end-of-word flag at the final node."
                ),
            ),
            run_time=0.6,
        )

        search_cases = ["apple", "apr", "bat", "bath"]
        for word in search_cases:
            path_nodes, missing_char, terminal = self.trace_path(trie.root, word)
            ok = missing_char is None and terminal is not None and terminal.is_end_of_word

            highlight_ids = {id(n) for n in path_nodes}
            new_tree_group, new_node_views = self.build_trie_group(
                trie.root,
                highlight_ids=highlight_ids,
                failed=not ok,
            )
            self.play(ReplacementTransform(tree_group, new_tree_group), run_time=0.65)
            tree_group = new_tree_group
            node_views = new_node_views

            self.play(
                Transform(
                    subtitle,
                    self.make_subtitle_group(f"search('{word}') walks the path and checks terminal end flag."),
                ),
                run_time=0.4,
            )
            for node in path_nodes:
                self.play(Indicate(node_views[id(node)], color=EDGE_ACTIVE), run_time=walk_step_time)

            if missing_char is not None:
                msg = f"search('{word}') = False (missing '{missing_char}')"
            elif terminal is None or not terminal.is_end_of_word:
                msg = f"search('{word}') = False (path exists but not a full word)"
            else:
                msg = f"search('{word}') = True"
            self.play(Transform(result_text, self.make_result_text(msg)), run_time=0.45)
            self.wait(0.5)

        self.play(
            Transform(mode_text, Text("Starts With", font_size=30).next_to(title, DOWN)),
            Transform(info_text, Text("starts_with(prefix) only needs a valid path", font_size=24).next_to(mode_text, DOWN)),
            Transform(result_text, self.make_result_text("")),
            Transform(
                subtitle,
                self.make_subtitle_group(
                    "starts_with is successful as long as every prefix character can be traced."
                ),
            ),
            run_time=0.6,
        )

        prefix_cases = ["ap", "ban", "cat", "ba"]
        for prefix in prefix_cases:
            path_nodes, missing_char, _ = self.trace_path(trie.root, prefix)
            ok = missing_char is None

            highlight_ids = {id(n) for n in path_nodes}
            new_tree_group, new_node_views = self.build_trie_group(
                trie.root,
                highlight_ids=highlight_ids,
                failed=not ok,
            )
            self.play(ReplacementTransform(tree_group, new_tree_group), run_time=0.65)
            tree_group = new_tree_group
            node_views = new_node_views

            self.play(
                Transform(
                    subtitle,
                    self.make_subtitle_group(f"starts_with('{prefix}') checks whether the prefix path exists."),
                ),
                run_time=0.4,
            )
            for node in path_nodes:
                self.play(Indicate(node_views[id(node)], color=NODE_ACTIVE), run_time=walk_step_time)

            if missing_char is None:
                msg = f"starts_with('{prefix}') = True"
            else:
                msg = f"starts_with('{prefix}') = False (missing '{missing_char}')"
            self.play(Transform(result_text, self.make_result_text(msg)), run_time=0.45)
            self.wait(0.5)

        self.play(
            Transform(
                subtitle,
                self.make_subtitle_group(
                    "Demo complete: insert builds structure, search validates full words, starts_with checks prefixes only."
                ),
            ),
            run_time=0.5,
        )
        self.wait(1.2)

    def first_missing_index(self, root, word):
        current = root
        for idx, char in enumerate(word):
            if char not in current.children:
                return idx
            current = current.children[char]
        return None

    def trace_path(self, root, text):
        current = root
        path = [root]
        for char in text:
            if char not in current.children:
                return path, char, None
            current = current.children[char]
            path.append(current)
        return path, None, current

    def make_subtitle_group(self, content):
        text = Text(content, font_size=24)
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
        text = Text(content, font_size=22)
        max_width = config.frame_width * 0.42
        if text.width > max_width:
            text.scale_to_fit_width(max_width)
        text.to_corner(UR).shift(LEFT * 0.35 + DOWN * 1.2)
        return text

    def collect_layout(self, root):
        layout = {}

        def dfs(node, char, depth, x0, x1, parent):
            children = sorted(node.children.items(), key=lambda item: item[0])
            if not children:
                x = (x0 + x1) / 2
                layout[node] = (x, depth, char, parent)
                return x

            width = x1 - x0
            step = width / len(children)
            child_xs = []
            for idx, (child_char, child_node) in enumerate(children):
                seg_l = x0 + idx * step
                seg_r = x0 + (idx + 1) * step
                child_x = dfs(child_node, child_char, depth + 1, seg_l, seg_r, node)
                child_xs.append(child_x)

            x = sum(child_xs) / len(child_xs)
            layout[node] = (x, depth, char, parent)
            return x

        dfs(root, "ROOT", 0, -6.0, 6.0, None)
        return layout

    def build_trie_group(self, root, highlight_ids=None, new_ids=None, failed=False):
        highlight_ids = highlight_ids or set()
        new_ids = new_ids or set()
        layout = self.collect_layout(root)
        max_depth = max(depth for _, depth, _, _ in layout.values())

        top_y = 1.35
        bottom_y = -2.35
        depth_step = (top_y - bottom_y) / max(1, max_depth)

        def y_of(depth):
            return top_y - depth * depth_step

        edges = VGroup()
        nodes = VGroup()
        node_views = {}

        for node, (x, depth, _char, parent) in layout.items():
            if parent is None:
                continue
            px, pdepth, _, _ = layout[parent]
            p = [px, y_of(pdepth), 0]
            q = [x, y_of(depth), 0]
            edge_color = RED_D if failed and id(node) in highlight_ids else TEXT_MUTED
            edges.add(Line(p, q, stroke_width=3, color=edge_color))

        for node, (x, depth, char, _parent) in layout.items():
            center = [x, y_of(depth), 0]
            fill = NODE_NEUTRAL
            if id(node) in highlight_ids:
                fill = NODE_ACTIVE
            if id(node) in new_ids:
                fill = EDGE_ACTIVE

            circle = Circle(radius=0.27, color=WHITE, stroke_width=2)
            circle.set_fill(fill, opacity=1.0)

            label_text = "*" if char == "ROOT" else char
            label = Text(label_text, font_size=22).move_to(ORIGIN)

            group = VGroup(circle, label)
            if node.is_end_of_word:
                end_mark = Dot(point=[0.22, 0.22, 0], radius=0.05, color=NODE_LEAF)
                group.add(end_mark)

            group.move_to(center)

            nodes.add(group)
            node_views[id(node)] = group

        return VGroup(edges, nodes), node_views