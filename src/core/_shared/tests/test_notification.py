import unittest

from src.core._shared.notification import Notification


class TestNotification(unittest.TestCase):
    def test_init(self):
        notification = Notification()
        self.assertEqual(notification._errors, [])

    def test_should_raise_when_adding_non_string_message(self):
        notification = Notification()
        with self.assertRaises(TypeError):
            notification.add_error(42)

    def test_add_error(self):
        notification = Notification()
        notification.add_error("Error 1")
        notification.add_error("Error 2")
        self.assertEqual(notification._errors, ["Error 1", "Error 2"])

    def test_has_errors(self):
        notification = Notification()
        self.assertFalse(notification.has_errors)
        notification.add_error("Error 1")
        self.assertTrue(notification.has_errors)

    def test_messages(self):
        notification = Notification()
        notification.add_error("Error 1")
        notification.add_error("Error 2")
        expected_message = "Error 1; Error 2"
        self.assertEqual(notification.messages, expected_message)
        self.assertEqual(str(notification), expected_message)

    def test_len(self):
        notification = Notification()
        notification.add_error("Error 1")
        notification.add_error("Error 2")
        self.assertEqual(len(notification), 2)

    def test_clear(self):
        notification = Notification()
        notification.add_error("Error 1")
        notification.add_error("Error 2")
        notification.clear()
        self.assertEqual(len(notification), 0)
