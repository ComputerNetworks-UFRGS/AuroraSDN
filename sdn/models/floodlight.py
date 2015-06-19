from sdn.models.controller import Controller
from sdn.models.openflow_switch1_0 import OpenflowSwitch1_0
from sdn.models.host import Host
from sdn.models.link import Link
from sdn.models.openflow_message_counter1_0 import OpenflowMessageCounter1_0
from sdn.models.openflow_header1_0 import OpenflowHeader1_0
from django.db import models
import urllib, json
import logging
import time

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your models here.
class Floodlight(Controller):

    # Current role
    role = models.CharField(max_length=100, blank=True, null=True)

    # Change description
    change_description = models.CharField(max_length=100, blank=True, null=True)

    # Change date time
    change_date_time = models.CharField(max_length=100, blank=True, null=True)

    # Total memory from controller
    memory_total = models.CharField(max_length=100, blank=True, null=True)

    # Free memory from controller
    memory_free = models.CharField(max_length=100, blank=True, null=True)

    # Last synchronization timestamp
    last_synchronization_time = models.CharField(max_length=100)

    def getOpenflowSwitches(self):
        # Importing Json from floodlight url for switch and port information
        url = "/wm/core/controller/switches/json"
        return self.getJsonFromURL(url)

    def getHosts(self):
        # Importing Json from floodlight url for devices information
        url = "/wm/device/"
        return self.getJsonFromURL(url)

    def getOpenflowFlowTables(self, openflow_switch1_0=None):
        # Importing Json from floodlight url for flow table information
        if openflow_switch1_0 is None:
            url = "/wm/core/switch/all/table/json"
        else:
            # TODO Control the match
            url = "/wm/core/switch/" + openflow_switch1_0.dpid + "/table/json"
        return self.getJsonFromURL(url)

    def getOpenflowHeaders(self, openflow_switch1_0=None):
        # Importing Json from floodlight url for flow headers information
        if openflow_switch1_0 is None:
            url = "/wm/core/switch/all/flow/json"
        else:
            # TODO Control the match
            url = "/wm/core/switch/" + openflow_switch1_0.dpid + "/flow/json"
        return self.getJsonFromURL(url)

    def getOpenflowPorts(self, openflow_switch1_0=None):
        # Importing Json from floodlight url for ports information
        if openflow_switch1_0 is None:
            url = "/wm/core/switch/all/port/json"
        else:
            # TODO Control the match
            url = "/wm/core/switch/" + openflow_switch1_0.dpid + "/port/json"
        return self.getJsonFromURL(url)

    def getLinks(self):
        # Importing Json from floodlight url for links information
        url = "/wm/topology/links/json"
        return self.getJsonFromURL(url)

    def getJsonFromURL(self, url):
        url = "http://" + self.ip_address + ":" + self.listen_port + url
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        return data

    def getMemoryUsage(self):
        # Importing Json from floodlight url for memory usage information
        url = "/wm/core/memory/json"
        return self.getJsonFromURL(url)

    def getRole(self):
        # Importing Json from floodlight url for role information
        url = "/wm/core/role/json"
        return self.getJsonFromURL(url)

    def getMessageCounters(self):
        # Importing Json from floodlight url for PACKET-IN and MODIFY-STATE information
        url = "/wm/core/counter/all/json"
        return self.getJsonFromURL(url)

    def sync(self):
        logger.debug("*** SYNC START ***")
        # Initialize sync time
        sync_time = int(time.time())
        debug_time = int(time.time())

        op_switches = self.getOpenflowSwitches()
        #logger.debug("Get switches JSON " + str(int(time.time()) - debug_time))
        #debug_time = int(time.time())

        op_tables = self.getOpenflowFlowTables()
        #logger.debug("Get tables JSON " + str(int(time.time()) - debug_time))
        #debug_time = int(time.time())

        op_headers = self.getOpenflowHeaders()
        #logger.debug("Get headers JSON " + str(int(time.time()) - debug_time))
        #debug_time = int(time.time())

        op_ports = self.getOpenflowPorts()
        #logger.debug("Get ports JSON " + str(int(time.time()) - debug_time))
        #debug_time = int(time.time())

        memory_usage = self.getMemoryUsage()
        #logger.debug("Get controller memory JSON " + str(int(time.time()) - debug_time))
        #debug_time = int(time.time())

        message_counters = self.getMessageCounters()
        #logger.debug("Get default message counters JSON " + str(int(time.time()) - debug_time))
        #debug_time = int(time.time())

        logger.debug("Get JSON urls from Floodlight " + str(int(time.time()) - debug_time))
        debug_time = int(time.time())

        hosts = self.getHosts()
        links = self.getLinks()

        logger.debug("Get Hosts and Links " + str(int(time.time()) - debug_time))
        debug_time = int(time.time())

        # All switches
        for op_switch in op_switches:
            dpid = op_switch['dpid']
            ofs = OpenflowSwitch1_0()
            ofs.controller = self
            # Only the first table will be passed
            ofs.sync(op_switch, op_tables[dpid][0], op_headers[dpid], op_ports[dpid], sync_time, debug_time)
            debug_time = int(time.time())

        logger.debug("Sync all switches " + str(int(time.time()) - debug_time))
        debug_time = int(time.time())

        # All hosts
        for host in hosts:
            h = Host()
            h.controller = self
            h.sync(host)

        logger.debug("Sync all hosts " + str(int(time.time()) - debug_time))
        debug_time = int(time.time())

        # All links
        for link in links:
            l = Link()
            l.sync(link, op_switches)

        logger.debug("Sync all links " + str(int(time.time()) - debug_time))
        debug_time = int(time.time())

        # Controller information (memory usage, role, description, change time)
        self.memory_total = memory_usage['total']
        self.memory_free = memory_usage['free']
        role_info = self.getRole()
        self.role = role_info['role']
        self.change_description = role_info['change-description']
        self.change_date_time = role_info['change-date-time']
        self.last_synchronization_time = sync_time
        self.save()

        logger.debug("Sync controller " + str(int(time.time()) - debug_time))
        debug_time = int(time.time())

        # All message counters
        mc = OpenflowMessageCounter1_0()
        mc.syncFloodlightDefaultCounters(message_counters)
        logger.debug("Sync default message counters " + str(int(time.time()) - debug_time))
        debug_time = int(time.time())

        mc.syncFloodlightCustomCounters(op_headers)
        logger.debug("Sync custom message counters " + str(int(time.time()) - debug_time))
        debug_time = int(time.time())

        # Delete all old flows
        # TODO more than these tables are considered
        OpenflowHeader1_0.objects.filter(
            openflow_table1_0__openflow_switch1_0__controller=self
        ).exclude(
            last_synchronization_time=sync_time
        ).delete()

        logger.debug("Delete all old flows " + str(int(time.time()) - debug_time))
