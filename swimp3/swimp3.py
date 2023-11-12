import spotipy
import random
from spotipy.oauth2 import SpotifyOAuth
import subprocess
import os
import random
from logging import Logger
from argparse import ArgumentParser


logger = Logger('swimp3')

parser = ArgumentParser(
    prog='Swimp3', 
    description='Generate a new random playlist and/or download (this) playlist as mp3s for my underwater swimming headphones'
)

parser.add_argument('--playlist-id', type=str, help='The playlist id to either download or seed to a new random playlist', required=True)
parser.add_argument('--seed', action='store_true', help='If this argument is present, swimp3 will generate a new random playlist, where the value of "playlist-id" is the id of the seed playlist. If it is not present, swimp3 will download the playlist given in "playlist-id" directly', required=False)
parser.add_argument('--path', type=str, default="/Users/noah.florin/Downloads", help="The base path to download the playlist mp3 files to. The actual path is a subdirectory at this path with the same name as the playlist")
parser.add_argument('--length', type=int, help='The number of tracks in the new randomly generate playlist. Only used if "--seed" is also provided', default=100)

def getSpotipyClient(scope):
    return spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

def new_random_playlist(playlist_id, new_playlist_name, new_playlist_length = 100):
    """
    Select ${new_playlist_length} songs at random from ${playlist_id}
    Create a new playlist with those songs under the name ${new_playlist_name}
    Returns the new playlist id
    """
    sp = getSpotipyClient('playlist-modify-public playlist-modify-private')
    playlist = sp.playlist_tracks(playlist_id)
    playlist_items = playlist.get('items')
    new_playlist_items = []

    while playlist['next']:
        playlist = sp.next(playlist)
        playlist_items.extend(playlist['items'])

    for item in playlist_items:
        if (item.get('is_local') is not True):
            track = item.get('track')
            track_uri = track.get('uri')
            new_playlist_items.append(track_uri)
    
    max_playlist_length = min(len(new_playlist_items), new_playlist_length)
    new_playlist_items = random.sample(new_playlist_items, max_playlist_length)
    user_id = sp.me()['id']
    new_playlist_result = sp.user_playlist_create(user_id, new_playlist_name)
    new_playlist_id = new_playlist_result['id']
    sp.playlist_add_items(new_playlist_id, new_playlist_items)
    logger.info(f"Created new playlist (id='{new_playlist_id}', name='{new_playlist_name}')")
    return new_playlist_id

def download_playlist(playlist_id):
    logger.info(f"Downloading playlist (id='{playlist_id}')")
    res = subprocess.check_output(['spotdl', f"https://open.spotify.com/playlist/{playlist_id}"])
    logger.info(res)

def move_mp3_files_to_path(new_path):
    """
    Moves all mp3 files in the current directory to the given path
    """
    logger.info(f"Moving mp3 files to {new_path}")
    os.mkdir(new_path)
    files = os.listdir()
    mp3_files = [file for file in files if file.endswith('.mp3')]
    for mp3_file in mp3_files:
        old_mp3_path = os.path.abspath(mp3_file)
        new_mp3_path = os.path.join(new_path, mp3_file)
        os.rename(old_mp3_path, new_mp3_path)

def swimp3():
    cli_args = vars(parser.parse_args())
    should_generate_new_playlist = cli_args.get('seed')
    playlist_id = cli_args.get('playlist_id')
    path = cli_args.get('path')
    if should_generate_new_playlist:
        new_playlist_length = cli_args.get('length')
        new_playlist_name = f"swimp3.{random.randint(1, 100000)}"
        playlist_id = new_random_playlist(playlist_id, new_playlist_name, new_playlist_length)

    download_playlist(playlist_id)
    download_path = os.path.join(path, new_playlist_name)
    move_mp3_files_to_path(download_path)