import os
from crontab import CronTab
from main import get_file_path, main


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
