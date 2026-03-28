from .custom_latency_extractor import CustomLatencyExtractor
from .event_trace_manager import EventTraceManager

trace_manager = {
    "custom_latency_extractor": CustomLatencyExtractor,
    "event_trace_manager": EventTraceManager,
}