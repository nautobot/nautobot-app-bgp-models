"""Test AutonomousSystem."""

from django.test import TestCase

from nautobot_bgp_models import models


class TestAutonomousSystem(TestCase):
    """Test AutonomousSystem."""

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
