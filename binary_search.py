from manim import *
from manim.scene.scene import Scene
from manim.mobject.mobject import Mobject


class BinarySearch(Scene):
    def construct(self):
        arr = [3, 7, 12, 18, 24, 31, 37, 45, 52, 60, 71, 83]
        target = 50

        # ── 1. Title ──────────────────────────────────────────────────
        title = Text("Binary Search", font_size=40, weight=BOLD)
        subtitle = Text(f"target = {target}", font_size=28, color=YELLOW)
        VGroup(title, subtitle).arrange(DOWN, buff=0.3).to_edge(UP)
        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.3))
        self.wait(0.5)

        # ── 2. Build the array of squares ────────────────────────────
        cell_size = 0.75
        squares = VGroup()
        val_labels = VGroup()
        idx_labels = VGroup()

        for i, v in enumerate(arr):
            sq = Square(side_length=cell_size)
            sq.set_stroke(WHITE, 1.5)
            sq.set_fill(DARK_GRAY, opacity=0.5)
            squares.add(sq)

            val = Text(str(v), font_size=22)
            val_labels.add(val)

            idx = Text(str(i), font_size=14, color=GRAY)
            idx_labels.add(idx)

        squares.arrange(RIGHT, buff=0.1).move_to(ORIGIN)

        for i, (sq, val, idx) in enumerate(zip(squares, val_labels, idx_labels)):
            val.move_to(sq.get_center())
            idx.next_to(sq, DOWN, buff=0.15)

        array_group = VGroup(squares, val_labels, idx_labels)
        self.play(
            LaggedStart(
                *[FadeIn(VGroup(squares[i], val_labels[i], idx_labels[i]), shift=DOWN * 0.2)
                  for i in range(len(arr))],
                lag_ratio=0.07,
            ),
            run_time=1.5,
        )
        self.wait(0.4)

        # ── 3. Pointer arrows: L (low), M (mid), R (high) ────────────
        def make_ptr(label, color):
            arrow = Arrow(start=DOWN * 0.3, end=UP * 0.3, color=color, buff=0.05,
                          stroke_width=3, max_tip_length_to_length_ratio=0.4)
            lbl = Text(label, font_size=18, color=color, weight=BOLD)
            return VGroup(arrow, lbl)

        ptr_lo = make_ptr("L", GREEN)
        ptr_hi = make_ptr("R", RED)
        ptr_mid = make_ptr("M", BLUE)

        def place_ptr(ptr, idx, side="below"):
            """Position a pointer below a given index."""
            sq = squares[idx]
            ptr[0].next_to(sq, DOWN, buff=0.55)
            ptr[1].next_to(ptr[0], DOWN, buff=0.05)
            return ptr

        # ── 4. Status text ────────────────────────────────────────────
        status = Text("", font_size=22).to_edge(DOWN, buff=0.5)

        def update_status(msg, color=WHITE):
            new_status = Text(msg, font_size=22, color=color).to_edge(DOWN, buff=0.5)
            return Transform(status, new_status)

        # ── 5. Binary search loop ─────────────────────────────────────
        lo, hi = 0, len(arr) - 1

        place_ptr(ptr_lo, lo)
        place_ptr(ptr_hi, hi)

        self.play(FadeIn(ptr_lo, shift=UP * 0.2), FadeIn(ptr_hi, shift=UP * 0.2))
        self.add(status)

        step = 0
        while lo <= hi:
            step += 1
            mid = (lo + hi) // 2

            # Place mid pointer
            place_ptr(ptr_mid, mid)
            msg = f"Step {step}: lo={lo}, hi={hi}  →  mid={mid}"
            self.play(
                FadeIn(ptr_mid, shift=UP * 0.15),
                update_status(msg),
                run_time=0.5,
            )

            # Highlight midpoint cell in blue
            self.play(
                squares[mid].animate.set_fill(BLUE, opacity=0.6),
                val_labels[mid].animate.set_color(WHITE),
                run_time=0.4,
            )
            self.wait(0.5)

            if arr[mid] == target:
                # ── Found ──
                self.play(
                    squares[mid].animate.set_fill(GREEN, opacity=0.7),
                    update_status(f"Found {target} at index {mid}!", color=GREEN),
                    run_time=0.6,
                )
                # Flash + scale effect
                self.play(
                    squares[mid].animate.scale(1.25),
                    val_labels[mid].animate.scale(1.25).set_color(GREEN),
                    run_time=0.35,
                )
                self.play(
                    squares[mid].animate.scale(1 / 1.25),
                    val_labels[mid].animate.scale(1 / 1.25),
                    run_time=0.3,
                )
                self.wait(1)
                break

            elif arr[mid] < target:
                # ── Go right: grey-out left half ──
                self.play(
                    update_status(
                        f"arr[{mid}]={arr[mid]} < {target}  →  move L right",
                        color=YELLOW,
                    ),
                    run_time=0.5,
                )
                self.wait(0.4)
                
                # Dim eliminated cells
                elim = VGroup(
                    *[squares[i] for i in range(lo, mid + 1)],
                    *[val_labels[i] for i in range(lo, mid + 1)],
                )
                self.play(elim.animate.set_opacity(0.18), run_time=0.4)

                lo = mid + 1
                new_lo = place_ptr(ptr_lo, lo)
                self.play(
                    Transform(ptr_lo, new_lo),
                    FadeOut(ptr_mid),
                    run_time=0.45,
                )

            else:
                # ── Go left: grey-out right half ──
                self.play(
                    update_status(
                        f"arr[{mid}]={arr[mid]} > {target}  →  move R left",
                        color=ORANGE,
                    ),
                    run_time=0.4,
                )

                elim = VGroup(
                    *[squares[i] for i in range(mid, hi + 1)],
                    *[val_labels[i] for i in range(mid, hi + 1)],
                )

                self.play(elim.animate.set_opacity(0.18), run_time=0.4)

                hi = mid - 1
                new_hi = place_ptr(ptr_hi, hi)
                self.play(
                    Transform(ptr_hi, new_hi),
                    FadeOut(ptr_mid),
                    run_time=0.45,
                )

        else:
            # Target not found
            self.play(
                update_status(f"{target} not found in array.", color=RED),
                run_time=0.5,
            )

        self.wait(2)