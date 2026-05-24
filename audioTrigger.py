# Audio playback module
# Handles playing audio files with optional wait-until-complete functionality

import pygame
import time

pygame.mixer.init()

def play_audio(path, wait=False, volume=0.8):
    """Play an audio file from the given path.
    
    Args:
        path: File path to the audio file
        wait: If True, block until the audio finishes playing
        volume: Volume level from 0.0 to 1.0 (default 0.8)
    """
    sound = pygame.mixer.Sound(path)
    sound.set_volume(volume)
    channel = sound.play()

    if wait:
        while channel.get_busy():
            time.sleep(0.05)