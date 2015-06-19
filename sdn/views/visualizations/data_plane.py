import json, urllib
import requests
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from sdn.helpers import session_flash
from sdn.models.controller import Controller
from sdn.models.configuration import Configuration
from sdn.models.openflow_message_counter1_0 import OpenflowMessageCounter1_0
from sdn.models.openflow_header1_0 import OpenflowHeader1_0
import logging

# Configure logging for the module name
logger = logging.getLogger(__name__)
active_menu = "Visualizations"


@login_required
def index(request):
    t = loader.get_template('data_plane_index.html')
    controller_list = Controller.objects.all()
    view_vars = {
        'active_menu': active_menu,
        'title': "Visualization of Data Plane"
    }
    c = RequestContext(request, {
        'view_vars': view_vars,
        'request': request,
        'flash': session_flash.get_flash(request),
        'controller_list': controller_list
    })
    return HttpResponse(t.render(c))

# Function for calculating the memory usage from floodlight controller
# Return values is the percentage of memory usage in the controller
def getFloodlightData(controller):
    percent_used = 100-(float(controller.floodlight.memory_free)*100/float(controller.floodlight.memory_total))
    return str(percent_used)


def getFloodlightDefaultCountersPerSwitch(controller):
    list_counters = {'packet_in': 0, 'packet_in_unicast': 0, 'packet_in_broadcast': 0,
                     'packet_in_L3_ARP': 0, 'packet_in_L3_8942': 0, 'packet_in_L3_IPv4': 0,
                     'packet_in_L3_LLDP': 0, 'packet_in_L4_ICMP': 0, 'packet_in_L4_UDP': 0,
                     'packet_out': 0, 'modify_state': 0}
    for sw in controller.floodlight.switch_set.all():
        cnt_list = OpenflowMessageCounter1_0.objects.filter(switch=sw, counter_type='default')
        for cnt in cnt_list:
            if 'packet-in' in cnt.message_subtype and cnt.message_subsubtype is None:
                list_counters['packet_in'] += cnt.counter_packets
            elif 'packet-in' in cnt.message_subtype and 'unicast' in cnt.message_subsubtype:
                list_counters['packet_in_unicast'] += cnt.counter_packets
            elif 'packet-in' in cnt.message_subtype and 'broadcast' in cnt.message_subsubtype:
                list_counters['packet_in_broadcast'] += cnt.counter_packets
            elif 'packet-in' in cnt.message_subtype and 'L3_ARP' in cnt.message_subsubtype:
                list_counters['packet_in_L3_ARP'] += cnt.counter_packets
            elif 'packet-in' in cnt.message_subtype and 'L3_8942' in cnt.message_subsubtype:
                list_counters['packet_in_L3_8942'] += cnt.counter_packets
            elif 'packet-in' in cnt.message_subtype and 'L3_IPv4' in cnt.message_subsubtype:
                list_counters['packet_in_L3_IPv4'] += cnt.counter_packets
            elif 'packet-in' in cnt.message_subtype and 'L3_LLDP' in cnt.message_subsubtype:
                list_counters['packet_in_L3_LLDP'] += cnt.counter_packets
            elif 'packet-in' in cnt.message_subtype and 'L4_ICMP' in cnt.message_subsubtype:
                list_counters['packet_in_L4_ICMP'] += cnt.counter_packets
            elif 'packet-in' in cnt.message_subtype and 'L4_UDP' in cnt.message_subsubtype:
                list_counters['packet_in_L4_UDP'] += cnt.counter_packets
            elif 'packet-out' in cnt.message_subtype:
                list_counters['packet_out'] += cnt.counter_packets
            elif 'modify-state' in cnt.message_subtype:
                list_counters['modify_state'] += cnt.counter_packets
    return list_counters

