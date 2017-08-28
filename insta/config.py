import configparser
import pathlib

from . import cli
from .log import logger


_here = pathlib.Path(__file__).resolve().parent
_root = _here.parent

SAMPLE_CONFIG = '''\
[common]

# Instagram user handle.
username = instagram

# Data directory for database and downloaded media; can be overridden by more
# specific configurations.
#
# The path undergoes tilde expansion. If a relative path is given, it is deemed
# as relative to the parent directory of the `insta` package. The same path
# resolution rules apply to other path settings below.
data_dir = ~/data/instagram

# Path for the SQLite database; defaults to {data_dir}/databases/{username}.db.
# database_path =

# Directory for downloaded images; defaults to {data_dir}/media/{username}/.
# images_dir =

# Directory for downloaded videos; defaults to images_dir.
# videos_dir =

# Whether to download video cover images; defaults to True.
# download_video_covers = False

[feed]

# The URL at which the generated feed will be served; used as atom:id and
# atom:feed with rel=self in atom:feed.
feed_url = https://example.org/instagram.atom

# Path to write the generated feed on the local filesystem.
local_path = /var/www/instafeed/instagram.atom

# Whether to download media of new entries; defaults to False.
# download_media = True
'''


class ConfigError(Exception):
    pass


class SubConfig(object):
    pass


class Config(object):
    # conf is a configparser.ConfigParser object.
    def __init__(self, conf):
        self._conf = conf

        self.username = conf.get('common', 'username', fallback=None)
        if not self.username:
            raise ConfigError('username required')

        self.data_dir = self._resolve_path(
            conf.get('common', 'data_dir', fallback=None),
            is_dir=True, mkdir=True,
        )

        default_database_path = ((self.data_dir / 'databases' / f'{self.username}.db')
                                 if self.data_dir is not None else None)
        self.database_path = self._resolve_path(
            conf.get('common', 'database_path', fallback=default_database_path),
            is_dir=False, mkdir=True,
        )
        if not self.database_path:
            raise ConfigError('database_path required')

        default_images_dir = ((self.data_dir / 'media' / self.username)
                              if self.data_dir is not None else None)
        self.images_dir = self._resolve_path(
            conf.get('common', 'images_dir', fallback=default_images_dir),
            is_dir=True, mkdir=True,
        )

        default_videos_dir = self.images_dir
        self.videos_dir = self._resolve_path(
            conf.get('common', 'videos_dir', fallback=default_videos_dir),
            is_dir=True, mkdir=True,
        )

        self.download_video_covers = conf.getboolean(
            'common', 'download_video_covers', fallback=True)

        # The feed section
        self.feed = SubConfig()
        self.feed.feed_url = conf.get('feed', 'feed_url', fallback=None)
        self.feed.local_path = self._resolve_path(
            conf.get('feed', 'local_path', fallback=None),
            is_dir=False, mkdir=True,
        )
        self.feed.download_media = conf.getboolean('feed', 'download_media', fallback=False)

    @staticmethod
    def _resolve_path(path, *, is_dir=False, mkdir=False):
        if path is None:
            return None

        path = pathlib.Path(path).expanduser()
        if not path.is_absolute():
            path = _root.joinpath(path)

        if mkdir:
            directory = path if is_dir else path.parent
            if not directory.is_dir():
                logger.info(f'makedirs: {directory}')
                directory.mkdir(parents=True)

        return path


def load_config(config_path):
    conf = configparser.ConfigParser()
    if not conf.read(config_path):
        raise RuntimeError(f'{config_path}: not found or failed to parse')
    return Config(conf)


def validate_config(config_path):
    conf = load_config(config_path)
    if not conf.images_dir:
        logger.warning('images_dir recommended')


def main():
    parser = cli.ArgumentParser(description='Validate or generate sample config file.')
    parser.add_argument('config_path', nargs='?',
                        help='''if specified, validate the config file;
                        otherwise, print a sample config file to stdout''')
    args = parser.parse_args()
    cli.adjust_verbosity(args)

    if args.config_path:
        def validate():
            validate_config(args.config_path)
            logger.info('valid config')

        cli.sandbox(validate)
    else:
        print(SAMPLE_CONFIG, end='')


if __name__ == '__main__':
    main()
