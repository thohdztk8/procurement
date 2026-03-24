import unittest

class TestAuthentication(unittest.TestCase):

    def setUp(self):
        # Setup code to prepare for tests
        self.valid_username = 'testuser'
        self.valid_password = 'testpass'
        self.invalid_username = 'wronguser'
        self.invalid_password = 'wrongpass'

    def test_login_with_valid_credentials(self):
        # Simulate a login with valid credentials and check if login is successful
        response = authenticate(self.valid_username, self.valid_password)
        self.assertTrue(response['success'])

    def test_login_with_invalid_username(self):
        # Test login with an invalid username
        response = authenticate(self.invalid_username, self.valid_password)
        self.assertFalse(response['success'])
        self.assertEqual(response['message'], 'Invalid username or password.')

    def test_login_with_invalid_password(self):
        # Test login with an invalid password
        response = authenticate(self.valid_username, self.invalid_password)
        self.assertFalse(response['success'])
        self.assertEqual(response['message'], 'Invalid username or password.')

    def test_login_with_empty_username(self):
        # Test login with empty username
        response = authenticate('', self.valid_password)
        self.assertFalse(response['success'])
        self.assertEqual(response['message'], 'Username is required.')

    def test_login_with_empty_password(self):
        # Test login with empty password
        response = authenticate(self.valid_username, '')
        self.assertFalse(response['success'])
        self.assertEqual(response['message'], 'Password is required.')

    def tearDown(self):
        # Clean up after tests
        pass

if __name__ == '__main__':
    unittest.main()