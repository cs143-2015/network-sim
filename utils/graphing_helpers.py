from components.packet_types import FlowPacket
from events.event_types import PacketReceivedEvent
from events.event_types.graph_events import FlowThroughputEvent


def get_flow_throughput_events(received_events):
    """
    Get a list of flow throughput events derived from the packet received events

    :param received_events: List of packet received events
    :type received_events: list[PacketReceivedEvent]
    :return:
    :rtype:
    """
    # Dictionary mapping flow IDs to bits sent for that flow
    bits_sent = {}
    # Newly added flow throughput events
    flow_t_events = []
    for event in received_events:
        if isinstance(event, PacketReceivedEvent):
            # Only include flow packets when calculating flow throughput
            if not isinstance(event.packet, FlowPacket):
                continue
            flow_id = event.packet.flow_id
            time_received = event.time
            packet_size = event.packet.size() * 8  # Packet size in bits
            # Set initial amount of bits sent to 0
            if flow_id not in bits_sent:
                bits_sent[flow_id] = 0
                flow_t_events.append(FlowThroughputEvent(0, flow_id, 0))
            # Add packet size to the bits sent
            bits_sent[flow_id] += packet_size
            # Get the time it has taken to send these bits (in seconds)
            time_to_sent = time_received / 1000
            # Calculate throughput bps
            throughput = bits_sent[flow_id] / time_to_sent
            flow_event = FlowThroughputEvent(time_received, flow_id, throughput)
            flow_t_events.append(flow_event)
        else:
            raise ValueError("Event is not a PacketReceivedEvent.")
    return flow_t_events
