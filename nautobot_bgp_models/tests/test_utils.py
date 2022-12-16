"""Unit test automation for utilities in nautobot_bgp_models."""
from nautobot.utilities.testing import TestCase

from nautobot_bgp_models.utils import expand_as_pattern


class TestUtils(TestCase):
    """Test the utilities."""

    def test_expand_as_pattern(self):
        tests = {
            "[1-9]": list(range(1, 10)),
            "[1,4]": [1, 4],
            "42[1,2]00000[1-9]": list(range(421000001, 421000010)) + list(range(422000001, 422000010)),
        }

        for test, result in tests.items():
            self.assertEqual(result, list(map(int, expand_as_pattern(test))))
