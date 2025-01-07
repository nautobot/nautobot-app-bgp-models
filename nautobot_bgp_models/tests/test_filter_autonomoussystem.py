"""Test AutonomousSystem Filter."""

from django.test import TestCase

from nautobot_bgp_models import filters, models
from nautobot_bgp_models.tests import fixtures


class AutonomousSystemFilterTestCase(TestCase):
    """AutonomousSystem Filter Test Case."""

    queryset = models.AutonomousSystem.objects.all()
    filterset = filters.AutonomousSystemFilterSet

    @classmethod
    def setUpTestData(cls):
        """Setup test data for AutonomousSystem Model."""
        fixtures.create_autonomoussystem()

    def test_q_search_name(self):
        """Test using Q search with name of AutonomousSystem."""
        params = {"q": "Test One"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_invalid(self):
        """Test using invalid Q search for AutonomousSystem."""
        params = {"q": "test-five"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
