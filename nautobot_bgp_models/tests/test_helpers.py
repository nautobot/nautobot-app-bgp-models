"""Unit test automation for Helper methods in nautobot_bgp_models."""

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from nautobot.extras.models import Status

from nautobot_bgp_models import models
from nautobot_bgp_models.helpers import add_available_asns


class AddAvailableAsns(TestCase):
    """Test BGP helper methods."""

    @classmethod
    def setUpTestData(cls):
        """One-time class data setup."""
        status_active = Status.objects.get(name__iexact="active")
        status_active.content_types.add(ContentType.objects.get_for_model(models.AutonomousSystem))

        cls.range_50_60 = models.AutonomousSystemRange.objects.create(
            name="Range 50 60", asn_min=50, asn_max=60, description="Test Description 1"
        )

        cls.range_90_120 = models.AutonomousSystemRange.objects.create(
            name="Range 90 120", asn_min=90, asn_max=120, description="Test Description 2"
        )

        cls.range_100_110 = models.AutonomousSystemRange.objects.create(
            name="Range 100 110", asn_min=100, asn_max=110, description="Test Description 3"
        )
        cls.asn_100 = models.AutonomousSystem.objects.create(asn=100, status=status_active)
        cls.asn_110 = models.AutonomousSystem.objects.create(asn=110, status=status_active)

    def test_range_boundary(self):
        """Test asns availability - boundary."""
        instance = self.range_100_110
        asns = models.AutonomousSystem.objects.filter(asn__gte=instance.asn_min, asn__lte=instance.asn_max)
        expected_availability = [
            self.asn_100,
            {"asn": 101, "available": 9},
            self.asn_110,
        ]

        self.assertEqual(expected_availability, add_available_asns(instance=instance, asns=asns))

    def test_range_middle(self):
        """Test asns availability - middle."""
        instance = self.range_90_120
        asns = models.AutonomousSystem.objects.filter(asn__gte=instance.asn_min, asn__lte=instance.asn_max)
        expected_availability = [
            {"asn": 90, "available": 10},
            self.asn_100,
            {"asn": 101, "available": 9},
            self.asn_110,
            {"asn": 111, "available": 10},
        ]

        self.assertEqual(expected_availability, add_available_asns(instance=instance, asns=asns))

    def test_range_empty(self):
        """Test asns availability - empty."""
        instance = self.range_50_60
        asns = models.AutonomousSystem.objects.filter(asn__gte=instance.asn_min, asn__lte=instance.asn_max)
        expected_availability = [
            {"asn": 50, "available": 11},
        ]

        self.assertEqual(expected_availability, add_available_asns(instance=instance, asns=asns))
