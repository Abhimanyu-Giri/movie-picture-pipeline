"""Offline regression checks for evidence validation; these are not AWS proof."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "runtime", Path(__file__).resolve().parents[1] / "scripts/verify-runtime.py"
)
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)

BACKEND = "http://backend-test.us-east-1.elb.amazonaws.com"
FRONTEND = "http://frontend-test.us-east-1.elb.amazonaws.com"
MOVIES = json.dumps({"movies": [{"id": 1, "title": "Test movie"}]}).encode()


class RuntimeVerificationTests(unittest.TestCase):
    def test_accepts_classic_and_network_elb_formats(self):
        for value in (BACKEND, "http://backend-test.elb.us-east-1.amazonaws.com"):
            self.assertEqual(runtime.aws_url(value + "/"), value)

    def test_rejects_local_cluster_and_placeholder_urls(self):
        for value in ("http://localhost:5000", "http://backend", "http://example.invalid",
                      BACKEND + "/movies", BACKEND + "?redirect=x", "http://user@" + BACKEND[7:]):
            with self.subTest(value=value), self.assertRaises(ValueError):
                runtime.aws_url(value)

    def run_check(self, api=MOVIES, cors=FRONTEND, bundle=BACKEND.encode(), frontend=FRONTEND):
        def response(url, origin=None):
            if url == BACKEND + "/movies":
                return api, {"Access-Control-Allow-Origin": cors}
            if url == FRONTEND:
                return b'<html><script src="/static/js/main.js"></script></html>', {}
            if url == FRONTEND + "/static/js/main.js":
                return bundle, {}
            raise AssertionError("Unexpected request " + url)

        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            # Failure must remove reports from an older successful verification.
            (output / "checks.json").write_text('{"old": true}')
            (output / "ENDPOINTS.md").write_text("old success")
            with patch.object(runtime, "fetch", side_effect=response), contextlib.redirect_stdout(io.StringIO()):
                try:
                    runtime.verify(BACKEND, frontend, output)
                except ValueError:
                    self.assertFalse((output / "checks.json").exists())
                    self.assertFalse((output / "ENDPOINTS.md").exists())
                    raise
            return json.loads((output / "checks.json").read_text())

    def test_checks_both_endpoints_bundle_and_cors(self):
        checks = self.run_check()
        self.assertTrue(checks["backend_url_found_in_served_javascript"])
        self.assertTrue(checks["cors_allowed"])
        self.assertEqual(checks["movie_count"], 1)

    def test_rejects_empty_movie_list(self):
        with self.assertRaisesRegex(ValueError, "no movie list"):
            self.run_check(api=b'{"movies": []}')

    def test_rejects_wrong_backend_in_served_bundle(self):
        with self.assertRaisesRegex(ValueError, "actual backend URL"):
            self.run_check(bundle=b'fetch("http://localhost:5000/movies")')

    def test_rejects_disallowed_frontend_origin(self):
        with self.assertRaisesRegex(ValueError, "CORS"):
            self.run_check(cors="http://different-origin.example")

    def test_backend_only_check(self):
        checks = self.run_check(frontend=None)
        self.assertEqual(checks["backend_movies_status"], 200)
        self.assertNotIn("frontend_status", checks)


if __name__ == "__main__":
    unittest.main()
