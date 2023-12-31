# Projectionist

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/EthanC/Projectionist/ci.yml?branch=main) ![Docker Pulls](https://img.shields.io/docker/pulls/ethanchrisp/projectionist?label=Docker%20Pulls) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/ethanchrisp/projectionist/latest?label=Docker%20Image%20Size)


Projectionist receives Plex webhooks and reports events via Discord.

<p align="center">
    <img src="https://i.imgur.com/o8FnsDe.png" draggable="false">
</p>

## Setup

Although not required, a [Discord Webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) is recommended for notifications.

**Environment Variables:**

-   `LOG_LEVEL`: [Loguru](https://loguru.readthedocs.io/en/stable/api/logger.html) severity level to write to the console.
-   `LOG_DISCORD_WEBHOOK_URL`: [Discord Webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) URL to receive log events.
-   `LOG_DISCORD_WEBHOOK_LEVEL`: Minimum [Loguru](https://loguru.readthedocs.io/en/stable/api/logger.html) severity level to forward to Discord.
-   `PROJECTIONIST_PORT`: HTTP port to bind the Projectionist API to. Default is `8000`.
-   `PLEX_EVENT_MEDIAPLAY`: Boolean toggle for the [`media.play`](https://support.plex.tv/articles/115002267687-webhooks/) Plex event. Default is False.
-   `TMDB_API_KEY`: API Key for [The Movie Database (TMDB)](https://developer.themoviedb.org/docs), required to enable media thumbnails.
-   `DISCORD_WEBHOOK_URL`: [Discord Webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) URL to receive Plex event notifications.

### Docker (Recommended)

Modify the following `docker-compose.yml` example file, then run `docker compose up`.

```yml
version: "3"
services:
  projectionist:
    container_name: projectionist
    image: ethanchrisp/projectionist:latest
    environment:
      LOG_LEVEL: INFO
      LOG_DISCORD_WEBHOOK_URL: https://discord.com/api/webhooks/YYYYYYYY/YYYYYYYY
      LOG_DISCORD_WEBHOOK_LEVEL: WARNING
      PROJECTIONIST_PORT: 8000
      PLEX_EVENT_MEDIAPLAY: true
      TMDB_API_KEY: XXXXXXXX
      DISCORD_WEBHOOK_URL: https://discord.com/api/webhooks/XXXXXXXX/XXXXXXXX
    restart: unless-stopped
```

### Standalone

Projectionist is built for [Python 3.11](https://www.python.org/) or greater.

1. Install required dependencies using [Poetry](https://python-poetry.org/): `poetry install`
2. Rename `.env.example` to `.env`, then provide the environment variables.
3. Start Projectionist: `python projectionist.py`

### Plex

Notice: Webhook functionality is exclusive to [Plex Pass](https://www.plex.tv/en-gb/plex-pass/) subscribers.

1. In Plex, open Settings, then select Webhooks.
2. Add a Webhook and enter the URL that points to your instance of Projectionist.
