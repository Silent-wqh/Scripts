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
```

其中：

- playlist_a：歌单A的名称。
- playlist_b：歌单B的名称。
- playlist_c：歌单C的名称。
- filter：筛选条件。可以是 "contains_chinese" 或 "not_contains_chinese"。
- client_id：你的 Spotify App 的 Client ID。
- client_secret：你的 Spotify App 的 Client Secret。
- redirect_uri：你的 Spotify App 的 Redirect URI。

命令行参数会覆盖配置文件中的相应设置。
"""

import os
import argparse
import yaml
import time
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# 定义命令行参数
parser = argparse.ArgumentParser(description='Manage Spotify playlists.')
parser.add_argument('--playlist-a', help='Name of Playlist A')
parser.add_argument('--filter', help='Filter condition for language')
args = parser.parse_args()

# 读取配置文件
config_path = os.path.join(os.path.dirname(__file__), 'config', 'spotify_playlist_manager_config.yaml')
with open(config_path, 'r', encoding="utf8") as f:
    config = yaml.safe_load(f)

# 覆盖配置文件中的信息
if args.playlist_a:
    config['playlist_a'] = args.playlist_a
if args.filter:
    config['filter'] = args.filter

# 连接到 Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config['client_id'],
                                               client_secret=config['client_secret'],
                                               redirect_uri=config['redirect_uri'],
                                               scope='playlist-modify-public'))

def classify_language(song):
    if song and song.get('track') and song['track'].get('name'):
        if config['filter'] == "contains_chinese" and re.search('[\u4e00-\u9fff]', song['track']['name']):
            return '中文'
        elif config['filter'] == "not_contains_chinese" and not re.search('[\u4e00-\u9fff]', song['track']['name']):
            return '非中文'
    return None

def classify_emotion(track_features):
    energy = track_features['energy']
    danceability = track_features['danceability']
    mode = track_features['mode']

    if energy > 0.7 and danceability > 0.7 and mode == 1:
        return '快乐'
    elif energy < 0.4 and danceability < 0.4 and mode == 0:
        return '悲伤'
    elif energy < 0.3 and danceability < 0.3:
        return '宁静/放松'
    elif energy > 0.7 and danceability > 0.5:
        return '愤怒/激烈'
    elif 0.4 < energy < 0.7 and 0.4 < danceability < 0.7 and mode == 1:
        return '浪漫/甜蜜'
    else:
        return None

# 获取歌单 A 的所有歌曲
def get_all_songs(playlist_id):
    all_songs = []
    response = sp.playlist_tracks(playlist_id)
    while response:
        all_songs.extend(response.get('items', []))
        response = sp.next(response)
    return all_songs

songs = get_all_songs(config['playlist_a'])

for i, song_item in enumerate(songs):
    track = song_item['track']

    # 检查歌曲URI的有效性
    if not track['uri'].startswith('spotify:track:'):
        print(f"Invalid URI for song {track['name']}. Skipping...")
        continue

    # 进行语言分类
    language = classify_language(song_item)
    language_playlist_id = config['languages'].get(language)
    if language_playlist_id:
        try:
            sp.playlist_add_items(language_playlist_id, [track['uri']])
            print(f"Added song {i+1}/{len(songs)} to {language} Playlist: {track['name']}")
        except spotipy.SpotifyException as e:
            # 更好地处理频率限制异常
            if 'Rate limit exceeded' in str(e):
                print(f"Rate limit exceeded, waiting for {e.headers.get('Retry-After', 2)} seconds")
                time.sleep(int(e.headers.get('Retry-After', 2)) + 2)
            else:
                print(f"Error adding song {track['name']} to {language} Playlist: {e}")

    # ... 同样的处理情绪分类

    # 进行情绪分类
    track_features = sp.audio_features([track['id']])[0]
    emotion = classify_emotion(track_features)
    emotion_playlist_id = config['emotions'].get(emotion)
    if emotion_playlist_id:
        try:
            sp.playlist_add_items(emotion_playlist_id, [track['uri']])
            print(f"Added song {i+1}/{len(songs)} to {emotion} Playlist: {track['name']}")
        except spotipy.SpotifyException as e:
            print(f"Rate limit exceeded, waiting for {e.headers['Retry-After']} seconds")
            time.sleep(int(e.headers['Retry-After']) + 2)
