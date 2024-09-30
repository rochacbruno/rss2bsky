# R2B

## RSS TO BLUESKY

Crosspost entries from RSS Feed to Bluesky.

> **TIP** Every Mastodon account has an RSS feed :)

---

> **NOTE** This project was created specifically for GoToSocial RSS feed format, if you implement support for other feed format please send a PR

## Installation

```console
$ pip install rss2bsky

# OR

$ git clone https://github.com/rochacbruno/rss2bsky
$ python -m pip install ./rss2bsky
```

## Configuration

The configuration uses [dynaconf](https://dynaconf.com) so it can
be configured by putting variables on `settings.toml` file
or **alternatively exporting to environment variables prefixed with `R2B`

**toml**
```toml
FEED_URL = "https://YOUR_FEED_URL"
HANDLE = "you.bsky.social"
PASSWORD = "your-app-password"
START_POST_DATE = "Mon, 29 Sep 2024 23:59:59 +0100"
```
**env**
```bash
R2B_FEED_URL="https://YOUR_FEED_URL"
R2B_HANDLE="you.bsky.social"
R2B_PASSWORD="your-app-password"
R2B_START_POST_DATE="Mon, 29 Sep 2024 23:59:59 +0100"
```

## Usage

Choose one of the options that fits your environment.

```console
$ pip install rss2bsky
```

```
$ rss2bsky
```

Or setting vars directly

```console
R2B_HANDLE=foo.bsky.app R2B_PASSWORD=batata-123 R2B_FEED_URL=https://foo.bar.rss rss2bsky
```

### Alternative usages

```console
# Python module directly
$ python -m rss2bsky
```

```console
# UVX
$ uvx rss2bsky
```

### Output

#### Success

```console
starting loop with https://go.rocha.social/@bruno/feed.rss
Processing 20
skipped https://go.rocha.social/@bruno/statuses/01J8N5DZMN7HME5XD1V67Z699Q, already posted
Posting https://go.rocha.social/@bruno/statuses/01J8NJBXSBQ8NFVCB9GHNY0W7C, to bluesky
...
```

#### Config error

```console
dynaconf.validator.ValidationError: FEED_URL is required in env main
```

#### Auth error

```console
atproto_client.exceptions.UnauthorizedError: Response(success=False, status_code=401, ...)
```
