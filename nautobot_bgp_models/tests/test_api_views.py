"""Unit tests for nautobot_bgp_models."""

from nautobot.apps.testing import APIViewTestCases

from nautobot_bgp_models import models
from nautobot_bgp_models.tests import fixtures


class AutonomousSystemAPIViewTest(APIViewTestCases.APIViewTestCase):
    # pylint: disable=too-many-ancestors
    """Test the API viewsets for AutonomousSystem."""

    model = models.AutonomousSystem
    create_data = [
        {
            "name": "Test Model 1",
            "description": "test description",
        },
        {
            "name": "Test Model 2",
        },
    ]
    bulk_update_data = {"description": "Test Bulk Update"}

    @classmethod
    def setUpTestData(cls):
        fixtures.create_autonomoussystem()
