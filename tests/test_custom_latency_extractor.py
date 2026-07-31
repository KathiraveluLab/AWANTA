import sys
import os
import json
import shutil
import tempfile
import unittest

# Add modules to path, matching the convention used by test_event_trace_manager.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules', 'emulator')))

from src.trace_manager.custom_latency_extractor import CustomLatencyExtractor
from src.trace_manager.Measurement import Measurement
from src.exceptions.exceptions import ExtensionError
from src.utils.utils import file_splitter


class TestCustomLatencyExtractor(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_trace_file(self, filename, values):
        path = os.path.join(self.temp_dir, filename)
        with open(path, 'w') as f:
            json.dump(values, f)

    def test_process_files_loads_measurements_for_each_node(self):
        self._write_trace_file('1.json', [10.5, 12.3])
        self._write_trace_file('2.json', [20.1, 22.4])

        extractor = CustomLatencyExtractor(self.temp_dir)
        extractor.process_files()

        self.assertIn('1', extractor.measurements)
        self.assertIn('2', extractor.measurements)

    def test_get_next_state_returns_measurements_in_lockstep(self):
        self._write_trace_file('1.json', [10.5, 12.3])
        self._write_trace_file('2.json', [20.1, 22.4])

        extractor = CustomLatencyExtractor(self.temp_dir)
        extractor.process_files()

        first_state = extractor.get_next_state()
        self.assertEqual(len(first_state), 2)
        for m in first_state:
            self.assertIsInstance(m, Measurement)
        metrics_first = sorted(m.metric for m in first_state)
        self.assertEqual(metrics_first, [10.5, 20.1])

        second_state = extractor.get_next_state()
        metrics_second = sorted(m.metric for m in second_state)
        self.assertEqual(metrics_second, [12.3, 22.4])

    def test_get_next_state_returns_none_when_exhausted(self):
        self._write_trace_file('1.json', [10.5])

        extractor = CustomLatencyExtractor(self.temp_dir)
        extractor.process_files()

        first_state = extractor.get_next_state()
        self.assertIsNotNone(first_state)

        second_state = extractor.get_next_state()
        self.assertIsNone(second_state)

    def test_measurement_src_matches_filename_key(self):
        self._write_trace_file('3.json', [99.9])

        extractor = CustomLatencyExtractor(self.temp_dir)
        extractor.process_files()

        state = extractor.get_next_state()
        self.assertEqual(state[0].src, 3)
        self.assertEqual(state[0].metric, 99.9)

    def test_process_files_handles_missing_directory_gracefully(self):
        extractor = CustomLatencyExtractor('/path/does/not/exist')
        # Should not raise, per the IOError handling in process_files
        extractor.process_files()
        self.assertEqual(extractor.measurements, {})

    def test_file_splitter_valid_json_file(self):
        self.assertEqual(file_splitter('5.json'), '5')

    def test_file_splitter_raises_clear_error_for_invalid_extension(self):
        with self.assertRaises(ExtensionError) as ctx:
            file_splitter('5.txt')
        self.assertIn('5.txt', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()