import subprocess
import os
import random
from main import get_file_path
import re
from flask import Flask, request, Response
from functools import wraps
import sys

process = None # 音楽再生プロセスを保持する変数

app = Flask(__name__)

def get_audio_device():
    # `aplay -l`の出力を取得
    result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
    output = result.stdout

    # スピーカーやヘッドホンに関連するデバイスを探す
    devices = []
    pattern = re.compile(r'card (\d+): .*, device (\d+):.*\[(.*)\]', re.IGNORECASE)
    
    for line in output.splitlines():
        match = pattern.search(line)
        if match:
            card, device, *name = match.groups()
            print("Connected Audio Devices: ", card, device, name)
            for n in name:
                if 'speaker' in n.lower() or 'headphone' in n.lower():
                    devices.append((int(card), int(device), name))
                    break
    
    # 最初に見つかったスピーカーやヘッドホンのデバイスを使用
    if devices:
        card, device, name = devices[0]
        print("Selected Audio Device: ", card, device, name)
        return f'hw:{card},{device}'
    
    # 見つからない場合はデフォルトのデバイスを使用
    return 'default'

def play_random_alarm(music_directory):
    # Get all mp3 files in the music directory
    mp3_files = [f for f in os.listdir(music_directory) if f.endswith('.mp3')]
    
    # Choose a random mp3 file
    if mp3_files:
        random_music_file = random.choice(mp3_files)
        music_path = os.path.join(music_directory, random_music_file)

        # Get the audio device
        device = get_audio_device()
        
        # Play the random mp3 file
        command = ["mpg123", "-a", device, os.path.join(music_directory, music_path)]
        global process
        procces = subprocess.Popen(command)
        return procces
    else:
        print("MP3 files not found in the music directory.")

def shutdown_server():
    """Flaskアプリケーションを終了させるための関数"""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def after_function_shutdown(func):
    """元の関数が実行された後にFlaskサーバーをシャットダウンするデコレータ"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)  # 元の関数を実行
        shutdown_server()  # 関数実行後にサーバーをシャットダウン
        sys.exit(0)  # サーバーがシャットダウンした後にプロセスを終了
        return result
    return wrapper

@app.route('/stop', methods=['GET'])
@after_function_shutdown
def stop():
    global process
    if process and process.poll() is None:  # プロセスが実行中かチェック
        process.terminate()  # プロセスを停止
        process.wait()  # プロセスが完全に終了するのを待つ
        process = None # プロセスをリセット
        
        return "Music stopped and server shutting down."
    return "No music is playing."

if __name__ == "__main__":
    music_directory = get_file_path("music")
    process = play_random_alarm(music_directory)
    app.run(host='0.0.0.0', port=5000)

