"""Test autonomoussystem forms."""

from django.test import TestCase

from nautobot_bgp_models import forms


class AutonomousSystemTest(TestCase):
    """Test AutonomousSystem forms."""

    def test_specifying_all_fields_success(self):
        form = forms.AutonomousSystemForm(
            data={
                "name": "Development",
                "description": "Development Testing",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_specifying_only_required_success(self):
        form = forms.AutonomousSystemForm(
            data={
                "name": "Development",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_validate_name_autonomoussystem_is_required(self):
        form = forms.AutonomousSystemForm(data={"description": "Development Testing"})
        self.assertFalse(form.is_valid())
        self.assertIn("This field is required.", form.errors["name"])
