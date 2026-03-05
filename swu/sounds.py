import pygame
import os


class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        
        self.sounds = {}
        self.sounds_loaded = False
        self.load_sounds()
    
    def load_sounds(self):
        """Загрузка звуков из папки sounds"""
        sounds_dir = "sounds"
        
        # Проверяем, существует ли папка
        if not os.path.exists(sounds_dir):
            os.makedirs(sounds_dir)
            print(f"Создана папка {sounds_dir}. Добавьте туда звуковые файлы.")
            return
        
        # Словарь звуков и их названий файлов
        sound_files = {
            'shoot': 'shoot.wav',
            'explosion': 'explosion.wav',
            'powerup': 'powerup.wav',
            'player_hit': 'player_hit.wav',
            'game_over': 'game_over.wav'
        }
        
        # Загрузка звуков
        for name, filename in sound_files.items():
            filepath = os.path.join(sounds_dir, filename)
            if os.path.exists(filepath):
                try:
                    self.sounds[name] = pygame.mixer.Sound(filepath)
                except:
                    print(f"Не удалось загрузить звук: {filename}")
            else:
                print(f"Звуковой файл не найден: {filename}")
        
        if self.sounds:
            self.sounds_loaded = True
            print(f"Загружено звуков: {len(self.sounds)}")
    
    def play(self, name):
        """Воспроизвести звук по имени"""
        if self.sounds_loaded and name in self.sounds:
            self.sounds[name].play()


# Глобальный менеджер звуков
sound_manager = SoundManager()
