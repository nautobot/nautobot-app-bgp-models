"""Create fixtures for tests."""

from nautobot_bgp_models.models import AutonomousSystem


def create_autonomoussystem():
    """Fixture to create necessary number of AutonomousSystem for tests."""
    AutonomousSystem.objects.create(name="Test One")
    AutonomousSystem.objects.create(name="Test Two")
    AutonomousSystem.objects.create(name="Test Three")
