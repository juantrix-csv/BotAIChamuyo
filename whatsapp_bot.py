import os
from whatsapp import Client  # provided by pywhatsapp
from yowsup.stacks import YowStack
from yowsup.stacks import YOWSUP_CORE_LAYERS, YOWSUP_PROTOCOL_LAYERS_FULL
from yowsup.layers import YowLayerEvent
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity
from yowsup.layers.auth import YowAuthenticationProtocolLayer
from yowsup.layers.coder import YowCoderLayer
from yowsup.common import YowConstants
from yowsup import env

from script import read_context, respond_to_message


class WhatsAppBotLayer(YowInterfaceLayer):
    """Layer that listens for incoming messages and replies using OpenAI."""

    def __init__(self, context: str, sender: Client) -> None:
        super().__init__()
        self.context = context
        self.sender = sender

    @ProtocolEntityCallback("message")
    def on_message(self, message_entity: TextMessageProtocolEntity) -> None:
        """Handle incoming messages from WhatsApp."""
        body = message_entity.getBody()
        sender_jid = message_entity.getFrom(False)
        response = respond_to_message(body, self.context)
        self.sender.send_message(sender_jid, response)
        self.ack(message_entity)


def start_whatsapp_bot() -> None:
    """Initialize the Yowsup stack and start the WhatsApp bot."""
    login = os.getenv("WHATSAPP_LOGIN")
    password = os.getenv("WHATSAPP_PASSWORD")
    if not login or not password:
        raise RuntimeError("WHATSAPP_LOGIN and WHATSAPP_PASSWORD must be set")

    context = read_context("archivo1.txt") + "\n" + read_context("archivo2.txt")
    sender = Client(login, password)

    layers = (WhatsAppBotLayer(context, sender),) + YOWSUP_PROTOCOL_LAYERS_FULL + YOWSUP_CORE_LAYERS
    stack = YowStack(layers)
    stack.setProp(YowAuthenticationProtocolLayer.PROP_PASSIVE, True)
    stack.setProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS, (login, password))
    stack.setProp(YowNetworkLayer.PROP_ENDPOINT, YowConstants.ENDPOINTS[0])
    stack.setProp(YowCoderLayer.PROP_DOMAIN, YowConstants.DOMAIN)
    stack.setProp(YowCoderLayer.PROP_RESOURCE, env.YowsupEnv.getCurrent().getResource())

    stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
    stack.loop()


if __name__ == "__main__":
    start_whatsapp_bot()
