# -*- coding: utf-8 -*-
from django.db import models
from sdn.models.switch import Switch
from sdn.models.base_model import BaseModel

MESSAGE_COUNTER_TYPE = (
    ('default', 'DEFAULT'),
    ('custom', 'CUSTOM')
)

MESSAGE_TYPE_CHOICE = (
    ('Controller-to-switch', 'CONTROLLER-TO-SWITCH'),
    ('Asynchronous', 'ASYNCHRONOUS'),
    ('Symmetric', 'SYMMETRIC')
)

MESSAGE_SUBTYPE_CHOICE = (
    # Controller to switch
    ('features', 'FEATURES'),
    ('configuration', 'CONFIGURATION'),
    ('modify-state', 'MODIFY_STATE'),
    ('read-state', 'READ_STATE'),
    ('send-packet', 'SEND_PACKET'),
    ('barrier', 'BARRIER'),
    # Asynchronous
    ('packet-in', 'PACKET_IN'),
    ('flow-removed', 'FLOW_REMOVED'),
    ('port-status', 'PORT_STATUS'),
    # Symmetric
    ('hello', 'HELLO'),
    ('echo', 'ECHO'),
    ('vendor', 'VENDOR')
)


# Create your models here.
class OpenflowMessageCounter1_0(BaseModel):
    # Counter type (ex:default provided by Floodlight controller and custom by my implementation :])
    counter_type = models.CharField(max_length=30, choices=MESSAGE_TYPE_CHOICE, db_index=True)

    # Message type
    message_type = models.CharField(max_length=30, choices=MESSAGE_TYPE_CHOICE, db_index=True)

    # Message subtype
    message_subtype = models.CharField(max_length=30, choices=MESSAGE_SUBTYPE_CHOICE, db_index=True)

    # Message subsubtype (ex: LLDP, ICMP, UDP, L3_ARP, L3_8942)
    message_subsubtype = models.CharField(max_length=100, null=True, db_index=True)

    # Number of packets counted
    counter_packets = models.BigIntegerField(null=True)

    # Length of packets counted
    counter_bytes = models.BigIntegerField(null=True)

    # Switch assigned
    switch = models.ForeignKey(Switch)

    def syncFloodlightDefaultCounters(self, message_counters):
        counter_type = 'default'
        list_counters = []
        for key, value in message_counters.iteritems():
            row = key.split('_')
            entity = row[0]
            if len(row) > 1:
                if entity != 'controller' and entity != 'StorageQuery' and entity != 'StorageUpdate' and entity != 'StorageDelete':
                    switch_dpid = entity
                    msg_subtype = row[2]
                    if 'PacketIn' in msg_subtype or 'FlowRemoved' in msg_subtype or 'PortStatus' in msg_subtype:
                        message_type = 'Asynchronous'
                    else:
                        if 'Hello' in msg_subtype or 'Echo' in msg_subtype or 'Barrier' in msg_subtype:
                            message_type = 'Symmetric'
                        else:
                            message_type = 'Controller-to-switch'
                    if 'PacketIn' in msg_subtype:
                        message_subtype = 'PACKET_IN'
                        message_subsubtype = None
                    elif 'FlowMod' in msg_subtype:
                        message_subtype = 'MODIFY_STATE'
                        message_subsubtype = None
                    elif 'PacketOut' in msg_subtype:
                        message_subtype = 'PACKET_OUT'
                        message_subsubtype = None
                    else:
                        message_subtype = msg_subtype
                    if 'PacketIn' in msg_subtype and len(row) > 3:
                        msg_subsubtype = row[4]
                        if 'unicast' in msg_subsubtype:
                            message_subsubtype = 'unicast'
                        elif 'broadcast' in msg_subsubtype:
                            message_subsubtype = 'broadcast'
                        elif 'L3' in msg_subsubtype:
                            msg_subsubtype = row[5]
                            if 'ARP' in msg_subsubtype:
                                message_subsubtype = 'L3_ARP'
                            elif '8942' in msg_subsubtype:
                                message_subsubtype = 'L3_8942'
                            elif 'IPv4' in msg_subsubtype:
                                message_subsubtype = 'L3_IPv4'
                            elif 'LLDP' in msg_subsubtype:
                                message_subsubtype = 'L3_LLDP'
                        elif 'L4' in msg_subsubtype:
                            msg_subsubtype = row[5]
                            if 'ICMP' in msg_subsubtype:
                                message_subsubtype = 'L4_ICMP'
                            elif 'UDP' in msg_subsubtype:
                                message_subsubtype = 'L4_UDP'
                    list_counters.append({'dpid':switch_dpid,'msg_subtype':message_subtype,'msg_subsubtype':message_subsubtype,'counter_packets':value})

        new_list_counters = {}
        for row in list_counters:
            switch = row['dpid']
            msg_subtype = row['msg_subtype']
            msg_subsubtype = row['msg_subsubtype']
            if switch in new_list_counters:
                new_list_counters[switch][str(msg_subtype)+'_'+str(msg_subsubtype)] += row['counter_packets']
            else:
                new_list_counters[switch] = {}
                new_list_counters[switch]['PACKET_IN_None'] = 0
                new_list_counters[switch]['PACKET_IN_unicast'] = 0
                new_list_counters[switch]['PACKET_IN_broadcast'] = 0
                new_list_counters[switch]['PACKET_IN_L3_ARP'] = 0
                new_list_counters[switch]['PACKET_IN_L3_8942'] = 0
                new_list_counters[switch]['PACKET_IN_L3_IPv4'] = 0
                new_list_counters[switch]['PACKET_IN_L3_LLDP'] = 0
                new_list_counters[switch]['PACKET_IN_L4_ICMP'] = 0
                new_list_counters[switch]['PACKET_IN_L4_UDP'] = 0
                new_list_counters[switch]['PACKET_OUT_None'] = 0
                new_list_counters[switch]['MODIFY_STATE_None'] = 0

        #logger.debug(new_list_counters)

        for key, value in list(new_list_counters.items()):
            sw = Switch.objects.get(dpid=key)
            #logger.debug(key)
            #logger.debug(value)
            # Packet-IN None
            try:
                cnt = OpenflowMessageCounter1_0.objects.get(switch=sw,
                    counter_type=counter_type,
                    message_type=message_type,
                    message_subtype='packet-in',
                    message_subsubtype=None)
                cnt.counter_packets = value['PACKET_IN_None']
            except OpenflowMessageCounter1_0.DoesNotExist:
                cnt = OpenflowMessageCounter1_0()
                cnt.switch = sw
                cnt.counter_type = counter_type
                cnt.message_type = message_type
                cnt.message_subtype = 'packet-in'
                cnt.message_subsubtype = None
                cnt.counter_packets = value['PACKET_IN_None']
            cnt.save()

            # Packet-IN unicast
            try:
                cnt = OpenflowMessageCounter1_0.objects.get(switch=sw,
                    counter_type=counter_type,
                    message_type=message_type,
                    message_subtype='packet-in',
                    message_subsubtype='unicast')
                cnt.counter_packets = value['PACKET_IN_unicast']
            except OpenflowMessageCounter1_0.DoesNotExist:
                cnt = OpenflowMessageCounter1_0()
                cnt.switch = sw
                cnt.counter_type = counter_type
                cnt.message_type = message_type
                cnt.message_subtype = 'packet-in'
                cnt.message_subsubtype = 'unicast'
                cnt.counter_packets = value['PACKET_IN_unicast']
            cnt.save()

            # Packet-IN broadcast
            try:
                cnt = OpenflowMessageCounter1_0.objects.get(switch=sw,
                    counter_type=counter_type,
                    message_type=message_type,
                    message_subtype='packet-in',
                    message_subsubtype='broadcast')
                cnt.counter_packets = value['PACKET_IN_broadcast']
            except OpenflowMessageCounter1_0.DoesNotExist:
                cnt = OpenflowMessageCounter1_0()
                cnt.switch = sw
                cnt.counter_type = counter_type
                cnt.message_type=message_type
                cnt.message_subtype = 'packet-in'
                cnt.message_subsubtype = 'broadcast'
                cnt.counter_packets = value['PACKET_IN_broadcast']
            cnt.save()

            # Packet-IN L3_ARP
            try:
                cnt = OpenflowMessageCounter1_0.objects.get(switch=sw,
                    counter_type=counter_type,
                    message_type=message_type,
                    message_subtype='packet-in',
                    message_subsubtype ='L3_ARP')
                cnt.counter_packets = value['PACKET_IN_L3_ARP']
            except OpenflowMessageCounter1_0.DoesNotExist:
                cnt = OpenflowMessageCounter1_0()
                cnt.switch = sw
                cnt.counter_type = counter_type
                cnt.message_type = message_type
                cnt.message_subtype = 'packet-in'
                cnt.message_subsubtype = 'L3_ARP'
                cnt.counter_packets = value['PACKET_IN_L3_ARP']
            cnt.save()

            # Packet-IN L3_8942
            try:
                cnt = OpenflowMessageCounter1_0.objects.get(switch=sw,
                    counter_type=counter_type,
                    message_type=message_type,
                    message_subtype='packet-in',
                    message_subsubtype='L3_8942')
                cnt.counter_packets = value['PACKET_IN_L3_8942']
            except OpenflowMessageCounter1_0.DoesNotExist:
                cnt = OpenflowMessageCounter1_0()
                cnt.switch = sw
                cnt.counter_type = counter_type
                cnt.message_type = message_type
                cnt.message_subtype = 'packet-in'
                cnt.message_subsubtype = 'L3_8942'
                cnt.counter_packets = value['PACKET_IN_L3_8942']
            cnt.save()

            # Packet-IN L3_IPv4
            try:
                cnt = OpenflowMessageCounter1_0.objects.get(switch=sw,
                    counter_type=counter_type,
                    message_type=message_type,
                    message_subtype='packet-in',
                    message_subsubtype='L3_IPv4')
                cnt.counter_packets = value['PACKET_IN_L3_IPv4']
            except OpenflowMessageCounter1_0().DoesNotExist:
                cnt = OpenflowMessageCounter1_0()
                cnt.switch = sw
                cnt.counter_type = counter_type
                cnt.message_type = message_type
                cnt.message_subtype = 'packet-in'
                cnt.message_subsubtype = 'L3_IPv4'
                cnt.counter_packets = value['PACKET_IN_L3_IPv4']
            cnt.save()

            # Packet-IN L3_LLDP
            try:
                cnt = OpenflowMessageCounter1_0.objects.get(switch=sw,
                    counter_type=counter_type,
                    message_type=message_type,
                    message_subtype='packet-in',
                    message_subsubtype='L3_LLDP')
                cnt.counter_packets = value['PACKET_IN_L3_LLDP']
            except OpenflowMessageCounter1_0.DoesNotExist:
                cnt = OpenflowMessageCounter1_0()
                cnt.switch = sw
                cnt.counter_type = counter_type
                cnt.message_type = message_type
                cnt.message_subtype = 'packet-in'
                cnt.message_subsubtype = 'L3_LLDP'
                cnt.counter_packets = value['PACKET_IN_L3_LLDP']
            cnt.save()

            # Packet-IN L4_ICMP
            try:
                cnt = OpenflowMessageCounter1_0.objects.get(switch=sw,
                    counter_type=counter_type,
                    message_type=message_type,
                    message_subtype='packet-in',
                    message_subsubtype='L4_ICMP')
                cnt.counter_packets = value['PACKET_IN_L4_ICMP']
            except OpenflowMessageCounter1_0.DoesNotExist:
                cnt = OpenflowMessageCounter1_0()
                cnt.switch = sw
                cnt.counter_type = counter_type
                cnt.message_type = message_type
                cnt.message_subtype = 'packet-in'
                cnt.message_subsubtype = 'L4_ICMP'
                cnt.counter_packets = value['PACKET_IN_L4_ICMP']
            cnt.save()

            # Packet-IN L4_UDP
            try:
                cnt = OpenflowMessageCounter1_0.objects.get(switch=sw,
                    counter_type=counter_type,
                    message_type=message_type,
                    message_subtype='packet-in',
                    message_subsubtype='L4_UDP')
                cnt.counter_packets = value['PACKET_IN_L4_UDP']
            except OpenflowMessageCounter1_0.DoesNotExist:
                cnt = OpenflowMessageCounter1_0()
                cnt.switch = sw
                cnt.counter_type = counter_type
                cnt.message_type = message_type
                cnt.message_subtype = 'packet-in'
                cnt.message_subsubtype = 'L4_UDP'
                cnt.counter_packets = value['PACKET_IN_L4_UDP']
            cnt.save()

            # Packet-OUT None
            try:
                cnt = OpenflowMessageCounter1_0.objects.get(switch=sw,
                    counter_type=counter_type,
                    message_type=message_type,
                    message_subtype='send-packet',
                    message_subsubtype=None)
                cnt.counter_packets = value['PACKET_OUT_None']
            except OpenflowMessageCounter1_0.DoesNotExist:
                cnt = OpenflowMessageCounter1_0()
                cnt.switch = sw
                cnt.counter_type = counter_type
                cnt.message_type = message_type
                cnt.message_subtype = 'send-packet'
                cnt.message_subsubtype = None
                cnt.counter_packets = value['PACKET_OUT_None']
            cnt.save()

            # Modify-State None
            try:
                cnt = OpenflowMessageCounter1_0.objects.get(switch=sw,
                    counter_type=counter_type,
                    message_type=message_type,
                    message_subtype='modify-state',
                    message_subsubtype=None)
                cnt.counter_packets = value['MODIFY_STATE_None']
            except OpenflowMessageCounter1_0.DoesNotExist:
                cnt = OpenflowMessageCounter1_0()
                cnt.switch = sw
                cnt.counter_type = counter_type
                cnt.message_type = message_type
                cnt.message_subtype = 'modify-state'
                cnt.message_subsubtype = None
                cnt.counter_packets = value['MODIFY_STATE_None']
            cnt.save()


    def syncFloodlightCustomCounters(self, message_counters):
        counter_type = 'custom'
        control_channel_statistics = message_counters['Control Channel Statistics']
        for dpid in control_channel_statistics:
            sw = Switch.objects.get(dpid=dpid)
            # Count features request messages
            cnt = OpenflowMessageCounter1_0()
            cnt.switch = sw
            cnt.counter_type = counter_type
            cnt.message_type = 'Controller-to-switch'
            cnt.message_subtype = 'features'
            cnt.message_subsubtype = 'request'
            cnt.counter_packets = control_channel_statistics[dpid]['featuresRequestCount']
            cnt.counter_bytes = control_channel_statistics[dpid]['featuresRequestBytes']
            cnt.save()
            # Count features reply messages
            cnt = OpenflowMessageCounter1_0()
            cnt.switch = sw
            cnt.counter_type = counter_type
            cnt.message_type = 'Controller-to-switch'
            cnt.message_subtype = 'features'
            cnt.message_subsubtype = 'reply'
            cnt.counter_packets = control_channel_statistics[dpid]['featuresReplyCount']
            cnt.counter_bytes = control_channel_statistics[dpid]['featuresReplyBytes']
            cnt.save()
            # Count configuration request messages
            cnt = OpenflowMessageCounter1_0()
            cnt.switch = sw
            cnt.counter_type = counter_type
            cnt.message_type = 'Controller-to-switch'
            cnt.message_subtype = 'configuration'
            cnt.message_subsubtype = 'request'
            cnt.counter_packets = control_channel_statistics[dpid]['configurationRequestCount']
            cnt.counter_bytes = control_channel_statistics[dpid]['configurationRequestBytes']
            cnt.save()
            # Count configuration reply messages
            cnt = OpenflowMessageCounter1_0()
            cnt.switch = sw
            cnt.counter_type = counter_type
            cnt.message_type = 'Controller-to-switch'
            cnt.message_subtype = 'configuration'
            cnt.message_subsubtype = 'reply'
            cnt.counter_packets = control_channel_statistics[dpid]['configurationReplyCount']
            cnt.counter_bytes = control_channel_statistics[dpid]['configurationReplyBytes']
            cnt.save()
            # Count modify-state messages
            cnt = OpenflowMessageCounter1_0()
            cnt.switch = sw
            cnt.counter_type = counter_type
            cnt.message_type = 'Controller-to-switch'
            cnt.message_subtype = 'modify-state'
            cnt.message_subsubtype = None
            cnt.counter_packets = control_channel_statistics[dpid]['modifyStateCount']
            cnt.counter_bytes = control_channel_statistics[dpid]['modifyStateBytes']
            cnt.save()
            # Count read-state request messages
            cnt = OpenflowMessageCounter1_0()
            cnt.switch = sw
            cnt.counter_type = counter_type
            cnt.message_type = 'Controller-to-switch'
            cnt.message_subtype = 'read-state'
            cnt.message_subsubtype = 'request'
            cnt.counter_packets = control_channel_statistics[dpid]['readStateRequestCount']
            cnt.counter_bytes = control_channel_statistics[dpid]['readStateRequestBytes']
            cnt.save()
            # Count read-state reply messages
            cnt = OpenflowMessageCounter1_0()
            cnt.switch = sw
            cnt.counter_type = counter_type
            cnt.message_type = 'Controller-to-switch'
            cnt.message_subtype = 'read-state'
            cnt.message_subsubtype = 'reply'
            cnt.counter_packets = control_channel_statistics[dpid]['readStateReplyCount']
            cnt.counter_bytes = control_channel_statistics[dpid]['readStateReplyBytes']
            cnt.save()
            # Count send-packet messages
            cnt = OpenflowMessageCounter1_0()
            cnt.switch = sw
            cnt.counter_type = counter_type
            cnt.message_type = 'Controller-to-switch'
            cnt.message_subtype = 'send-packet'
            cnt.message_subsubtype = None
            cnt.counter_packets = control_channel_statistics[dpid]['sendPacketCount']
            cnt.counter_bytes = control_channel_statistics[dpid]['sendPacketBytes']
            cnt.save()
            # Count barrier request messages
            cnt = OpenflowMessageCounter1_0()
            cnt.switch = sw
            cnt.counter_type = counter_type
            cnt.message_type = 'Controller-to-switch'
            cnt.message_subtype = 'barrier'
            cnt.message_subsubtype = 'request'
            cnt.counter_packets = control_channel_statistics[dpid]['barrierRequestCount']
            cnt.counter_bytes = control_channel_statistics[dpid]['barrierRequestBytes']
            cnt.save()
            # Count barrier reply messages
            cnt = OpenflowMessageCounter1_0()
            cnt.switch = sw
            cnt.counter_type = counter_type
            cnt.message_type = 'Controller-to-switch'
            cnt.message_subtype = 'barrier'
            cnt.message_subsubtype = 'reply'
            cnt.counter_packets = control_channel_statistics[dpid]['barrierReplyCount']
            cnt.counter_bytes = control_channel_statistics[dpid]['barrierReplyBytes']
            cnt.save()
            # Count packet-in messages
            cnt = OpenflowMessageCounter1_0()
            cnt.switch = sw
            cnt.counter_type = counter_type
            cnt.message_type = 'Asynchronous'
            cnt.message_subtype = 'packet-in'
            cnt.message_subsubtype = None
            cnt.counter_packets = control_channel_statistics[dpid]['packetInCount']
            cnt.counter_bytes = control_channel_statistics[dpid]['packetInBytes']
            cnt.save()
            # Count flow-removed messages
            cnt = OpenflowMessageCounter1_0()
            cnt.switch = sw
            cnt.counter_type = counter_type
            cnt.message_type = 'Asynchronous'
            cnt.message_subtype = 'flow-removed'
            cnt.message_subsubtype = None
            cnt.counter_packets = control_channel_statistics[dpid]['flowRemovedCount']
            cnt.counter_bytes = control_channel_statistics[dpid]['flowRemovedBytes']
            cnt.save()
            # Count port-status messages
            cnt = OpenflowMessageCounter1_0()
            cnt.switch = sw
            cnt.counter_type = counter_type
            cnt.message_type = 'Asynchronous'
            cnt.message_subtype = 'port-status'
            cnt.message_subsubtype = None
            cnt.counter_packets = control_channel_statistics[dpid]['portStatusCount']
            cnt.counter_bytes = control_channel_statistics[dpid]['portStatusBytes']
            cnt.save()
            # Count hello request messages
            cnt = OpenflowMessageCounter1_0()
            cnt.switch = sw
            cnt.counter_type = counter_type
            cnt.message_type = 'Symmetric'
            cnt.message_subtype = 'hello'
            cnt.message_subsubtype = 'request'
            cnt.counter_packets = control_channel_statistics[dpid]['helloRequestCount']
            cnt.counter_bytes = control_channel_statistics[dpid]['helloRequestBytes']
            cnt.save()
            # Count hello reply messages
            cnt = OpenflowMessageCounter1_0()
            cnt.switch = sw
            cnt.counter_type = counter_type
            cnt.message_type = 'Symmetric'
            cnt.message_subtype = 'hello'
            cnt.message_subsubtype = 'reply'
            cnt.counter_packets = control_channel_statistics[dpid]['helloReplyCount']
            cnt.counter_bytes = control_channel_statistics[dpid]['helloReplyBytes']
            cnt.save()
            # Count echo request messages
            cnt = OpenflowMessageCounter1_0()
            cnt.switch = sw
            cnt.counter_type = counter_type
            cnt.message_type = 'Symmetric'
            cnt.message_subtype = 'echo'
            cnt.message_subsubtype = 'request'
            cnt.counter_packets = control_channel_statistics[dpid]['echoRequestCount']
            cnt.counter_bytes = control_channel_statistics[dpid]['echoRequestBytes']
            cnt.save()
            # Count echo reply messages
            cnt = OpenflowMessageCounter1_0()
            cnt.switch = sw
            cnt.counter_type = counter_type
            cnt.message_type = 'Symmetric'
            cnt.message_subtype = 'echo'
            cnt.message_subsubtype = 'reply'
            cnt.counter_packets = control_channel_statistics[dpid]['echoReplyCount']
            cnt.counter_bytes = control_channel_statistics[dpid]['echoReplyBytes']
            cnt.save()
            # Count vendor request messages
            cnt = OpenflowMessageCounter1_0()
            cnt.switch = sw
            cnt.counter_type = counter_type
            cnt.message_type = 'Symmetric'
            cnt.message_subtype = 'vendor'
            cnt.message_subsubtype = 'request'
            cnt.counter_packets = control_channel_statistics[dpid]['vendorRequestCount']
            cnt.counter_bytes = control_channel_statistics[dpid]['vendorRequestBytes']
            cnt.save()
            # Count vendor reply messages
            cnt = OpenflowMessageCounter1_0()
            cnt.switch = sw
            cnt.counter_type = counter_type
            cnt.message_type = 'Symmetric'
            cnt.message_subtype = 'vendor'
            cnt.message_subsubtype = 'reply'
            cnt.counter_packets = control_channel_statistics[dpid]['vendorReplyCount']
            cnt.counter_bytes = control_channel_statistics[dpid]['vendorReplyBytes']
            cnt.save()