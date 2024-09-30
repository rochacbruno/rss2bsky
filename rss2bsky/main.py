import os
import time
from datetime import datetime

import feedparser
import httpx
from atproto import Client, client_utils
from dynaconf import Dynaconf, Validator

REQUIRED_CONFIG = (
    "FEED_URL",
    "HANDLE",
    "PASSWORD",
    "START_POST_DATE",
    "INTERVAL",
    "LAST_POSTED_FILE",
    "DATE_FORMAT",
)

settings = Dynaconf(
    envvar_prefix="R2B",
    settings_files=["settings.toml"],
    validators=[Validator(*REQUIRED_CONFIG, required=True)],
    INTERVAL=60,
    START_POST_DATE="",
    LAST_POSTED_FILE="last_posted.txt",
    DATE_FORMAT="%a, %d %b %Y %H:%M:%S %z",
)


def read_last_posted_date():
    if os.path.exists(settings.LAST_POSTED_FILE):
        with open(settings.LAST_POSTED_FILE, "r") as file:
            return file.read().strip()
    return None


def save_last_posted_date(pub_date):
    with open(settings.LAST_POSTED_FILE, "w") as file:
        file.write(pub_date)


def truncate_text(description, link, limit):
    # cleanups
    if splitter := settings.get("SPLITTER"):
        if splitter in description:
            description = description.split(splitter, 1)[1].strip()

    link_text = "Read more on #fediverse"
    max_description_length = limit - len(link_text)
    if len(description) > max_description_length:
        description = description[:max_description_length]

    return (
        client_utils.TextBuilder().text(description + " ").link(link_text, link)
    )


def download_image(url):
    response = httpx.get(url)
    if response.status_code == 200:
        return response.content
    return None


def is_image(url):
    return url.lower().endswith((".jpg", ".jpeg", ".png"))


def post_to_bluesky(client, message, image=None):
    print("posting to bluesky")
    # embed = None
    if image:
        client.send_image(
            text=message,
            image=image,
            image_alt="Image coming from the Fediverse",
        )
    else:
        client.send_post(text=message)


def main():
    # Read RSS feed URL and start date from environment variables
    feed_url = settings.FEED_URL
    if not feed_url:
        raise ValueError("FEED_URL environment variable is not set")

    start_post_date_str = settings.START_POST_DATE
    start_post_date = (
        datetime.strptime(start_post_date_str, settings.DATE_FORMAT)
        if start_post_date_str
        else None
    )

    # Initialize Bluesky client
    bsky_handle = settings.HANDLE
    bsky_password = settings.PASSWORD
    if not bsky_handle or not bsky_password:
        raise ValueError("HANDLE and PASSWORD must be set")

    client = Client()
    client.login(bsky_handle, bsky_password)

    print(f"starting loop with {feed_url}")

    while True:
        # Fetch RSS feed
        feed = feedparser.parse(feed_url)

        # Read last posted date
        last_posted_date_str = read_last_posted_date()
        last_posted_date = (
            datetime.strptime(last_posted_date_str, settings.DATE_FORMAT)
            if last_posted_date_str
            else None
        )

        print(f"Processing {len(feed.entries)}")
        # Process feed items in reverse order
        for entry in reversed(feed.entries):
            pub_date = datetime.strptime(entry.published, settings.DATE_FORMAT)

            if (not last_posted_date or pub_date > last_posted_date) and (
                not start_post_date or pub_date > start_post_date
            ):
                print(f"Preparing {entry.link}")
                # Truncate description to 300 characters
                message = truncate_text(entry.description, entry.link, 300)

                # Check if the entry has an image enclosure
                image = None
                if (enclosures := entry.get("enclosures")) and is_image(
                    enclosures[0].get("url")
                ):
                    image = download_image(enclosures[0]["url"])

                if image:
                    print("Entry has an image")

                # Post to Bluesky
                post_to_bluesky(client, message, image)

                # Save the last posted date
                save_last_posted_date(entry.published)
            else:
                print(f"skipped {entry.link}, already posted")

        # Wait for 30 seconds before the next check
        time.sleep(settings.INTERVAL)


if __name__ == "__main__":
    main()
