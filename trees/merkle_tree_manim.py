from __future__ import annotations

from pathlib import Path
import sys

from manim import *

try:
    from common.color import BG_DARK, EDGE_ACTIVE, NODE_ACTIVE, NODE_LEAF, NODE_NEUTRAL, TEXT_MUTED
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from common.color import BG_DARK, EDGE_ACTIVE, NODE_ACTIVE, NODE_LEAF, NODE_NEUTRAL, TEXT_MUTED

from merkle_tree import MerkleTree


class MerkleTreeAnim(Scene):
    def construct(self):
        self.camera.background_color = BG_DARK
        self.subtitle_font = "Arial"

        pace = 1.12

        def t(seconds: float) -> float:
            return seconds * pace

        blocks = [
            "tx1: Alice -> Bob 10",
            "tx2: Bob -> Carol 5",
            "tx3: Carol -> Dave 2",
            "tx4: Dave -> Erin 1",
            "tx5: Erin -> Frank 8",
        ]

        tree = MerkleTree(blocks, algorithm="sha256")

        title = Text("Merkle Tree", font_size=46, color=NODE_ACTIVE).to_edge(UP)
        self.play(Write(title))

        subtitle = self.make_subtitle_group(
            "Leaves are transaction hashes; each parent hash commits to both children."
        )
        self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=t(0.55))

        mode_text = Text("Build", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)
        info_text = Text("algorithm=sha256 | odd levels duplicate last hash", font_size=23, color=TEXT_MUTED)
        info_text.next_to(mode_text, DOWN)
        result_text = self.make_result_text("")
        self.play(FadeIn(mode_text), FadeIn(info_text), FadeIn(result_text))

        tree_group = self.build_merkle_group(tree, leaf_labels=self.leaf_tags(blocks))
        self.play(FadeIn(tree_group), run_time=t(0.8))

        self.play(
            Transform(
                subtitle,
                self.make_subtitle_group("Built from 5 blocks. Root hash is the single top hash."),
            ),
            Transform(result_text, self.make_result_text(f"Leaf count={len(tree)} | Root={self.short_hex(tree.root_hex)}")),
            run_time=t(0.55),
        )
        self.wait(t(0.25))

        # Proof demo from main(): idx = 2
        idx = 2
        target = blocks[idx]
        proof = tree.get_proof(idx)
        path_nodes, sibling_nodes = self.proof_nodes(tree, idx)

        self.play(
            Transform(mode_text, Text("Proof", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info_text, Text(f"target index={idx}", font_size=23, color=TEXT_MUTED).next_to(mode_text, DOWN)),
            Transform(
                subtitle,
                self.make_subtitle_group("Merkle proof uses sibling hashes along the path from leaf to root."),
            ),
            run_time=t(0.55),
        )

        proof_group = self.build_merkle_group(
            tree,
            leaf_labels=self.leaf_tags(blocks),
            active_nodes=path_nodes,
            sibling_nodes=sibling_nodes,
        )
        self.play(ReplacementTransform(tree_group, proof_group), run_time=t(0.9))
        tree_group = proof_group

        for level, cur_idx, sib_idx in self.proof_steps(idx, tree):
            step_group = self.build_merkle_group(
                tree,
                leaf_labels=self.leaf_tags(blocks),
                active_nodes={(level, cur_idx), (level, sib_idx), (level + 1, cur_idx // 2)},
                sibling_nodes=sibling_nodes,
            )
            self.play(ReplacementTransform(tree_group, step_group), run_time=t(0.6))
            tree_group = step_group

        ok = MerkleTree.verify_proof(target, proof, tree.root_hash, algorithm="sha256")
        self.play(
            Transform(result_text, self.make_result_text(f"verify_proof(target) -> {ok}")),
            run_time=t(0.45),
        )
        self.wait(t(0.25))

        # Tamper test from main
        fake = "tx3: Carol -> Dave 2000"
        tampered_ok = MerkleTree.verify_proof(fake, proof, tree.root_hash, algorithm="sha256")

        self.play(
            Transform(mode_text, Text("Tamper Test", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info_text, Text("same proof, modified leaf data", font_size=23, color=TEXT_MUTED).next_to(mode_text, DOWN)),
            Transform(
                subtitle,
                self.make_subtitle_group("Changing leaf content changes leaf hash, so reconstructed root no longer matches."),
            ),
            run_time=t(0.55),
        )

        tamper_group = self.build_merkle_group(
            tree,
            leaf_labels=self.leaf_tags(blocks),
            active_nodes=path_nodes,
            sibling_nodes=sibling_nodes,
            failed=True,
        )
        self.play(ReplacementTransform(tree_group, tamper_group), run_time=t(0.8))
        tree_group = tamper_group
        self.play(
            Transform(result_text, self.make_result_text(f"tampered proof valid -> {tampered_ok}")),
            run_time=t(0.45),
        )
        self.wait(t(0.25))

        # Update leaf from main
        old_root = tree.root_hex
        tree.update_leaf(1, "tx2: Bob -> Carol 999")
        new_root = tree.root_hex
        changed = old_root != new_root

        self.play(
            Transform(mode_text, Text("Update Leaf", font_size=30, color=TEXT_MUTED).next_to(title, DOWN)),
            Transform(info_text, Text("update_leaf(1, 'tx2: Bob -> Carol 999')", font_size=23, color=TEXT_MUTED).next_to(mode_text, DOWN)),
            Transform(
                subtitle,
                self.make_subtitle_group("Updating one leaf rehashes its path upward and changes the root commitment."),
            ),
            run_time=t(0.55),
        )

        updated_labels = [b.decode("utf-8") for b in tree.blocks]
        updated_group = self.build_merkle_group(tree, leaf_labels=self.leaf_tags(updated_labels))
        self.play(ReplacementTransform(tree_group, updated_group), run_time=t(0.95))
        tree_group = updated_group
        self.play(
            Transform(
                result_text,
                self.make_result_text(
                    f"Old root={self.short_hex(old_root)} | New root={self.short_hex(new_root)} | changed={changed}"
                ),
            ),
            run_time=t(0.5),
        )

        self.play(
            Transform(
                subtitle,
                self.make_subtitle_group("Done: Merkle tree enables efficient inclusion proofs and tamper detection."),
            ),
            run_time=t(0.5),
        )
        self.wait(t(1.0))

    def leaf_tags(self, blocks):
        tags = []
        for i, b in enumerate(blocks):
            text = b.decode("utf-8") if isinstance(b, bytes) else str(b)
            head = text.split(":", 1)[0]
            tags.append(f"{i}:{head}")
        return tags

    def proof_steps(self, index: int, tree: MerkleTree):
        idx = index
        steps = []
        for level in range(len(tree.levels) - 1):
            nodes = tree.levels[level]
            sib_idx = idx - 1 if idx % 2 == 1 else idx + 1
            if sib_idx >= len(nodes):
                sib_idx = idx
            steps.append((level, idx, sib_idx))
            idx //= 2
        return steps

    def proof_nodes(self, tree: MerkleTree, index: int):
        active = set()
        siblings = set()
        idx = index
        for level in range(len(tree.levels) - 1):
            nodes = tree.levels[level]
            sib_idx = idx - 1 if idx % 2 == 1 else idx + 1
            if sib_idx >= len(nodes):
                sib_idx = idx
            active.add((level, idx))
            active.add((level + 1, idx // 2))
            siblings.add((level, sib_idx))
            idx //= 2
        return active, siblings

    def build_merkle_group(self, tree: MerkleTree, leaf_labels=None, active_nodes=None, sibling_nodes=None, failed=False):
        leaf_labels = leaf_labels or []
        active_nodes = active_nodes or set()
        sibling_nodes = sibling_nodes or set()

        panel = RoundedRectangle(corner_radius=0.1, width=12.1, height=5.95, stroke_color=NODE_NEUTRAL, stroke_width=1.5)
        panel.set_fill(BLACK, opacity=0.22)
        panel.move_to([0, -0.35, 0])

        caption = Text("Level 0 = leaf hashes | Top = root hash", font_size=17, color=TEXT_MUTED).next_to(panel, UP, buff=0.08)

        # layout
        level_count = len(tree.levels)
        y_bottom = -2.55
        y_top = 1.65
        y_step = (y_top - y_bottom) / max(1, level_count - 1)

        positions = {}
        for level, nodes in enumerate(tree.levels):
            y = y_bottom + level * y_step
            n = len(nodes)
            left, right = -5.25, 5.25
            if n == 1:
                xs = [0.0]
            else:
                step = (right - left) / (n - 1)
                xs = [left + i * step for i in range(n)]
            for i, x in enumerate(xs):
                positions[(level, i)] = (x, y)

        edges = VGroup()
        nodes_group = VGroup()
        labels = VGroup()

        # edges from level 0 upward
        for level in range(level_count - 1):
            child_count = len(tree.levels[level])
            parent_count = len(tree.levels[level + 1])
            for p in range(parent_count):
                li = 2 * p
                ri = min(2 * p + 1, child_count - 1)
                px, py = positions[(level + 1, p)]

                for ci in {li, ri}:
                    cx, cy = positions[(level, ci)]
                    col = TEXT_MUTED
                    if (level, ci) in active_nodes or (level + 1, p) in active_nodes:
                        col = EDGE_ACTIVE if not failed else RED_D
                    edges.add(Line([cx, cy, 0], [px, py, 0], color=col, stroke_width=2.2))

        for level, lvl_nodes in enumerate(tree.levels):
            for i, h in enumerate(lvl_nodes):
                x, y = positions[(level, i)]

                if failed and (level, i) in active_nodes:
                    fill = RED_D
                    txt_col = WHITE
                elif (level, i) in active_nodes:
                    fill = NODE_ACTIVE
                    txt_col = BG_DARK
                elif (level, i) in sibling_nodes:
                    fill = EDGE_ACTIVE
                    txt_col = BG_DARK
                elif level == 0:
                    fill = NODE_NEUTRAL
                    txt_col = WHITE
                elif level == level_count - 1:
                    fill = NODE_LEAF
                    txt_col = WHITE
                else:
                    fill = NODE_NEUTRAL
                    txt_col = WHITE

                box = RoundedRectangle(corner_radius=0.08, width=1.75, height=0.46, stroke_color=WHITE, stroke_width=1.6)
                box.set_fill(fill, opacity=0.9)
                box.move_to([x, y, 0])

                text = Text(self.short_hex(h.hex()), font_size=14, color=txt_col)
                text.move_to(box.get_center())

                nodes_group.add(box)
                labels.add(text)

                if level == 0 and i < len(leaf_labels):
                    tag = Text(leaf_labels[i], font_size=12, color=TEXT_MUTED)
                    tag.next_to(box, DOWN, buff=0.05)
                    labels.add(tag)

        return VGroup(panel, caption, edges, nodes_group, labels)

    def short_hex(self, h: str):
        if len(h) <= 16:
            return h
        return f"{h[:8]}..{h[-8:]}"

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
        max_width = config.frame_width * 0.46
        if text.width > max_width:
            text.scale_to_fit_width(max_width)
        text.to_corner(UL).shift(RIGHT * 0.3 + DOWN * 1.85)
        return text

