#!/usr/bin/env python3

import datetime
import filecmp
import mimetypes
import os
import pathlib
import tempfile
import textwrap

import feedgen.feed

from . import cli, config, remote
from .log import logger


def _mimetype(url):
    return mimetypes.guess_type(url)[0] or 'application/octet-stream'


def generate_feed(username, feed_url):
    media_list, apirespobj = remote.timeline(username)

    fg = feedgen.feed.FeedGenerator()
    fg.id(feed_url)
    fg.title(f"{username}'s Instagram feed")
    instagram_home = f'https://www.instagram.com/{username}/'
    fg.author({'name': apirespobj['user']['full_name'], 'uri': instagram_home})
    fg.link(href=feed_url, rel='self', type='application/atom+xml')
    fg.link(href=instagram_home, rel='alternate', type='text/html')

    tz_utc = datetime.timezone.utc
    if not media_list:
        fg.updated(datetime.datetime.now(tz=tz_utc))
    else:
        fg.updated(datetime.datetime.fromtimestamp(media_list[0]['timestamp'], tz=tz_utc))
        for media in media_list:
            url = f'https://www.instagram.com/p/{media["code"]}/'
            is_video = media['is_video']
            image_url = media['image_url']
            video_url = media['video_url']
            height = media['height']
            width = media['width']
            timestamp = media['timestamp']
            caption = media['caption']

            fe = fg.add_entry()
            fe.id(url)
            fe.link(href=url, rel='alternate', type='text/html')
            fe.link(href=url, rel='alternate', type=_mimetype(image_url))
            if is_video:
                fe.link(href=url, rel='alternate', type=_mimetype(video_url))
            fe.title(caption)
            fe.published(datetime.datetime.fromtimestamp(timestamp, tz=tz_utc))
            fe.updated(datetime.datetime.fromtimestamp(timestamp, tz=tz_utc))
            imgtag = f'<img width="{width}" height="{height}" src="{image_url}" alt="{image_url}">'
            if is_video:
                content = f'<a href="{video_url}">{imgtag}</a>'
            else:
                content = imgtag
            fe.content(textwrap.dedent(content), type='html')

    return fg.atom_str(pretty=True).decode('utf-8')


def overwrite_on_change(content, path):
    path = pathlib.Path(path)
    fd, tmppath = tempfile.mkstemp(prefix=path.name, dir=path.parent)
    with os.fdopen(fd, 'w') as fp:
        fp.write(content)
    if path.exists() and filecmp.cmp(path, tmppath):
        os.unlink(tmppath)
        logger.info(f'feed unchanged: {path}')
    else:
        os.replace(tmppath, path)
        logger.info(f'feed updated: {path}')


def main():
    parser = cli.ArgumentParser(description="Generate Atom feed for a user's timeline.")
    parser.add_argument('config_path', help='path to the config file (generate with instaconfig)')
    args = parser.parse_args()
    cli.adjust_verbosity(args)

    def load_config_and_generate():
        conf = config.load_config(args.config_path)
        for attr in ('feed_url', 'local_path'):
            if not getattr(conf.feed, attr, None):
                raise config.ConfigError(f'feed.{attr} required')

        atom = generate_feed(conf.username, conf.feed.feed_url)
        overwrite_on_change(atom, conf.feed.local_path)

    cli.sandbox(load_config_and_generate)


if __name__ == '__main__':
    main()
