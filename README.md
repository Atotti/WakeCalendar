# Wake Calendar

This is a application that set alarms for you based on google calendar events.
If you use this application, you need to get google service account key file. And place it in the application directory as `credentials.json`.

In this application you can set your own alarm sound file (mp3). You can place it in the music directory.
If you don't have any sound file, you can use the default sound file.

And you can set your alarm on google calendar like this:

## Requirements

- This application is intended to run on a Raspberry Pi with a speaker connected to it.
- Docker

## Build

```bash
docker build -t wake-calendar .
```

## Run

```bash
docker run -d --rm --device /dev/snd:/dev/snd -v /path/to/host/directory:/app/data wake-calendar:latest
```

## Auto Restart

I recommend using systemd to auto restart the container in case of a crash. Here is an example service file:

```service
[Unit]
Description=Wake Calendar Docker Container
After=docker.service
Requires=docker.service

[Service]
Restart=always
ExecStart=/usr/bin/docker run --rm --device /dev/snd:/dev/snd -v {/path/to/host/directory}:/app/data wake-calendar:latest
ExecStop=/usr/bin/docker stop %n

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
