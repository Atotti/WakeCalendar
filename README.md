# Wake Calendar

Googleカレンダーから目覚ましをセットするアプリケーションです。
目覚ましをかけ忘れて遅刻したので、作りました。

This is a application that set alarms for you based on google calendar events.

You can set your alarm on google calendar like this:
![image](https://github.com/user-attachments/assets/772b5046-bf28-44ec-adae-a3fb6eb900d4)

## How to use

If you use this application, you need to get google service account key file at Google Cloud Console.
Don't forget to enable the Google Calendar API to service account. And you need to share your calendar with the service account in google calendar setting.

Please place it in the application directory as `credentials.json`.
And you need to set `.env` file. This file should contain the following:

```env
CALENDAR_ID=your_calendar_id
```

Usually, the calendar id is your gmail address. You can find it in the google calendar settings.

```tree
WakeCalendar
|   .dockerignore
|   .env
|   .gitignore
|   alarm.py
|   alarm_schedule.json
|   credentials.json
|   Dockerfile
|   main.py
|   README.md
|   requirements.txt
|   setup.py
|   
+---.github
|       dependabot.yml
|       
\---music
        sample.mp3
```

In this application you can set your own alarm sound file (mp3). You can place it in the music directory.
If you don't have any sound file, you can use the default sound file.

### Requirements

- This application is intended to run on a Raspberry Pi with a speaker connected to it.
- Docker

### Build

```bash
docker build -t wake-calendar .
```

### Run

```bash
docker run -d --rm -p 5000:5000 --device /dev/snd:/dev/snd -v /path/to/host/directory:/app/data wake-calendar:latest
```

### Auto Restart

I recommend using systemd to auto restart the container in case of a crash. Here is an example service file:

```service
[Unit]
Description=Wake Calendar Docker Container
After=docker.service
Requires=docker.service

[Service]
Restart=always
ExecStart=/usr/bin/docker run --rm  -p 5000:5000 --device /dev/snd:/dev/snd -v {/path/to/host/directory}:/app/data wake-calendar:latest
ExecStop=/usr/bin/docker stop wake-calendar

[Install]
WantedBy=multi-user.target
```

Replace `{/path/to/host/directory}` with the path to the directory you want to use for the data volume.
I recommend you to write your repository directory.

### Note

```bash
sudo systemctl daemon-reload
sudo systemctl enable wake-calendar.service

sudo systemctl start wake-calendar.service

sudo systemctl status wake-calendar.service
```
