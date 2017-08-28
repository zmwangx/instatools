# TODO: resolve URLs of multiple videos in parallel.

import requests

from .log import logger


_session = requests.Session()


# TODO: exponential backoff
def _get_url(base_url, *, params=None):
    req = requests.Request('GET', base_url, params=params).prepare()
    logger.info(f'GET {req.url}')
    resp = _session.send(req, timeout=10)
    assert resp.status_code == 200, f'GET {req.url}: HTTP {resp.status_code} - {resp.text}'
    return resp


# Returns a list of dicts conforming to the db.Media schema, along with
# the raw JSON object as returned by the API.
#
# The timeline API here returns the last few (12 at the time of writing)
# media entries. It does not contain URLs of videos. If
# `resolve_video_urls` is True (default), `media` is called to resolve
# the URL of each video, resulting in N+1 API calls where N is the
# number of videos.
def timeline(username, *, resolve_video_urls=True):
    resp = _get_url(f'https://www.instagram.com/{username}/', params={'__a': '1'})
    respobj = resp.json()
    assert respobj['user']['username'] == username
    user_id = respobj['user']['id']

    return [media(mediaobj['code'])[0] if mediaobj['is_video'] and resolve_video_urls else {
        'username': username,
        'user_id': user_id,
        'id': mediaobj['id'],
        'code': mediaobj['code'],
        'is_video': mediaobj['is_video'],
        'image_url': mediaobj['display_src'],
        'video_url': None,
        'height': mediaobj['dimensions']['height'],
        'width': mediaobj['dimensions']['width'],
        'timestamp': mediaobj['date'],
        'caption': mediaobj['caption'],
    } for mediaobj in respobj['user']['media']['nodes']], respobj


# Returns a dict conforming to the db.Media schema, along with the raw
# JSON object as returned by the API.
def media(code):
    resp = _get_url(f'https://www.instagram.com/p/{code}/', params={'__a': '1'})
    respobj = resp.json()
    mediaobj = respobj['graphql']['shortcode_media']
    assert mediaobj['shortcode'] == code

    return {
        'username': mediaobj['owner']['username'],
        'user_id': mediaobj['owner']['id'],
        'id': mediaobj['id'],
        'code': code,
        'is_video': mediaobj['is_video'],
        'image_url': mediaobj['display_url'],
        'video_url': mediaobj.get('video_url'),
        'height': mediaobj['dimensions']['height'],
        'width': mediaobj['dimensions']['width'],
        'timestamp': mediaobj['taken_at_timestamp'],
        'caption': mediaobj['edge_media_to_caption']['edges'][0]['node']['text'],
    }, respobj
