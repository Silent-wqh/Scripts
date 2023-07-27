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
parser.add_argument('--playlist-b', help='Name of Playlist B')
parser.add_argument('--playlist-c', help='Name of Playlist C')
parser.add_argument('--filter', help='Filter condition')
args = parser.parse_args()

# 读取配置文件
config_path = os.path.join(os.path.dirname(__file__), 'config', 'spotify_playlist_manager_config.yaml')
with open(config_path, 'r', encoding="utf8") as f:
    config = yaml.safe_load(f)

# 覆盖配置文件中的信息
if args.playlist_a:
    config['playlist_a'] = args.playlist_a
if args.playlist_b:
    config['playlist_b'] = args.playlist_b
if args.playlist_c:
    config['playlist_c'] = args.playlist_c
if args.filter:
    config['filter'] = args.filter

# 连接到 Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config['client_id'],
                                               client_secret=config['client_secret'],
                                               redirect_uri=config['redirect_uri'],
                                               scope='playlist-modify-public'))

# 获取歌单 A 的所有歌曲
def get_all_songs(playlist_id):
    all_songs = []
    response = sp.playlist_tracks(playlist_id)
    if response:
        all_songs.extend(response.get('items', []))
        while response and response.get('next'):
            response = sp.next(response)
            if response:
                all_songs.extend(response.get('items', []))

    return all_songs

playlist_a_songs = get_all_songs(config['playlist_a'])

# 筛选出符合规则的歌曲
def filter_songs(songs, filter_condition):
    filtered_songs = []
    unfiltered_songs = []
    for song in songs:
        if song and song.get('track') and song['track'].get('name'):
            if filter_condition == "contains_chinese":
                if re.search('[\u4e00-\u9fff]', song['track']['name']):
                    filtered_songs.append(song['track'])
                else:
                    unfiltered_songs.append(song['track'])
            elif filter_condition == "not_contains_chinese":
                if not re.search('[\u4e00-\u9fff]', song['track']['name']):
                    filtered_songs.append(song['track'])
                else:
                    unfiltered_songs.append(song['track'])
    return filtered_songs, unfiltered_songs

filtered_songs, unfiltered_songs = filter_songs(playlist_a_songs, config['filter'])

# 获取歌单 B 和歌单 C 的所有歌曲
playlist_b_songs = get_all_songs(config['playlist_b'])
playlist_c_songs = get_all_songs(config['playlist_c'])

# 将歌曲添加到歌单 B 和歌单 C，跳过已存在的歌曲
for i, song in enumerate(filtered_songs):
    if not any(b_song['track']['id'] == song['id'] for b_song in playlist_b_songs):
        try:
            sp.playlist_add_items(config['playlist_b'], [song['uri']])
            print(f"Added song {i+1}/{len(filtered_songs)} to Playlist B: {song['name']}")
        except spotipy.SpotifyException as e:
            print(f"Rate limit exceeded, waiting for {e.headers['Retry-After']} seconds")
            time.sleep(int(e.headers['Retry-After']) + 2)

for i, song in enumerate(unfiltered_songs):
    if not any(c_song['track']['id'] == song['id'] for c_song in playlist_c_songs):
        try:
            sp.playlist_add_items(config['playlist_c'], [song['uri']])
            print(f"Added song {i+1}/{len(unfiltered_songs)} to Playlist C: {song['name']}")
        except spotipy.SpotifyException as e:
            print(f"Rate limit exceeded, waiting for {e.headers['Retry-After']} seconds")
            time.sleep(int(e.headers['Retry-After']) + 2)
