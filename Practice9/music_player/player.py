import pygame
import os

class MusicPlayer:
    def __init__(self, music_dir):
        self.music_dir = music_dir
        self.playlist = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.wav'))]
        self.current_idx = 0
        self.is_playing = False
        self.volume = 0.5
        pygame.mixer.music.set_volume(self.volume)

    def play(self):
        if not self.playlist: return

        path = os.path.join(self.music_dir, self.playlist[self.current_idx])
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        self.is_playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False

    def next_track(self):
        self.current_idx = (self.current_idx + 1) % len(self.playlist)
        self.play()

    def prev_track(self):
        self.current_idx = (self.current_idx - 1) % len(self.playlist)

    def get_current_track_name(self):
        if not self.playlist: return "No music found"
        track = self.playlist[self.current_idx].split(".")
        return track[0]
    
    def get_pos_seconds(self):
        return pygame.mixer.music.get_pos() // 1000
    
    def set_volume(self, delta):
        self.volume = max(0.0, min(1.0, self.volume + delta))
        pygame.mixer.music.set_volume(self.volume)