def getFloodlightCustomCountersPerSwitch(controller):
    list_switches = {}
    for sw in controller.floodlight.switch_set.all():
        cnt_list = OpenflowMessageCounter1_0.objects.filter(switch=sw, counter_type='custom')
        list_switches[sw.dpid] = {'features_request_count': 0, 'features_request_bytes': 0,
                                  'features_reply_count': 0, 'features_reply_bytes': 0,
                                  'configuration_request_count': 0, 'configuration_request_bytes': 0,
                                  'configuration_reply_count': 0, 'configuration_reply_bytes': 0,
                                  'modify_state_count': 0, 'modify_state_bytes': 0,
                                  'read_state_request_count': 0, 'read_state_request_bytes': 0,
                                  'read_state_reply_count': 0, 'read_state_reply_bytes': 0,
                                  'send_packet_count': 0, 'send_packet_bytes': 0,
                                  'barrier_request_count': 0, 'barrier_request_bytes': 0,
                                  'barrier_reply_count': 0, 'barrier_reply_bytes': 0,
                                  'packet_in_count': 0, 'packet_in_bytes': 0,
                                  'flow_removed_count': 0, 'flow_removed_bytes': 0,
                                  'port_status_count': 0, 'port_status_bytes': 0,
                                  'hello_request_count': 0, 'hello_request_bytes': 0,
                                  'hello_reply_count': 0, 'hello_reply_bytes': 0,
                                  'echo_request_count': 0, 'echo_request_bytes': 0,
                                  'echo_reply_count': 0, 'echo_reply_bytes': 0,
                                  'vendor_request_count': 0, 'vendor_request_bytes': 0,
                                  'vendor_reply_count': 0, 'vendor_reply_bytes': 0}
        for cnt in cnt_list:
            if 'features' in cnt.message_subtype and 'request' in cnt.message_subsubtype:
                list_switches[sw.dpid]['features_request_count'] = cnt.counter_packets
                list_switches[sw.dpid]['features_request_bytes'] = cnt.counter_bytes
            elif 'features' in cnt.message_subtype and 'reply' in cnt.message_subsubtype:
                list_switches[sw.dpid]['features_reply_count'] = cnt.counter_packets
                list_switches[sw.dpid]['features_reply_bytes'] = cnt.counter_bytes
            elif 'configuration' in cnt.message_subtype and 'request' in cnt.message_subsubtype:
                list_switches[sw.dpid]['configuration_request_count'] = cnt.counter_packets
                list_switches[sw.dpid]['configuration_request_bytes'] = cnt.counter_bytes
            elif 'configuration' in cnt.message_subtype and 'reply' in cnt.message_subsubtype:
                list_switches[sw.dpid]['configuration_reply_count'] = cnt.counter_packets
                list_switches[sw.dpid]['configuration_reply_bytes'] = cnt.counter_bytes
            elif 'modify-state' in cnt.message_subtype:
                list_switches[sw.dpid]['modify_state_count'] = cnt.counter_packets
                list_switches[sw.dpid]['modify_state_bytes'] = cnt.counter_bytes
            elif 'read-state' in cnt.message_subtype and 'request' in cnt.message_subsubtype:
                list_switches[sw.dpid]['read_state_request_count'] = cnt.counter_packets
                list_switches[sw.dpid]['read_state_request_bytes'] = cnt.counter_bytes
            elif 'read-state' in cnt.message_subtype and 'reply' in cnt.message_subsubtype:
                list_switches[sw.dpid]['read_state_reply_count'] = cnt.counter_packets
                list_switches[sw.dpid]['read_state_reply_bytes'] = cnt.counter_bytes
            elif 'send-packet' in cnt.message_subtype:
                list_switches[sw.dpid]['send_packet_count'] = cnt.counter_packets
                list_switches[sw.dpid]['send_packet_bytes'] = cnt.counter_bytes
            elif 'barrier' in cnt.message_subtype and 'request' in cnt.message_subsubtype:
                list_switches[sw.dpid]['barrier_request_count'] = cnt.counter_packets
                list_switches[sw.dpid]['barrier_request_bytes'] = cnt.counter_bytes
            elif 'barrier' in cnt.message_subtype and 'reply' in cnt.message_subsubtype:
                list_switches[sw.dpid]['barrier_reply_count'] = cnt.counter_packets
                list_switches[sw.dpid]['barrier_reply_bytes'] = cnt.counter_bytes
            elif 'packet-in' in cnt.message_subtype:
                list_switches[sw.dpid]['packet_in_count'] = cnt.counter_packets
                list_switches[sw.dpid]['packet_in_bytes'] = cnt.counter_bytes
            elif 'flow-removed' in cnt.message_subtype:
                list_switches[sw.dpid]['flow_removed_count'] = cnt.counter_packets
                list_switches[sw.dpid]['flow_removed_bytes'] = cnt.counter_bytes
            elif 'port-status' in cnt.message_subtype:
                list_switches[sw.dpid]['port_status_count'] = cnt.counter_packets
                list_switches[sw.dpid]['port_status_bytes'] = cnt.counter_bytes
            elif 'hello' in cnt.message_subtype and 'request' in cnt.message_subsubtype:
                list_switches[sw.dpid]['hello_request_count'] = cnt.counter_packets
                list_switches[sw.dpid]['hello_request_bytes'] = cnt.counter_bytes
            elif 'hello' in cnt.message_subtype and 'reply' in cnt.message_subsubtype:
                list_switches[sw.dpid]['hello_reply_count'] = cnt.counter_packets
                list_switches[sw.dpid]['hello_reply_bytes'] = cnt.counter_bytes
            elif 'echo' in cnt.message_subtype and 'request' in cnt.message_subsubtype:
                list_switches[sw.dpid]['echo_request_count'] = cnt.counter_packets
                list_switches[sw.dpid]['echo_request_bytes'] = cnt.counter_bytes
            elif 'echo' in cnt.message_subtype and 'reply' in cnt.message_subsubtype:
                list_switches[sw.dpid]['echo_reply_count'] = cnt.counter_packets
                list_switches[sw.dpid]['echo_reply_bytes'] = cnt.counter_bytes
            elif 'vendor' in cnt.message_subtype and 'request' in cnt.message_subsubtype:
                list_switches[sw.dpid]['vendor_request_count'] = cnt.counter_packets
                list_switches[sw.dpid]['vendor_request_bytes'] = cnt.counter_bytes
            elif 'vendor' in cnt.message_subtype and 'reply' in cnt.message_subsubtype:
                list_switches[sw.dpid]['vendor_reply_count'] = cnt.counter_packets
                list_switches[sw.dpid]['vendor_reply_bytes'] = cnt.counter_bytes

    return list_switches

