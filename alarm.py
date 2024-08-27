import subprocess


def play_alarm():
    music_file = "/path/to/your_music.mp3"
    subprocess.run(["mpg123", music_file])


if __name__ == "__main__":
    play_alarm()
