import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules', 'event_manager')))

from EventManager import EventManager


class TestEventManagerValidation(unittest.TestCase):
    def test_valid_defaults_do_not_raise(self):
        # Should not raise
        EventManager()

    def test_valid_custom_params_do_not_raise(self):
        # Should not raise
        EventManager(host='broker.example.com', port=61614, destination='/queue/custom')

    def test_empty_host_raises(self):
        with self.assertRaises(ValueError) as ctx:
            EventManager(host='   ')
        self.assertIn("'host' must be a non-empty string", str(ctx.exception))

    def test_non_string_host_raises(self):
        with self.assertRaises(ValueError) as ctx:
            EventManager(host=None)
        self.assertIn("'host' must be a non-empty string", str(ctx.exception))

    def test_non_integer_port_raises(self):
        with self.assertRaises(ValueError) as ctx:
            EventManager(port="61613")
        self.assertIn("'port' must be an integer between 1 and 65535", str(ctx.exception))

    def test_out_of_range_port_raises(self):
        with self.assertRaises(ValueError) as ctx:
            EventManager(port=70000)
        self.assertIn("'port' must be an integer between 1 and 65535", str(ctx.exception))

    def test_zero_port_raises(self):
        with self.assertRaises(ValueError) as ctx:
            EventManager(port=0)
        self.assertIn("'port' must be an integer between 1 and 65535", str(ctx.exception))

    def test_boolean_port_raises(self):
        # bool is technically an int subclass in Python; must not be accepted as a valid port
        with self.assertRaises(ValueError) as ctx:
            EventManager(port=True)
        self.assertIn("'port' must be an integer between 1 and 65535", str(ctx.exception))

    def test_empty_destination_raises(self):
        with self.assertRaises(ValueError) as ctx:
            EventManager(destination='')
        self.assertIn("'destination' must be a non-empty string", str(ctx.exception))

    def test_multiple_invalid_params_collected_together(self):
        with self.assertRaises(ValueError) as ctx:
            EventManager(host='', port=-1, destination='')
        message = str(ctx.exception)
        self.assertIn("'host' must be a non-empty string", message)
        self.assertIn("'port' must be an integer between 1 and 65535", message)
        self.assertIn("'destination' must be a non-empty string", message)


if __name__ == '__main__':
    unittest.main()