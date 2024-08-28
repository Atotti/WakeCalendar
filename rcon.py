from flask import Flask, request
from alarm import process

app = Flask(__name__)

@app.route('/stop', methods=['GET'])
def stop():
    global process
    if process and process.poll() is None:  # プロセスが実行中かチェック
        process.terminate()  # プロセスを停止
        process.wait()  # プロセスが完全に終了するのを待つ
        return "Music stopped."
    return "No music is playing."
