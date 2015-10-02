from django.test import TestCase
from django.conf import settings

class SettingsTest(TestCase):
    def test_allowed_crispy_template(self):
        self.assertIn(settings.CRISPY_TEMPLATE_PACK, settings.CRISPY_ALLOWED_TEMPLATE_PACKS)