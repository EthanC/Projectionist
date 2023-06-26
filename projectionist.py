import logging
from datetime import datetime
from os import environ
from typing import Any, Dict, Optional, Self

import dotenv
import uvicorn
from discord_webhook import DiscordEmbed, DiscordWebhook
from fastapi import Body, FastAPI, HTTPException, Request
from loguru import logger
from notifiers.logging import NotificationHandler

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
        async def Receive(req: Request, payload: Dict[str, Any] = Body()) -> None:
            """Determine the proper event handler for incoming HTTP POST requests."""

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

        if dotenv.load_dotenv():
            logger.success("Loaded environment variables")
            logger.trace(environ)

        # Reroute standard logging to Loguru
        logging.basicConfig(handlers=[Intercept()], level=0, force=True)

        if logUrl := environ.get("DISCORD_LOG_WEBHOOK"):
            if not (logLevel := environ.get("DISCORD_LOG_LEVEL")):
                logger.critical("Level for Discord webhook logging is not set")

                return

            logger.add(
                NotificationHandler(
                    "slack", defaults={"webhook_url": f"{logUrl}/slack"}
                ),
                level=logLevel,
                format="```\n{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}\n```",
            )

            logger.success(f"Enabled logging to Discord webhook")
            logger.trace(logUrl)

        uvicorn.run(self.app, port=int(environ.get("PROJECTIONIST_PORT", 8000)))

    def Notify(self: Self, embed: DiscordEmbed) -> None:
        """Report Plex events to the configured Discord webhook."""

        if not (url := environ.get("DISCORD_NOTIFY_WEBHOOK")):
            logger.info("Discord webhook for notifications is not set")

            return

        embed.set_color("EBAF00")
        embed.set_timestamp(datetime.now().timestamp())

        DiscordWebhook(url=url, embeds=[embed], rate_limit_retry=True).execute()


Projectionist().Start()
