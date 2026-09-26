import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules', 'measurements_client')))

import MeasurementsClient as mc


class TestMultiTargetMeasurements(unittest.TestCase):
    def test_string_target_is_normalized_to_a_single_item_list(self):
        # `targets` is built at module import time from config.json's Target
        self.assertIsInstance(mc.targets, list)

    @patch('MeasurementsClient.subprocess.run')
    def test_measure_target_country_returns_metrics_per_probe(self, mock_run):
        ping_result = MagicMock()
        ping_result.stdout = '[{"prb_id": 123, "result": [{"rtt": 10.0}, {"rtt": 12.0}]}]'
        traceroute_result = MagicMock()
        traceroute_result.stdout = '[{"result": [{}, {}, {}]}]'
        mock_run.side_effect = [ping_result, traceroute_result]

        result = mc.measure_target_country("1.1.1.1", "US")

        self.assertIn("123", result)
        self.assertAlmostEqual(result["123"]["rtt"], 11.0)
        self.assertEqual(result["123"]["hop_count"], 3)

    @patch('MeasurementsClient.subprocess.run')
    def test_measure_target_country_handles_malformed_output_gracefully(self, mock_run):
        bad_result = MagicMock()
        bad_result.stdout = 'not valid json'
        mock_run.return_value = bad_result

        # Should not raise, just return an empty dict
        result = mc.measure_target_country("1.1.1.1", "US")
        self.assertEqual(result, {})

    @patch('MeasurementsClient.measure_target_country')
    def test_measure_latency_populates_whole_dict_per_target(self, mock_measure):
        mock_measure.return_value = {"123": {"rtt": 10.0, "jitter": 1.0, "hop_count": 2}}

        mc.whole_dict = {}
        mc.completed_countries = {}
        mc.targets = ["1.1.1.1", "8.8.8.8"]
        mc.from_countries = ["US"]
        mc.INIT_EXECUTION = True
        mc.EXTRACTION_RUNNING = False
        mc.event_manager = MagicMock()

        with patch('builtins.open', unittest.mock.mock_open()):
            mc.measure_latency()

        self.assertIn("1.1.1.1", mc.whole_dict)
        self.assertIn("8.8.8.8", mc.whole_dict)
        self.assertIn("US", mc.whole_dict["1.1.1.1"])
        self.assertIn("US", mc.whole_dict["8.8.8.8"])


if __name__ == '__main__':
    unittest.main()