import pygame
import time

pygame.mixer.init()

def play_audio(path, wait=False, volume=0.8):
    sound = pygame.mixer.Sound(path)
    sound.set_volume(volume)
    channel = sound.play()

    if wait:
        while channel.get_busy():
            time.sleep(0.05)