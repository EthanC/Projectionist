import json
import logging
from datetime import datetime
from os import environ
from sys import stdout
from typing import Any, Dict, Optional, Self

import dotenv
import uvicorn
from discord_webhook import DiscordEmbed, DiscordWebhook
from fastapi import FastAPI, Form, HTTPException, Request
from loguru import logger
from loguru_discord import DiscordSink

from handlers import Events, Intercept


class Projectionist:
    """
    Receive Plex webhooks and report events via Discord.

    https://github.com/EthanC/Projectionist
    """

    def __init__(self: Self) -> None:
        """Initialize the FastAPI service."""

        self.app: FastAPI = FastAPI()

        @self.app.post("/")
        async def Receive(req: Request, payload: str = Form()) -> None:
            """Determine the proper event handler for incoming HTTP POST requests."""

            payload: Dict[str, Any] = json.loads(payload)

            logger.debug(
                f"Received HTTP POST to / from {req.client.host}:{req.client.port}"
            )
            logger.trace(payload)

            embed: Optional[DiscordEmbed] = None

            # https://support.plex.tv/articles/115002267687-webhooks/
            match (event := payload.get("event")):
                case "media.play":
                    if environ.get("PLEX_EVENT_MEDIAPLAY"):
                        embed = Events.MediaPlay(self, payload)
                case "media.pause":
                    # TODO: Potential reuse of media.play?
                    Events.Unsupported(self, event)
                case "media.resume":
                    # TODO: Potential reuse of media.play?
                    Events.Unsupported(self, event)
                case "media.stop":
                    # TODO: Potential reuse of media.play?
                    Events.Unsupported(self, event)
                case "media.scrobble":
                    # TODO: Potential reuse of media.play?
                    Events.Unsupported(self, event)
                case "media.rate":
                    Events.Unsupported(self, event)
                case "library.on.deck":
                    Events.Unsupported(self, event)
                case "library.new":
                    Events.Unsupported(self, event)
                case "admin.database.backup":
                    Events.Unsupported(self, event)
                case "admin.database.corrupted":
                    Events.Unsupported(self, event)
                case "device.new":
                    Events.Unsupported(self, event)
                case "playback.started":
                    # TODO: Potential reuse of media.play?
                    Events.Unsupported(self, event)
                case _:
                    logger.warning(
                        f"Payload from Plex contains an unknown event type ({event})"
                    )
                    logger.debug(payload)

                    raise HTTPException(404, "UNKNOWN_EVENT")

            if embed:
                Projectionist.Notify(self, embed)

    def Start(self: Self) -> None:
        """Initialize Projectionist and begin primary functionality."""

        logger.info("Projectionist")
        logger.info("https://github.com/EthanC/Projectionist")

        # Reroute standard logging to Loguru
        logging.basicConfig(handlers=[Intercept()], level=0, force=True)

        if dotenv.load_dotenv():
            logger.success("Loaded environment variables")
            logger.trace(environ)

        if level := environ.get("LOG_LEVEL"):
            logger.remove()
            logger.add(stdout, level=level)

            logger.success(f"Set console logging level to {level}")

        if url := environ.get("LOG_DISCORD_WEBHOOK_URL"):
            logger.add(
                DiscordSink(url),
                level=environ.get("LOG_DISCORD_WEBHOOK_LEVEL"),
                backtrace=False,
            )

            logger.success(f"Enabled logging to Discord webhook")
            logger.trace(url)

        uvicorn.run(self.app, port=int(environ.get("PROJECTIONIST_PORT", 8000)))

    def Notify(self: Self, embed: DiscordEmbed) -> None:
        """Report Plex events to the configured Discord webhook."""

        if not (url := environ.get("DISCORD_WEBHOOK_URL")):
            logger.info("Discord webhook for notifications is not set")

            return

        embed.set_color("EBAF00")
        embed.set_timestamp(datetime.now().timestamp())

        DiscordWebhook(url=url, embeds=[embed], rate_limit_retry=True).execute()


Projectionist().Start()