def getFloodlightHeaderCountersPerSwitch(controller):
    list_switches = {}
    for sw in controller.floodlight.switch_set.all():
        list_switches[sw.dpid] = []
        headers = OpenflowHeader1_0.objects.filter(openflow_table1_0__openflow_switch1_0=sw)
        for head in headers:
            list_switches[sw.dpid] += [{'ingress_port': head.ingress_port,
                                        'ethernet_source_address': head.ethernet_source_address,
                                        'ethernet_destination_address': head.ethernet_destination_address,
                                        'ethernet_type': head.ethernet_type,
                                        'vlan_id': head.vlan_id,
                                        'vlan_priority': head.vlan_priority,
                                        'ip_source_address': head.ip_source_address,
                                        'ip_destination_address': head.ip_destination_address,
                                        'ip_protocol': head.ip_protocol,
                                        'ip_tos_bits': head.ip_tos_bits,
                                        'transport_source_port': head.transport_source_port,
                                        'transport_destination_port': head.transport_destination_port,
                                        'flow_status': head.flow_status,
                                        'last_synchronization_time': head.last_synchronization_time,
                                        'received_packets': head.openflowheadercounter1_0_set.all()[0].received_packets,
                                        'received_bytes': head.openflowheadercounter1_0_set.all()[0].received_bytes,
                                        'duration_seconds': head.openflowheadercounter1_0_set.all()[0].duration_seconds,
                                        'duration_nanoseconds': head.openflowheadercounter1_0_set.all()[0].duration_nanoseconds}]
    return list_switches

