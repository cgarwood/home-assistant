import json
import logging
from pydispatch import dispatcher

from .const import (
    DOMAIN,
    SIGNAL_NODE_ADDED,
    SIGNAL_NODE_QUERY_COMPLETE,
    SIGNAL_VALUE_CHANGED,
)

_LOGGER = logging.getLogger(__name__)


class ZWaveManager:
    """Handle OpenZWave MQTT messages"""

    def __init__(self):
        pass

    def process_message(self, msg):
        """Process an OpenZWave MQTT Message."""

        # Split up the topic for easier parsing.
        # Topics start with: /OpenZwave/<instance>
        # Node topics: /OpenZwave/<instance>/node/<node_id>
        # Value topics: /OpenZwave/<instance>/node/<node_id>/<value_id>

        topic = msg.topic.split("/")
        topic.pop(0)
        del topic[-1]

        payload = json.loads(msg.payload)

        # _LOGGER.debug("Received Message: Topic %s, Payload: %s", topic, payload)

        # Based on topic, determine how to handle message
        if len(topic) == 2:
            self.process_general_message(topic, payload)

        if len(topic) > 2:
            if topic[2] == "node":
                if len(topic) == 5:
                    self.process_value_message(topic, payload)
                else:
                    self.process_node_message(topic, payload)

    def process_general_message(self, topic, payload):
        """Process general OpenZWave Messages."""
        if "Network" in payload:
            # Network data
            pass

    def process_node_message(self, topic, payload):
        """Process node messages."""
        node_id = topic[3]
        _LOGGER.debug("process_node_message: %s :: %s", topic, payload)

        if payload["Event"] == SIGNAL_NODE_ADDED:
            dispatcher.send(
                signal=SIGNAL_NODE_ADDED, sender=DOMAIN, **{"node": payload}
            )

        if payload["Event"] == SIGNAL_NODE_QUERY_COMPLETE:
            dispatcher.send(
                signal=SIGNAL_NODE_QUERY_COMPLETE, sender=DOMAIN, **{"node": payload}
            )

    def process_value_message(self, topic, payload):
        """Process value messages."""
        node_id = topic[3]
        value_id = topic[4]
        _LOGGER.debug(
            "process_value_message: Node %s :: Instance %s :: Index %s :: %s :: Value %s",
            node_id,
            payload["Instance"],
            payload["Index"],
            payload["CommandClass"],
            payload["Value"],
        )
        if payload["Event"] == SIGNAL_VALUE_CHANGED:
            dispatcher.send(
                signal=SIGNAL_VALUE_CHANGED, sender=DOMAIN, **{"value": payload}
            )
