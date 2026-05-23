from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple
import hashlib


def _to_bytes(data: bytes | str) -> bytes:
    return data if isinstance(data, bytes) else data.encode("utf-8")


def _hash(data: bytes, algorithm: str = "sha256") -> bytes:
    h = hashlib.new(algorithm)
    h.update(data)
    return h.digest()


@dataclass(frozen=True)
class MerkleProofStep:
    """
    A single step in a Merkle proof path.
    sibling_hash: hash bytes of sibling node
    is_left_sibling: True if sibling is on the left, False if on the right
    """
    sibling_hash: bytes
    is_left_sibling: bool


class MerkleTree:
    """
    Binary Merkle Tree (Hash Tree).

    - Leaves: H(leaf_data)
    - Parent: H(left_hash || right_hash)
    - If a level has odd count, last node is duplicated (Bitcoin-style padding)

    Supports:
      - root_hash / root_hex
      - get_proof(index)
      - verify_proof(...)
      - verify_leaf(index, data)
      - update_leaf(index, new_data)
    """

    def __init__(self, blocks: List[bytes | str], algorithm: str = "sha256") -> None:
        self.algorithm = algorithm
        self.blocks: List[bytes] = [_to_bytes(b) for b in blocks]
        self.levels: List[List[bytes]] = []  # levels[0] = leaves, levels[-1][0] = root
        self._build()

    # ---------------- Build ----------------

    def _build(self) -> None:
        self.levels = []
        if not self.blocks:
            # empty tree convention: root = hash(empty)
            self.levels = [[_hash(b"", self.algorithm)]]
            return

        leaves = [_hash(b, self.algorithm) for b in self.blocks]
        self.levels.append(leaves)

        cur = leaves
        while len(cur) > 1:
            nxt: List[bytes] = []
            i = 0
            while i < len(cur):
                left = cur[i]
                right = cur[i + 1] if i + 1 < len(cur) else cur[i]  # duplicate last if odd
                parent = _hash(left + right, self.algorithm)
                nxt.append(parent)
                i += 2
            self.levels.append(nxt)
            cur = nxt

    # ---------------- Properties ----------------

    @property
    def root_hash(self) -> bytes:
        return self.levels[-1][0]

    @property
    def root_hex(self) -> str:
        return self.root_hash.hex()

    def __len__(self) -> int:
        return len(self.blocks)

    # ---------------- Proofs ----------------

    def get_proof(self, index: int) -> List[MerkleProofStep]:
        """
        Returns Merkle proof for leaf at `index`.
        Proof does not include the leaf hash itself.
        """
        if index < 0 or index >= len(self.blocks):
            raise IndexError("leaf index out of range")

        proof: List[MerkleProofStep] = []
        idx = index

        # walk from leaves level up to root-1
        for level in range(len(self.levels) - 1):
            nodes = self.levels[level]
            sib_idx = idx - 1 if idx % 2 == 1 else idx + 1

            if sib_idx >= len(nodes):
                sib_idx = idx  # odd-end duplication case

            is_left = sib_idx < idx
            proof.append(MerkleProofStep(sibling_hash=nodes[sib_idx], is_left_sibling=is_left))
            idx //= 2

        return proof

    @staticmethod
    def verify_proof(
        leaf_data: bytes | str,
        proof: List[MerkleProofStep],
        expected_root: bytes | str,
        algorithm: str = "sha256",
        expected_root_is_hex: bool = False,
    ) -> bool:
        """
        Verify a Merkle proof for a leaf against expected root.
        """
        cur = _hash(_to_bytes(leaf_data), algorithm)

        for step in proof:
            if step.is_left_sibling:
                cur = _hash(step.sibling_hash + cur, algorithm)
            else:
                cur = _hash(cur + step.sibling_hash, algorithm)

        if isinstance(expected_root, str):
            root_bytes = bytes.fromhex(expected_root) if expected_root_is_hex else _to_bytes(expected_root)
        else:
            root_bytes = expected_root

        return cur == root_bytes

    def verify_leaf(self, index: int, leaf_data: bytes | str) -> bool:
        """
        Convenience method: verify leaf data at index against current tree root.
        """
        proof = self.get_proof(index)
        return self.verify_proof(
            leaf_data=leaf_data,
            proof=proof,
            expected_root=self.root_hash,
            algorithm=self.algorithm,
        )

    # ---------------- Updates ----------------

    def update_leaf(self, index: int, new_data: bytes | str) -> None:
        """
        Update leaf block and recompute tree.
        (Simple full rebuild; easy and safe. Could be optimized to O(log n) rehash path.)
        """
        if index < 0 or index >= len(self.blocks):
            raise IndexError("leaf index out of range")
        self.blocks[index] = _to_bytes(new_data)
        self._build()

    def append_leaf(self, data: bytes | str) -> None:
        self.blocks.append(_to_bytes(data))
        self._build()

    # ---------------- Helpers ----------------

    def leaf_hashes_hex(self) -> List[str]:
        return [h.hex() for h in self.levels[0]]

    def level_hex(self, level: int) -> List[str]:
        if level < 0 or level >= len(self.levels):
            raise IndexError("level out of range")
        return [h.hex() for h in self.levels[level]]

    def dump(self) -> List[List[str]]:
        """
        Returns all levels as hex strings (level 0 = leaves, last = root).
        """
        return [[h.hex() for h in lvl] for lvl in self.levels]
    
    
    
def main():
    blocks = [
        "tx1: Alice -> Bob 10",
        "tx2: Bob -> Carol 5",
        "tx3: Carol -> Dave 2",
        "tx4: Dave -> Erin 1",
        "tx5: Erin -> Frank 8",
    ]

    tree = MerkleTree(blocks, algorithm="sha256")

    print("=== MERKLE TREE ===")
    print("Leaf count:", len(tree))
    print("Root hash :", tree.root_hex)

    print("\nLeaf hashes:")
    for i, h in enumerate(tree.leaf_hashes_hex()):
        print(f"  [{i}] {h}")

    # Build + verify proof
    idx = 2
    target = blocks[idx]
    proof = tree.get_proof(idx)

    print(f"\n=== PROOF for leaf index {idx} ===")
    print("Data:", target)
    for step_i, step in enumerate(proof):
        side = "LEFT" if step.is_left_sibling else "RIGHT"
        print(f"  step {step_i}: sibling({side})={step.sibling_hash.hex()}")

    ok = MerkleTree.verify_proof(
        leaf_data=target,
        proof=proof,
        expected_root=tree.root_hash,
        algorithm="sha256",
    )
    print("Proof valid:", ok)

    # Tamper test
    fake = "tx3: Carol -> Dave 2000"
    tampered_ok = MerkleTree.verify_proof(
        leaf_data=fake,
        proof=proof,
        expected_root=tree.root_hash,
        algorithm="sha256",
    )
    print("Tampered proof valid:", tampered_ok)

    # Update leaf -> root changes
    old_root = tree.root_hex
    tree.update_leaf(1, "tx2: Bob -> Carol 999")
    new_root = tree.root_hex
    print("\n=== UPDATE LEAF ===")
    print("Old root:", old_root)
    print("New root:", new_root)
    print("Root changed:", old_root != new_root)


if __name__ == "__main__":
    main()