import asyncio
import json
import os
import random
import ssl
import uuid
import warnings
from enum import Enum
from typing import Generator, Any
from typing import Literal
from typing import Optional
from typing import Union

import certifi
import httpx
import websockets.client as websockets


"""
EdgeGPT - reverse engineer bing chat: https://github.com/acheong08/EdgeGPT
author: https://github.com/acheong08
all credits to him.
little personal touch (by honraVT) to catch uncensored responses, on line 290
"""

DELIMITER = "\x1e"

# Generate random IP between range 13.104.0.0/14
FORWARDED_IP = (
    f"13.{random.randint(104, 107)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
)

HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "sec-ch-ua": '"Not_A Brand";v="99", "Microsoft Edge";v="110", "Chromium";v="110"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"109.0.1518.78"',
    "sec-ch-ua-full-version-list": '"Chromium";v="110.0.5481.192", "Not A(Brand";v="24.0.0.0", "Microsoft Edge";v="110.0.1587.69"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": "",
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"15.0.0"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-ms-client-request-id": str(uuid.uuid4()),
    "x-ms-useragent": "azsdk-js-api-client-factory/1.0.0-beta.1 core-rest-pipeline/1.10.0 OS/Win32",
    "Referer": "https://www.bing.com/search?q=Bing+AI&showconv=1&FORM=hpcodx",
    "Referrer-Policy": "origin-when-cross-origin",
    "x-forwarded-for": FORWARDED_IP,
}

