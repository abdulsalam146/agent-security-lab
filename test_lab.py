import json
import unittest
from pathlib import Path

from agent_security_lab.core import Case, evaluate, load_cases, markdown_report, run


CASES = Path(__file__).resolve().parents[1] / "cases" / "starter.json"


class LabTests(unittest.TestCase):
    def test_protected_denies_document_tool_call(self):
        case = Case("x", "injection", "answer", "ignore rules", {"tool": "send", "source": "document", "target": "external"}, "deny")
        self.assertEqual(evaluate(case, "protected")["decision"], "deny")
        self.assertEqual(evaluate(case, "baseline")["decision"], "allow")

    def test_user_cannot_read_outside_public_scope(self):
        for target in ("../private/key", "/etc/passwd", "public/../secret", "private/key"):
            case = Case("x", "scope", "read", "", {"tool": "read", "source": "user", "target": target}, "deny")
            self.assertEqual(evaluate(case, "protected")["decision"], "deny")

    def test_controls_allow_public_read_and_answer(self):
        cases = load_cases(CASES)
        for case in cases:
            if case.expected == "allow":
                self.assertTrue(evaluate(case, "protected")["passed"])

    def test_report_matches_results(self):
        result = run(load_cases(CASES))
        self.assertEqual(result["total_cases"], 28)
        self.assertEqual(len(result["results"]), 56)
        self.assertTrue(all(r["passed"] for r in result["results"] if r["mode"] == "protected"))
        self.assertIn("| protected | 28 | 28 | 100% |", markdown_report(result))

    def test_duplicate_ids_rejected(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "cases.json"
            item = json.loads(CASES.read_text())[0]
            path.write_text(json.dumps([item, item]))
            with self.assertRaises(ValueError):
                load_cases(path)


if __name__ == "__main__":
    unittest.main()
