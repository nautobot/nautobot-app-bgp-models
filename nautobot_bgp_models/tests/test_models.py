"""Test AutonomousSystem."""

from nautobot.apps.testing import ModelTestCases

from nautobot_bgp_models import models
from nautobot_bgp_models.tests import fixtures


class TestAutonomousSystem(ModelTestCases.BaseModelTestCase):
    """Test AutonomousSystem."""

    model = models.AutonomousSystem

    @classmethod
    def setUpTestData(cls):
        """Create test data for AutonomousSystem Model."""
        super().setUpTestData()
        # Create 3 objects for the model test cases.
        fixtures.create_autonomoussystem()

    def test_create_autonomoussystem_only_required(self):
        """Create with only required fields, and validate null description and __str__."""
        autonomoussystem = models.AutonomousSystem.objects.create(name="Development")
        self.assertEqual(autonomoussystem.name, "Development")
        self.assertEqual(autonomoussystem.description, "")
        self.assertEqual(str(autonomoussystem), "Development")

    def test_create_autonomoussystem_all_fields_success(self):
        """Create AutonomousSystem with all fields."""
        autonomoussystem = models.AutonomousSystem.objects.create(name="Development", description="Development Test")
        self.assertEqual(autonomoussystem.name, "Development")
        self.assertEqual(autonomoussystem.description, "Development Test")
