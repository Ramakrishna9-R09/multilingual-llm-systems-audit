import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_analysis import graphemes, line_fertility


class AnalysisUnitTests(unittest.TestCase):
    def test_whitespace_split_does_not_create_empty_words(self):
        encode = lambda text: list(text)
        lines = ["a  b"]
        literal = line_fertility(lines, encode, lowercase=False, literal_space=True)
        whitespace = line_fertility(lines, encode, lowercase=False, literal_space=False)
        self.assertEqual(literal["words"], 3)
        self.assertEqual(whitespace["words"], 2)

    def test_grapheme_clusters_keep_a_combining_character_together(self):
        self.assertEqual(graphemes("e\u0301"), 1)

    def test_prepared_corpus_has_no_boundary_whitespace(self):
        corpus = Path(__file__).resolve().parents[1] / "data" / "flores200_devtest"
        for path in corpus.glob("*.txt"):
            for line in path.read_text(encoding="utf-8").splitlines():
                self.assertEqual(line, line.strip(), path.name)


if __name__ == "__main__":
    unittest.main()
