from __future__ import annotations

from manim import *

from binary_heap import BinaryHeap

# Match suffix_tree_manim palette
BG_DARK = "#121317"
TEXT_MUTED = "#8E929D"
NODE_NEUTRAL = "#2A3B49"
NODE_ACTIVE = "#00E5FF"
EDGE_ACTIVE = "#FFB000"
NODE_LEAF = "#2E7D32"


class BinaryHeapAnim(Scene):
    def construct(self):
        self.camera.background_color = BG_DARK
        self.subtitle_font = "Arial"

        pace = 1.1

        def t(seconds: float) -> float:
            return seconds * pace

        nums = [10, 4, 7, 1, 3, 20, 15]

        title = Text("Binary Heap", font_size=46, color=NODE_ACTIVE).to_edge(UP)
        self.play(Write(title))

        subtitle = self.make_subtitle_group(
            "A heap is a complete binary tree stored in an array with parent-child order constraints."
        )
        self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=t(0.55))

        mode_text = Text("Min Heap Demo", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)
        info_text = Text(f"input nums = {nums}", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN)
        result_text = self.make_result_text("")
        self.play(FadeIn(mode_text), FadeIn(info_text), FadeIn(result_text))

        h = BinaryHeap(nums, is_min_heap=True)
        heap_group = self.build_heap_group(h.to_list())
        self.play(FadeIn(heap_group), run_time=t(0.8))

        self.play(
            Transform(
                subtitle,
                self.make_subtitle_group("Heapify builds a valid min-heap: each parent is <= both children."),
            ),
            Transform(result_text, self.make_result_text(f"initial heap array: {h.to_list()}")),
            run_time=t(0.5),
        )
        self.wait(t(0.35))

        peek_val = h.peek()
        self.play(
            Transform(subtitle, self.make_subtitle_group("peek() returns root (minimum) without removing it.")),
            Transform(result_text, self.make_result_text(f"peek -> {peek_val}")),
            ReplacementTransform(heap_group, self.build_heap_group(h.to_list(), highlight_indices={0})),
            run_time=t(0.7),
        )
        heap_group = self.build_heap_group(h.to_list(), highlight_indices={0})
        self.wait(t(0.25))

        before = h.to_list()
        h.push(2)
        after = h.to_list()
        changed = self.changed_indices(before, after)
        new_group = self.build_heap_group(after, highlight_indices=changed)
        self.play(
            Transform(subtitle, self.make_subtitle_group("push(2): append to array, then sift up to restore heap order.")),
            ReplacementTransform(heap_group, new_group),
            Transform(result_text, self.make_result_text(f"after push(2): {after}")),
            run_time=t(0.95),
        )
        heap_group = new_group
        self.wait(t(0.25))

        before = h.to_list()
        popped = h.pop()
        after = h.to_list()
        changed = self.changed_indices(before, after)
        new_group = self.build_heap_group(after, highlight_indices=changed)
        self.play(
            Transform(subtitle, self.make_subtitle_group("pop(): remove root, move last element to root, then sift down.")),
            ReplacementTransform(heap_group, new_group),
            Transform(result_text, self.make_result_text(f"pop -> {popped}; heap: {after}")),
            run_time=t(1.15),
        )
        heap_group = new_group
        self.wait(t(0.35))

        self.play(
            Transform(
                subtitle,
                self.make_subtitle_group("Pop all from a min-heap gives ascending order."),
            ),
            run_time=t(0.45),
        )

        pop_seq = []
        while h:
            val = h.pop()
            pop_seq.append(val)
            new_group = self.build_heap_group(h.to_list(), highlight_indices={0} if h else set())
            self.play(
                ReplacementTransform(heap_group, new_group),
                Transform(result_text, self.make_result_text(f"pop sequence: {pop_seq}")),
                run_time=t(0.62),
            )
            heap_group = new_group

        self.wait(t(0.35))

        mh = BinaryHeap(nums, is_min_heap=False)
        heap_group2 = self.build_heap_group(mh.to_list())
        self.play(
            Transform(mode_text, Text("Max Heap Demo", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info_text, Text("same input, max-heap order", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN)),
            Transform(result_text, self.make_result_text(f"initial heap array: {mh.to_list()}")),
            Transform(
                subtitle,
                self.make_subtitle_group("Max-heap keeps the largest element at the root."),
            ),
            ReplacementTransform(heap_group, heap_group2),
            run_time=t(0.85),
        )
        heap_group = heap_group2

        self.play(
            ReplacementTransform(heap_group, self.build_heap_group(mh.to_list(), highlight_indices={0})),
            Transform(result_text, self.make_result_text(f"peek -> {mh.peek()}")),
            run_time=t(0.6),
        )
        heap_group = self.build_heap_group(mh.to_list(), highlight_indices={0})

        max_pop_seq = []
        self.play(
            Transform(subtitle, self.make_subtitle_group("Pop repeatedly from max-heap gives descending order.")),
            run_time=t(0.4),
        )
        while mh:
            val = mh.pop()
            max_pop_seq.append(val)
            new_group = self.build_heap_group(mh.to_list(), highlight_indices={0} if mh else set())
            self.play(
                ReplacementTransform(heap_group, new_group),
                Transform(result_text, self.make_result_text(f"max pop sequence: {max_pop_seq}")),
                run_time=t(0.62),
            )
            heap_group = new_group

        asc = BinaryHeap.heap_sort(nums, ascending=True)
        desc = BinaryHeap.heap_sort(nums, ascending=False)

        self.play(
            Transform(mode_text, Text("Heap Sort", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info_text, Text("heap_sort uses repeated pop from a heap", font_size=24, color=TEXT_MUTED).next_to(mode_text, DOWN)),
            Transform(
                subtitle,
                self.make_subtitle_group("heap_sort(nums, ascending=True/False) builds a heap then pops all elements."),
            ),
            Transform(result_text, self.make_result_text(f"ascending={asc} | descending={desc}")),
            run_time=t(0.8),
        )

        self.wait(t(1.1))

    def changed_indices(self, before, after):
        max_len = max(len(before), len(after))
        changed = set()
        for i in range(max_len):
            bv = before[i] if i < len(before) else None
            av = after[i] if i < len(after) else None
            if bv != av:
                changed.add(i)
        return changed

    def build_heap_group(self, arr, highlight_indices=None):
        highlight_indices = highlight_indices or set()

        nodes = VGroup()
        edges = VGroup()
        array_boxes = VGroup()
        array_labels = VGroup()

        if not arr:
            empty = Text("(heap empty)", font_size=26, color=TEXT_MUTED).move_to([0, 0.2, 0])
            return VGroup(empty)

        positions = {0: (0.0, 1.4)}
        for i in range(1, len(arr)):
            p = (i - 1) // 2
            px, py = positions[p]
            depth = self.node_depth(i)
            gap = max(0.38, 2.7 / (2 ** (depth - 1)))
            if i == 2 * p + 1:
                positions[i] = (px - gap, py - 0.82)
            else:
                positions[i] = (px + gap, py - 0.82)

        for i in range(1, len(arr)):
            p = (i - 1) // 2
            x1, y1 = positions[p]
            x2, y2 = positions[i]
            e_color = EDGE_ACTIVE if (i in highlight_indices or p in highlight_indices) else TEXT_MUTED
            edges.add(Line([x1, y1, 0], [x2, y2, 0], color=e_color, stroke_width=3))

        for i, value in enumerate(arr):
            x, y = positions[i]
            if i in highlight_indices:
                fill = NODE_ACTIVE
            elif i == 0:
                fill = NODE_LEAF
            else:
                fill = NODE_NEUTRAL

            c = Circle(radius=0.24, color=WHITE, stroke_width=2)
            c.set_fill(fill, opacity=1.0)
            label = Text(str(value), font_size=19, color=WHITE)
            nodes.add(VGroup(c, label).move_to([x, y, 0]))

            box = RoundedRectangle(
                corner_radius=0.04,
                width=0.52,
                height=0.38,
                stroke_color=WHITE,
                stroke_width=1.8,
            )
            box_fill = NODE_ACTIVE if i in highlight_indices else NODE_NEUTRAL
            box.set_fill(box_fill, opacity=0.9)
            box.move_to([-5.7 + i * 0.58, -3.2, 0])

            idx_label = Text(str(i), font_size=12, color=TEXT_MUTED).next_to(box, DOWN, buff=0.04)
            val_label = Text(str(value), font_size=15, color=WHITE).move_to(box.get_center())

            array_boxes.add(box)
            array_labels.add(idx_label, val_label)

        array_title = Text("Array Representation", font_size=18, color=TEXT_MUTED).move_to([0, -2.8, 0])
        return VGroup(edges, nodes, array_title, array_boxes, array_labels)

    def node_depth(self, index: int) -> int:
        depth = 0
        i = index
        while i > 0:
            i = (i - 1) // 2
            depth += 1
        return depth

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