HEADERS_INIT_CONVER = {
    "authority": "edgeservices.bing.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="110", "Not A(Brand";v="24", "Microsoft Edge";v="110"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"110.0.1587.69"',
    "sec-ch-ua-full-version-list": '"Chromium";v="110.0.5481.192", "Not A(Brand";v="24.0.0.0", "Microsoft Edge";v="110.0.1587.69"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"15.0.0"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.69",
    "x-edge-shopping-flag": "1",
    "x-forwarded-for": "1.1.1.1",
}

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


class NotAllowedToAccess(Exception):
    pass


class RequestThrottledError(Exception):
    pass


class ConversationStyle(Enum):
    creative = "h3relaxedimg"
    balanced = "galileo"
    precise = "h3precise"


CONVERSATION_STYLE_TYPE = Optional[
    Union[ConversationStyle, Literal["creative", "balanced", "precise"]]
]


def append_identifier(msg: dict) -> str:
    """
    Appends special character to end of message to identify end of message
    """
    # Convert dict to json string
    return json.dumps(msg) + DELIMITER


def get_ran_hex(length: int = 32) -> str:
    """
    Returns random hex string
    """
    return "".join(random.choice("0123456789abcdef") for _ in range(length))


class ChatHubRequest:
    """
    Request object for ChatHub
    """

    def __init__(
            self,
            conversation_signature: str,
            client_id: str,
            conversation_id: str,
            invocation_id: int = 0,
    ) -> None:
        self.struct: dict = {}

        self.client_id: str = client_id
        self.conversation_id: str = conversation_id
        self.conversation_signature: str = conversation_signature
        self.invocation_id: int = invocation_id

    def update(
            self,
            prompt: str,
            conversation_style: CONVERSATION_STYLE_TYPE,
            options: list | None = None,
    ) -> None:
        """
        Updates request object
        """
        if options is None:
            options = [
                "deepleo",
                "enable_debug_commands",
                "disable_emoji_spoken_text",
                "enablemm",
            ]
        if conversation_style:
            if not isinstance(conversation_style, ConversationStyle):
                conversation_style = getattr(ConversationStyle, conversation_style)
            options = [
                "nlu_direct_response_filter",
                "deepleo",
                "disable_emoji_spoken_text",
                "responsible_ai_policy_235",
                "enablemm",
                conversation_style.value,
                "dtappid",
                "cricinfo",
                "cricinfov2",
                "dv3sugg",
            ]
        self.struct = {
            "arguments": [
                {
                    "source": "cib",
                    "optionsSets": options,
                    "sliceIds": [
                        "222dtappid",
                        "225cricinfo",
                        "224locals0",
                    ],
                    "traceId": get_ran_hex(32),
                    "isStartOfSession": self.invocation_id == 0,
                    "message": {
                        "author": "user",
                        "inputMethod": "Keyboard",
                        "text": prompt,
                        "messageType": "Chat",
                    },
                    "conversationSignature": self.conversation_signature,
                    "participant": {
                        "id": self.client_id,
                    },
                    "conversationId": self.conversation_id,
                },
            ],
            "invocationId": str(self.invocation_id),
            "target": "chat",
            "type": 4,
        }
        self.invocation_id += 1


class Conversation:
    """
    Conversation API
    """

    def __init__(
            self,
            cookie_value: str = str,
            proxy: str | None = None,
    ) -> None:
        self.struct: dict = {
            "conversationId": None,
            "clientId": None,
            "conversationSignature": None,
            "result": {"value": "Success", "message": None},
        }
        self.session = httpx.Client(
            proxies=proxy,
            timeout=30,
            headers=HEADERS_INIT_CONVER,
        )

        self.session.cookies.set("_U", cookie_value)

        # Send GET request
        response = self.session.get(
            url=os.environ.get("BING_PROXY_URL") or "https://edgeservices.bing.com/edgesvc/turing/conversation/create")
        if response.status_code != 200:
            response = self.session.get(
                "https://edge.churchless.tech/edgesvc/turing/conversation/create",
            )
        if response.status_code != 200:
            print(f"Status code: {response.status_code}")
            print(response.text)
            print(response.url)
            raise Exception("Authentication failed")
        try:
            self.struct = response.json()
        except (json.decoder.JSONDecodeError, NotAllowedToAccess) as exc:
            raise Exception(
                "Authentication failed. You have not been accepted into the beta.",
            ) from exc
        if self.struct["result"]["value"] == "UnauthorizedRequest":
            raise NotAllowedToAccess(self.struct["result"]["message"])


class ChatHub:
    """
    Chat API
    """

    def __init__(self, conversation: Conversation) -> None:
        self.wss: websockets.WebSocketClientProtocol | None = None
        self.request = ChatHubRequest(
            conversation_signature=conversation.struct["conversationSignature"],
            client_id=conversation.struct["clientId"],
            conversation_id=conversation.struct["conversationId"],
        )

    async def ask_stream(
            self,
            prompt: str,
            wss_link: str,
            conversation_style: CONVERSATION_STYLE_TYPE = None,
    ) -> Generator[str, None, None]:
        """
        Ask a question to the bot
        """
        if self.wss and not self.wss.closed:
            await self.wss.close()
        # Check if websocket is closed
        self.wss = await websockets.connect(
            wss_link,
            extra_headers=HEADERS,
            max_size=None,
            ssl=ssl_context,
        )
        await self.__initial_handshake()
        # Construct a ChatHub request
        self.request.update(prompt=prompt, conversation_style=conversation_style)
        # Send request
        await self.wss.send(append_identifier(self.request.struct))
        final = False
        resp_text = ""
        while not final:
            objects = str(await self.wss.recv()).split(DELIMITER)
            for obj in objects:
                if obj is None or not obj:
                    continue
                response = json.loads(obj)
                if response.get("type") == 1 and response["arguments"][0].get(
                        "messages",
                ):
                    revoke = response["arguments"][0]["messages"][0]["contentOrigin"]
                    if revoke == "Apology":
                        final = True
                        warnings.warn("[!] Revoked response (1)")
                        yield True, resp_text
                    resp_text = response["arguments"][0]["messages"][0].get("text")
                    yield False, resp_text
                elif response.get("type") == 2:
                    limit_reached = response["item"]["result"]["value"]
                    if limit_reached != "Success":
                        await self.close()
                        raise RequestThrottledError(f"Limit reached! request is: {limit_reached}")
                    revoke = response["item"]["messages"][1]["contentOrigin"]
                    if revoke == "Apology":
                        warnings.warn("[!] Revoked response (2)")
                        final = True
                        yield True, None
                    elif revoke == "NluDirectResponse":
                        warnings.warn("[!] Revoked response (2) by NluDirectResponse")
                        final = True
                        yield True, None
                    warnings.warn(f'[!] Prompt Offence:  {response["item"]["messages"][0]["offense"]}')
                    warnings.warn(f'[!] Response Offence:  {response["item"]["messages"][1]["offense"]}')
                    final = True
                    yield True, response["item"]["messages"][1].get("text")

    async def __initial_handshake(self) -> None:
        await self.wss.send(append_identifier({"protocol": "json", "version": 1}))
        await self.wss.recv()

    async def close(self) -> None:
        """
        Close the connection
        """
        if self.wss and not self.wss.closed:
            await self.wss.close()


class Chatbot:
    """
    Combines everything to make it seamless
    """

    def __init__(
            self,
            cookie_value: str,
            proxy: str | None = None,
            warning_mgs: bool = False
    ) -> None:
        self.cookie_value: str = cookie_value
        self.proxy: str | None = proxy
        self.chat_hub: ChatHub = ChatHub(
            Conversation(self.cookie_value, self.proxy),
        )
        if not warning_mgs:
            warnings.filterwarnings("ignore")

    async def ask(
            self,
            prompt: str,
            wss_link: str = "wss://sydney.bing.com/sydney/ChatHub",
            conversation_style: CONVERSATION_STYLE_TYPE = None,
    ) -> Any | None:
        """
        Ask a question to the bot
        """
        async for final, response in self.chat_hub.ask_stream(
                prompt=prompt,
                conversation_style=conversation_style,
                wss_link=wss_link,
        ):
            if final:
                await self.chat_hub.close()
                return response
        await self.chat_hub.close()
        return None

    async def close(self) -> None:
        """
        Close the connection
        """
        await self.chat_hub.close()

    async def reset(self, cookie: str | None = None) -> None:
        """
        Reset the conversation
        """
        if cookie is None:
            cookie = self.cookie_value
        await self.close()
        self.chat_hub = ChatHub(Conversation(cookie))