def getDataPlane(request, controller_id):
    dataplane = {'nodes': [], 'edges': [], 'controller': {}, 'data_traffic': {}}
    try:
        controller = Controller.objects.get(pk=controller_id)
        aggregate_flow_count = OpenflowHeader1_0.objects.filter(openflow_table1_0__openflow_switch1_0__controller=controller)
        aggregate_idle_flow_count = aggregate_flow_count.filter(flow_status=False)
        aggregate_message_count = {'features_request_count': 0, 'features_request_bytes': 0,
                                  'features_reply_count': 0, 'features_reply_bytes': 0,
                                  'configuration_request_count': 0, 'configuration_request_bytes': 0,
                                  'configuration_reply_count': 0, 'configuration_reply_bytes': 0,
                                  'modify_state_count': 0, 'modify_state_bytes': 0,
                                  'read_state_request_count': 0, 'read_state_request_bytes': 0,
                                  'read_state_reply_count': 0, 'read_state_reply_bytes': 0,
                                  'send_packet_count': 0, 'send_packet_bytes': 0,
                                  'barrier_request_count': 0, 'barrier_request_bytes': 0,
                                  'barrier_reply_count': 0, 'barrier_reply_bytes': 0,
                                  'packet_in_count': 0, 'packet_in_bytes': 0,
                                  'flow_removed_count': 0, 'flow_removed_bytes': 0,
                                  'port_status_count': 0, 'port_status_bytes': 0,
                                  'hello_request_count': 0, 'hello_request_bytes': 0,
                                  'hello_reply_count': 0, 'hello_reply_bytes': 0,
                                  'echo_request_count': 0, 'echo_request_bytes': 0,
                                  'echo_reply_count': 0, 'echo_reply_bytes': 0,
                                  'vendor_request_count': 0, 'vendor_request_bytes': 0,
                                  'vendor_reply_count': 0, 'vendor_reply_bytes': 0}
        list_switches = getFloodlightCustomCountersPerSwitch(controller)
        for dpid in list_switches:
            for message in list_switches[dpid]:
                aggregate_message_count[message] += list_switches[dpid][message]


        aggregate_last_synchronization_time = controller.floodlight.last_synchronization_time
        #list_headers = getFloodlightHeaderCountersPerSwitch(controller)
        #for dpid in list_headers:
            # TODO last_synchronization_time for the cont
            #for flow in list_headers[dpid]:
                #aggregate_last_synchronization_time += float(flow['last_synchronization_time'])
            #    aggregate_last_synchronization_time += list_headers[dpid][flow]['last_synchronization_time']

        # Populate controller data
        if controller.controller_type == 'f':
            dataplane['controller']['default'] = {'memory_percent_used': getFloodlightData(controller),
                                                  'packet_in_unicast': str(getFloodlightDefaultCountersPerSwitch(controller)['packet_in_unicast']),
                                                  'packet_in_broadcast': str(getFloodlightDefaultCountersPerSwitch(controller)['packet_in_broadcast']),
                                                  'packet_in_L3_ARP': str(getFloodlightDefaultCountersPerSwitch(controller)['packet_in_L3_ARP']),
                                                  'packet_in_L3_8942': str(getFloodlightDefaultCountersPerSwitch(controller)['packet_in_L3_8942']),
                                                  'packet_in_L3_IPv4': str(getFloodlightDefaultCountersPerSwitch(controller)['packet_in_L3_IPv4']),
                                                  'packet_in_L3_LLDP': str(getFloodlightDefaultCountersPerSwitch(controller)['packet_in_L3_LLDP']),
                                                  'packet_in_L4_ICMP': str(getFloodlightDefaultCountersPerSwitch(controller)['packet_in_L4_ICMP']),
                                                  'packet_in_L4_UDP': str(getFloodlightDefaultCountersPerSwitch(controller)['packet_in_L4_UDP']),
                                                  'packet_out': str(getFloodlightDefaultCountersPerSwitch(controller)['packet_out']),
                                                  'modify_state': str(getFloodlightDefaultCountersPerSwitch(controller)['modify_state'])}
            dataplane['controller']['custom'] = {'aggregate': {'idle_flow_count': len(aggregate_idle_flow_count),
                                                               'flow_count': len(aggregate_flow_count),
                                                               'control_messages_count': aggregate_message_count,
                                                               'last_synchronization_time': aggregate_last_synchronization_time},
                                                 'per_switch': getFloodlightCustomCountersPerSwitch(controller)}
            dataplane['data_traffic']['header'] = {'aggregate': 0,
                                                   'per_switch': getFloodlightHeaderCountersPerSwitch(controller)}

        # Populate json with links, hosts and switches
        links_list = []
        hosts_list = []
        for s in controller.switch_set.all():
            dataplane['nodes'] += [{'id':str(s.dpid), 'name': str(s.dpid), 'type': 's'}]
            for p in s.port_set.all():
                for l in p.link_set.all():
                    links_list.append(l)
        for h in controller.host_set.all():
            hosts_list.append(h)

        for l in links_list:
            try:
                # src = dataplane['nodes'].index({'name': str(l.src_port.switch.dpid), 'type': 's'})
                # dst = dataplane['nodes'].index({'name': str(l.dst_port.switch.dpid), 'type': 's'})

                dataplane['edges'] += [{'source': str(l.src_port.switch.dpid), 'target': str(l.dst_port.switch.dpid)}]
            except ValueError as e:
                logger.warning(e)

        for h in hosts_list:
            dataplane['nodes'] += [{'id':str(h.mac_address), 'name': str(h.ipv4_address), 'type':'h'}]
            try:
                # src = dataplane['nodes'].index({'name': str(h.ipv4_address), 'type':'h'})
                if h.port is not None:
                    # dst = dataplane['nodes'].index({'name': str(h.port.switch.dpid), 'type':'s'})
                    dataplane['edges'] += [{'source': str(h.mac_address), 'target': str(h.port.switch.dpid)}]

            except ValueError as e:
                logger.warning(e)

        return HttpResponse(json.dumps(dataplane), mimetype='application/json')
    except:
        pass



