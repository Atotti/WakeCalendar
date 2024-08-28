import subprocess
import os
import random
from main import get_file_path

def play_random_alarm(music_directory):
    # Get all mp3 files in the music directory
    mp3_files = [f for f in os.listdir(music_directory) if f.endswith('.mp3')]
    
    # Choose a random mp3 file
    if mp3_files:
        random_music_file = random.choice(mp3_files)
        music_path = os.path.join(music_directory, random_music_file)
        
        # Play the random mp3 file
        command = f"mpg123 -a hw:0,0 {os.path.join(music_directory, music_path)}"
        os.system(command)
    else:
        print("MP3 files not found in the music directory.")

if __name__ == "__main__":
    music_directory = get_file_path("music")
    play_random_alarm(music_directory)
