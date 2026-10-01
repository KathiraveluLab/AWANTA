import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules', 'measurements_client')))
from MeasurementsClient import validate_config


VALID_CONFIG = {
    "Target": "99.79.30.74",
    "NoOfProbes": 500,
    "From": ["US", "IN", "GB"],
    "Measure": "ping",
    "Me": "2600:1700:c710:4f10:1:f7ff:fece:8b21",
    "Packets": 1,
    "Size": 2048,
}


class TestValidateConfig(unittest.TestCase):
    def test_valid_config_passes(self):
        # Should not raise
        validate_config(dict(VALID_CONFIG))

    def test_missing_key_raises(self):
        config = dict(VALID_CONFIG)
        del config["Target"]
        with self.assertRaises(ValueError) as ctx:
            validate_config(config)
        self.assertIn("Missing required key: 'Target'", str(ctx.exception))

    def test_wrong_type_raises(self):
        config = dict(VALID_CONFIG)
        config["NoOfProbes"] = "500"  # should be int, not str
        with self.assertRaises(ValueError) as ctx:
            validate_config(config)
        self.assertIn("'NoOfProbes' should be of type int", str(ctx.exception))

    def test_empty_target_raises(self):
        config = dict(VALID_CONFIG)
        config["Target"] = "   "
        with self.assertRaises(ValueError) as ctx:
            validate_config(config)
        self.assertIn("'Target' cannot be an empty string", str(ctx.exception))

    def test_empty_from_list_raises(self):
        config = dict(VALID_CONFIG)
        config["From"] = []
        with self.assertRaises(ValueError) as ctx:
            validate_config(config)
        self.assertIn("'From' cannot be an empty list", str(ctx.exception))

    def test_invalid_country_code_raises(self):
        config = dict(VALID_CONFIG)
        config["From"] = ["USA"]  # 3 letters, not 2
        with self.assertRaises(ValueError) as ctx:
            validate_config(config)
        self.assertIn("2-letter country codes", str(ctx.exception))

    def test_negative_no_of_probes_raises(self):
        config = dict(VALID_CONFIG)
        config["NoOfProbes"] = -5
        with self.assertRaises(ValueError) as ctx:
            validate_config(config)
        self.assertIn("'NoOfProbes' must be a positive integer", str(ctx.exception))

    def test_multiple_errors_collected_together(self):
        config = {"Target": "", "NoOfProbes": -1}
        with self.assertRaises(ValueError) as ctx:
            validate_config(config)
        message = str(ctx.exception)
        self.assertIn("Missing required key: 'From'", message)
        self.assertIn("Missing required key: 'Measure'", message)
        self.assertIn("'NoOfProbes' must be a positive integer", message)


if __name__ == "__main__":
    unittest.main()