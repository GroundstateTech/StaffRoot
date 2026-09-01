import unittest

from core.security import hash_password, verify_password


class PasswordTests(unittest.TestCase):
    def test_password_hashes_are_salted_and_verify(self):
        first = hash_password("correct horse battery staple")
        second = hash_password("correct horse battery staple")
        self.assertNotEqual(first, second)
        self.assertTrue(verify_password("correct horse battery staple", first))
        self.assertFalse(verify_password("wrong password", first))

    def test_malformed_hash_is_rejected(self):
        self.assertFalse(verify_password("anything", "not-a-valid-hash"))


if __name__ == "__main__":
    unittest.main()
