from typing import Any, Dict, Self, Union

from discord_webhook import DiscordEmbed
from loguru import logger

from .tmdb import TMDB


class Events:
    """Class containing handlers for Plex webhook events."""

    def MediaPlay(self: Self, payload: Dict[str, Any]) -> DiscordEmbed:
        """Handler for the media.play Plex webhook event."""

        account: Dict[str, Union[int, str]] = payload.get("Account", {})
        server: Dict[str, str] = payload.get("Server", {})
        player: Dict[str, Union[bool, str]] = payload.get("Player", {})
        metadata: Dict[str, Any] = payload.get("Metadata", {})

        embed: DiscordEmbed = DiscordEmbed()

        if user := account.get("title"):
            embed.set_author(user, icon_url=account.get("thumb"))

        embed.set_description("Now Playing")

        match (mType := metadata.get("type")):
            case "movie":
                title: str = metadata.get("title")

                embed.set_title(title)

                if image := TMDB.Thumbnail(self, title, mType):
                    embed.set_thumbnail(image)

                embed.set_url(TMDB.Info(self, title, mType))
            case "episode":
                series: str = metadata.get("grandparentTitle")
                title: str = metadata.get("title")
                season: int = metadata.get("parentIndex", 0)
                episode: int = metadata.get("index", 0)

                embed.set_title(series)

                embed.add_embed_field("Title", title)
                embed.add_embed_field("Season", f"{season:,}")
                embed.add_embed_field("Episode", f"{episode:,}")

                if image := TMDB.Thumbnail(self, series, mType):
                    embed.set_thumbnail(image)

                embed.set_url(TMDB.Info(self, series, mType))
            case "track":
                title: str = metadata.get("title")
                artist: str = metadata.get("parentTitle")

                embed.set_title(f"{artist} - {title}")
            case "clip":
                title: str = metadata.get("title")
                subtype: str = metadata.get("subtype")

                embed.set_title(f"{title} ({subtype})")
            case _:
                logger.warning(
                    f"Payload from Plex contains an unsupported media.play metadata type ({mType})"
                )
                logger.debug(metadata)

        if library := metadata.get("librarySectionTitle"):
            embed.add_embed_field("Library", library)

        if device := player.get("title"):
            embed.add_embed_field("Device", device)

        if "local" in player.keys():
            embed.add_embed_field(
                "Connection", "Local" if player["local"] else "Remote"
            )

        if server := server.get("title"):
            embed.set_footer(text=server, icon_url="https://i.imgur.com/HAcu5a1.png")

        return embed

    def Unsupported(self: Self, event: str) -> None:
        """Function to catch known, unsupported Plex webhook events."""

        # https://support.plex.tv/articles/115002267687-webhooks/
        logger.info(f"Plex event type {event} is not yet implemented")
        logger.info("Contribute at https://github.com/EthanC/Projectionist")