def getFloodlightConfigurations(controller):
    url = 'http://' + str(controller.ip_address) + ':' + str(controller.listen_port) + '/wm/core/controller/configure/json'
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    # return the configuration parameters
    return data


def selectController(request, controller_id):
    try:
        controller_list = Controller.objects.all()
        #if 'controller_selector' in request.POST:
        #selected_controller_id = request.POST['controller_selector']
        configure_url = "/Aurora/sdn/visualizations/data_plane/controller/"+str(controller_id)+"/configure/"
        selected_controller = Controller.objects.get(pk=controller_id)
        monitoring_configurations = loadConfiguration(selected_controller)
        configurations = getFloodlightConfigurations(selected_controller)
        t = loader.get_template('data_plane_visualization.html')
    except:
        selected_controller = None
        monitoring_configurations = None
        configurations = None
        monitoring_configurations = loadConfiguration(None);
        t = loader.get_template('data_plane_index.html')
        session_flash.set_flash(request, "Controller is unavailable for viewing!", 'danger')

    idle_options = []
    for i in range(0, 101):
        idle_options.append(i)
    hard_options = []
    for i in range(0, 31):
        hard_options.append(i)
    polling_interval_options = []
    for i in range(1, 121):
        polling_interval_options.append(i)
    #polling_interval = 20
    chart_update_options = []
    for i in range(1, 121):
        chart_update_options.append(i)
    #chart_update_interval = 10
    view_vars = {
        'active_menu': active_menu,
        'title': "Visualization of Data Plane"
    }
    c = RequestContext(request, {
        'view_vars': view_vars,
        'request': request,
        'controller_list': controller_list,
        'selected_controller': selected_controller,
        'configurations': configurations,
        'idle_options': idle_options,
        'hard_options': hard_options,
        'polling_interval': monitoring_configurations['polling_interval'],
        'polling_interval_options': polling_interval_options,
        'chart_update_interval': monitoring_configurations['chart_update_interval'],
        'chart_update_options': chart_update_options,
        'configure_url': configure_url,
        'flash': session_flash.get_flash(request)
    })
    return HttpResponse(t.render(c))



def configureController(request, controller_id):
    selected_controller = Controller.objects.get(pk=controller_id)
    url = "http://" + str(selected_controller.ip_address) + ":" + str(selected_controller.listen_port) + "/wm/core/controller/configure/json"
    payload = {'idle_timeout': request.POST['idle_timeout_selector'],
    'hard_timeout': request.POST['hard_timeout_selector']}
    requests.get(url, data=payload)
    monitoring_configurations = {'polling_interval':request.POST['polling_interval_selector'],
                                'chart_update_interval':request.POST['chart_update_selector']}
    saveConfiguration(selected_controller, monitoring_configurations)
    return redirect('/Aurora/sdn/visualizations/data_plane/controller/' + controller_id + '/view/') # Redirect after POST

def loadConfiguration(controller):
    try:
        configuration = Configuration.objects.get(controller=controller)
        pol_int = configuration.polling_interval
        cha_up_int = configuration.chart_update_interval
    except Configuration.DoesNotExist:
        pol_int = 25
        cha_up_int = 25
    return {'polling_interval': pol_int, 'chart_update_interval': cha_up_int};

def saveConfiguration(selected_controller, parameters):
    try:
        conf = Configuration.objects.get(controller=selected_controller)
    except Configuration.DoesNotExist:
        conf = Configuration()
    conf.polling_interval = parameters['polling_interval']
    conf.chart_update_interval = parameters['chart_update_interval']
    conf.controller = selected_controller
    conf.save()

