# Wake Calendar

## Build

```bash
docker build -t wake-calendar .
```

## Run

```bash
docker run -d -v /path/to/host/directory:/app/data wake-calendar:latest
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
ExecStart=/usr/bin/docker run --rm -v {/path/to/host/directory}:/app/data my-alarm-app
ExecStop=/usr/bin/docker stop %n

[Install]
WantedBy=multi-user.target
```

### Note

```bash
sudo systemctl daemon-reload
sudo systemctl enable wake-calendar.service

sudo systemctl start wake-calendar.service

sudo systemctl status wake-calendar.service
```
