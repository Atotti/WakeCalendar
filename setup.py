import os
from crontab import CronTab


def set_cron_job():
    """Set a cron job to run the alarm script at the specified time."""
    current_file_path = os.path.abspath(__file__)
    script_path = os.path.join(os.path.dirname(current_file_path), "main.py")
    cron = CronTab(user=True)  # Create a new cron job
    job = cron.new(command=f"/usr/bin/python3 {script_path}")

    # 5分ごとに実行
    job.minute.every(5)

    cron.write()  # crontabにジョブを保存

if __name__ == "__main__":
    set_cron_job()