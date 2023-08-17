"""
这个程序是一个 Spotify 歌单管理工具，使用 Spotify 的 API 来读取和修改用户的歌单。

该程序接受以下命令行参数：

- playlist-a：歌单A的名称。程序会读取这个歌单的所有歌曲。
- playlist-b：歌单B的名称。程序会将符合筛选条件的歌曲添加到这个歌单。
- playlist-c：歌单C的名称。程序会将不符合筛选条件的歌曲添加到这个歌单。
- filter：筛选条件。可以是 "contains_chinese" 或 "not_contains_chinese"。前者会筛选出名称中包含中文的歌曲，后者会筛选出名称中不包含中文的歌曲。

这些参数也可以通过一个名为 "spotify_playlist_manager_config.yaml" 的配置文件提供。配置文件应该放在程序所在路径的 "config" 目录下。

配置文件的结构如下：

```yaml
playlist_a: "Playlist A Name"
playlist_b: "Playlist B Name"
playlist_c: "Playlist C Name"
filter: "contains_chinese"
client_id: "Your Spotify App Client ID"
client_secret: "Your Spotify App Client Secret"
redirect_uri: "Your Spotify App Redirect URI"

"""

import os
import argparse
import yaml
import time
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import collections

# 定义命令行参数
parser = argparse.ArgumentParser(description='Manage Spotify playlists.')
parser.add_argument('--playlist-a', help='Name of Playlist A')
parser.add_argument('--filter', help='Filter condition for language')
args = parser.parse_args()

# 读取配置文件
print("Reading configuration file...")
config_path = os.path.join(os.path.dirname(__file__), 'config', 'spotify_playlist_manager_config.yaml')
with open(config_path, 'r', encoding="utf8") as f:
    config = yaml.safe_load(f)

print("Setting up configurations...")
if args.playlist_a:
    config['playlist_a'] = args.playlist_a
if args.filter:
    config['filter'] = args.filter

print("Connecting to Spotify...")
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config['client_id'],
                                               client_secret=config['client_secret'],
                                               redirect_uri=config['redirect_uri'],
                                               scope='playlist-modify-public'))

def classify_language(song):
    if song and song.get('track') and song['track'].get('name'):
        if re.search('[\u4e00-\u9fff]', song['track']['name']):
            return '中文'
        else:
            return '非中文'
    return '非中文'  # 默认情况下，如果上面的条件都不满足，则返回“非中文”

def classify_emotion(track_features):
    emotions = []

    energy = track_features['energy']
    danceability = track_features['danceability']
    mode = track_features['mode']

    # 快乐
    if energy > 0.7 and danceability > 0.7:
        emotions.append('快乐')

    # 悲伤
    if energy < 0.4 and danceability < 0.4:
        emotions.append('悲伤')

    # 宁静/放松
    if energy < 0.3 and danceability < 0.3:
        emotions.append('宁静/放松')

    # 愤怒/激烈
    if energy > 0.8 and danceability > 0.6:
        emotions.append('愤怒/激烈')

    # 浪漫/甜蜜
    if 0.4 <= energy <= 0.7 and 0.4 <= danceability <= 0.7 and mode == 1:
        emotions.append('浪漫/甜蜜')

    # 中性
    if not emotions:
        emotions.append('中性')

    return emotions

# 获取歌单 A 的所有歌曲
def get_all_songs(playlist_id):
    all_songs = []
    response = sp.playlist_tracks(playlist_id)
    total_tracks = response.get('total', 0)
    print(f"Getting information for {total_tracks} songs from the playlist...")

    while response:
        items = response.get('items', [])
        all_songs.extend(items)
        print(f"Fetching information for songs {len(all_songs)+1}-{len(all_songs)+len(items)}...")
        response = sp.next(response)

    return all_songs, [item['track']['id'] for item in all_songs]

print("Fetching songs from playlist {}...".format(config['playlist_a']))
songs, song_ids = get_all_songs(config['playlist_a'])
existing_song_ids = {config['playlist_a']: set(song_ids)}

for key in config['languages'].values():
    _, song_ids = get_all_songs(key)
    existing_song_ids[key] = set(song_ids)

for key in config['emotions'].values():
    _, song_ids = get_all_songs(key)
    existing_song_ids[key] = set(song_ids)

print(f"Found {len(songs)} songs in the source playlist.")

print("Classifying songs based on language and emotion...")
for i, song_item in enumerate(songs):
    track = song_item['track']

    # 显示歌曲信息
    print(f"{i+1}/{len(songs)} Song: {track['name']}")

    # 进行语言分类
    print("    Classifying song based on language...")
    language = classify_language(song_item)
    print(f"    Song is classified as {language}.")
    language_playlist_id = config['languages'].get(language)
    if track['uri'] and language_playlist_id and track['id'] not in existing_song_ids[language_playlist_id]:
        try:
            sp.playlist_add_items(language_playlist_id, [track['uri']])
            print(f"    Added song to {language} Playlist: {track['name']}")
        except spotipy.SpotifyException as e:
            if 'Unsupported URL / URI.' in str(e):
                print(f"Cannot add song {track['name']} due to unsupported URI. The song might have been removed from Spotify.")
            elif 'Retry-After' in e.headers:
                print(f"Rate limit exceeded, waiting for {e.headers['Retry-After']} seconds")
                time.sleep(int(e.headers['Retry-After']) + 2)
            else:
                print(f"Error adding song to {language} Playlist: {e}")

    # 进行情绪分类
    print("    Classifying song based on emotion...")
    if track['id']:
        track_features = sp.audio_features([track['id']])[0]
        emotions = classify_emotion(track_features)
        print(f"    Song is classified with emotions: {emotions}.")
        for emotion in emotions:
            emotion_playlist_id = config['emotions'].get(emotion)
            if track['uri'] and emotion_playlist_id and track['id'] not in existing_song_ids[emotion_playlist_id]:
                try:
                    sp.playlist_add_items(emotion_playlist_id, [track['uri']])
                    print(f"    Added song to {emotion} Playlist: {track['name']}")
                except spotipy.SpotifyException as e:
                    if 'Unsupported URL / URI.' in str(e):
                        print(f"Cannot add song {track['name']} due to unsupported URI. The song might have been removed from Spotify.")
                    elif 'Retry-After' in e.headers:
                        print(f"Rate limit exceeded, waiting for {e.headers['Retry-After']} seconds")
                        time.sleep(int(e.headers['Retry-After']) + 2)
                    else:
                        print(f"Error adding song to {emotion} Playlist: {e}")
    else:
        print(f"    Skipping emotion classification for song {i+1}/{len(songs)} due to missing track ID.")

def remove_duplicates_from_playlist(playlist_id, existing_song_ids):
    song_ids_in_playlist = existing_song_ids[playlist_id]
    duplicate_ids = [item for item, count in collections.Counter(song_ids_in_playlist).items() if count > 1]

    if duplicate_ids:
        print(f"Found {len(duplicate_ids)} duplicate songs in playlist ID {playlist_id}. Removing them...")

    for track_id in duplicate_ids:
        sp.playlist_remove_all_occurrences_of_items(playlist_id, [track_id])
        print(f"Removed all occurrences of song with track ID {track_id} from playlist ID {playlist_id}.")

    if duplicate_ids:
        print(f"Finished removing duplicates from playlist ID {playlist_id}.")

# 用于每个歌单
remove_duplicates_from_playlist(config['playlist_a'], existing_song_ids)
for playlist_id in config['languages'].values():
    remove_duplicates_from_playlist(playlist_id, existing_song_ids)

print("All songs have been classified and added to the respective playlists.")
print("\nTask Completed!")

