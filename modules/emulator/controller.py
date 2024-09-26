from __future__ import annotations
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.topology import event

from src.routing.routing import Routing
from src.trace_manager.TraceManager import TraceManager
from src.network_manager.network_manager import NetworkManager
from src.trace_manager import trace_manager
from src.routing import routing

from ryu import cfg
from src.utils.constants import *


class Controller(app_manager.RyuApp):

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.network_manager = NetworkManager()
        conf = cfg.CONF
        conf.register_opts([
            cfg.StrOpt('trace_manager', default="custom_latency_extractor", help=('Select the trace manager strategy')),
            cfg.StrOpt('routing', default='latency_relaxing', help=('Select the routing strategy'))])

        self.trace_manager: TraceManager = trace_manager[conf.trace_manager](TraceManagerConstants.PATH)
        self.routing: Routing = routing[conf.routing](self.network_manager, self.datapaths)
        self.monitor_thread = hub.spawn(self._monitor)

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]

        self.logger.info('OFPSwitchFeatures received: '
                          'datapath_id=0x%016x n_buffers=%d '
                          'n_tables=%d auxiliary_id=%d '
                          'capabilities=0x%08x',
                          ev.msg.datapath_id, ev.msg.n_buffers, ev.msg.n_tables,
                          ev.msg.auxiliary_id, ev.msg.capabilities)
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        instruction = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod_message = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=instruction)
        else:
            mod_message = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=instruction)

        datapath.send_msg(mod_message)

    def _monitor(self):
        try:
            self.trace_manager.process_files()
            while True:
                if len(self.datapaths) != 0:
                    measurement_data = self.trace_manager.get_next_state()
                    if measurement_data is not None:
                        self.routing.fetch_latency_results(measurement_data)
                    else:
                        raise StopIteration
                hub.sleep(ControllerConstants.FREQUENCY)
        except StopIteration as e:
            self.logger.error("Reached End of Measurement Data, Stopping Periodic Routing")
        except Exception as e:
            self.logger.error("Stopping Periodic Routing, Unexpected Error Occurred")
            raise e

    @set_ev_cls(event.EventSwitchEnter)
    def handler_switch_enter(self, ev):
        self.network_manager.initialize_links(self)
