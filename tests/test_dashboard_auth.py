import base64
import unittest

from bot import is_authorized


class DashboardAuthTests(unittest.TestCase):
    def test_missing_header_is_rejected(self):
        self.assertFalse(is_authorized(None, "peak", "a-long-test-password"))

    def test_wrong_scheme_is_rejected(self):
        self.assertFalse(is_authorized("Bearer abc", "peak", "a-long-test-password"))

    def test_malformed_base64_is_rejected(self):
        self.assertFalse(is_authorized("Basic !!!", "peak", "a-long-test-password"))

    def test_wrong_password_is_rejected(self):
        raw = base64.b64encode(b"peak:wrong-password").decode("ascii")
        self.assertFalse(is_authorized("Basic " + raw, "peak", "a-long-test-password"))

    def test_correct_credentials_are_accepted(self):
        raw = base64.b64encode(b"peak:a-long-test-password").decode("ascii")
        self.assertTrue(is_authorized("Basic " + raw, "peak", "a-long-test-password"))

    def test_missing_configured_password_fails_closed(self):
        raw = base64.b64encode(b"peak:anything").decode("ascii")
        self.assertFalse(is_authorized("Basic " + raw, "peak", ""))


if __name__ == "__main__":
    unittest.main()
