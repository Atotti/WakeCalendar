import os
from crontab import CronTab
from main import get_file_path, main
from flask import Flask
from alarm import play_sound

app = Flask(__name__)
process = None # 音楽再生プロセスを保持する変数

@app.route('/stop', methods=['GET'])
def stop():
    global process
    if process and process.poll() is None:  # プロセスが実行中かチェック
        process.terminate()  # プロセスを停止
        process.wait()  # プロセスが完全に終了するのを待つ
        process = None # プロセスをリセット
        return "Music stopped and server shutting down."
    return "No music is playing."

@app.route('/play', methods=['GET'])
def play():
    global process
    if process and process.poll() is None:
        return "Music is already playing."
    else:
        process = play_sound()
        return "Music started."

def set_cron_job():
    """Set a cron job to run the alarm script at the specified time.
    The job runs the main script every 5 minutes.
    This function is setup to run main.py every 5 minutes.
    """
    script_path = get_file_path('main.py')
    cron = CronTab(user=True)  # Create a new cron job
    job = cron.new(command=f"/usr/local/bin/python3 {script_path} >> /proc/1/fd/1 2>> /proc/1/fd/2")

    # 5分ごとに実行
    job.minute.every(5)

    cron.write()  # crontabにジョブを保存

if __name__ == "__main__":
    set_cron_job()
    print("Cron job set successfully.")
    main()
    app.run(host='0.0.0.0', port=5000)  # Flaskサーバーを起動
