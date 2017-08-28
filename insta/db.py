import peewee


_database_proxy = peewee.Proxy()


class Media(peewee.Model):
    # Instagram handle
    username = peewee.TextField()
    # Numeric user ID
    user_id = peewee.TextField()
    # Numeric media ID
    id = peewee.TextField(unique=True)
    # Short identifier with 10 word characters, sometimes called shortcode
    code = peewee.TextField(unique=True)
    # Whether the media is a video
    is_video = peewee.BooleanField()
    # URL of the image, or the cover image of a video
    image_url = peewee.TextField()
    # URL of the video, or None for an image
    video_url = peewee.TextField(nullable=True)
    # Pixel dimensions of the media
    height = peewee.IntegerField()
    width = peewee.IntegerField()
    # Epoch time of the media (this timestamp is called
    # "taken_at_timestamp" in one API, but I believe this is the time of
    # upload/posting; to my point, in the public API it is called
    # 'created_time'. Also, from my observations, Instagram strips media
    # EXIF data, at least by default.)
    timestamp = peewee.IntegerField()
    # Media caption
    caption = peewee.TextField()

    class Meta:
        database = _database_proxy


def init_database(database_path):
    database = peewee.SqliteDatabase(database_path)
    _database_proxy.initialize(database)
    database.create_tables((Media), safe=True)
