import unittest

from core.config import DEFAULT_LOCAL_CONFIG, normalize_local_config
from core.identity_provider_client import IdentityProviderClient, IdentityProviderError


class StandaloneIdentityTests(unittest.TestCase):
    def test_default_configuration_is_standalone(self):
        self.assertEqual(DEFAULT_LOCAL_CONFIG["identity_base_url"], "")
        self.assertEqual(DEFAULT_LOCAL_CONFIG["identity_api_token"], "")
        self.assertFalse(DEFAULT_LOCAL_CONFIG["identity_sync_enabled"])

    def test_legacy_configuration_migrates_without_losing_values(self):
        migrated = normalize_local_config({
            "admin_center_base_url": "http://127.0.0.1:8000",
            "admin_center_api_key": "legacy-token",
            "sync_enabled": True,
        })
        self.assertEqual(migrated["identity_base_url"], "http://127.0.0.1:8000")
        self.assertEqual(migrated["identity_api_token"], "legacy-token")
        self.assertTrue(migrated["identity_sync_enabled"])
        self.assertNotIn("admin_center_base_url", migrated)

    def test_current_keys_take_precedence_over_legacy_keys(self):
        migrated = normalize_local_config({
            "identity_base_url": "https://directory.example",
            "admin_center_base_url": "http://legacy.invalid",
        })
        self.assertEqual(migrated["identity_base_url"], "https://directory.example")

    def test_identity_client_rejects_unsafe_url_schemes(self):
        with self.assertRaises(IdentityProviderError):
            IdentityProviderClient("file:///tmp/directory.json")


if __name__ == "__main__":
    unittest.main()
