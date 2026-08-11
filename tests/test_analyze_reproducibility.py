from __future__ import annotations

import unittest

from scripts.analyze_reproducibility import _sha256_bytes


class ReproducibilityHelperTests(unittest.TestCase):
    def test_byte_hash_is_uppercase_and_stable(self) -> None:
        self.assertEqual(
            _sha256_bytes(b"CIP"),
            "6FFD7437623206029C878CD6CA5B3CD219C15B8C6DA8F3A8D8BD66EE9D8021F8",
        )


if __name__ == "__main__":
    unittest.main()
