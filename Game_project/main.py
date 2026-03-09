# main.py
import pygame
from source_code.engine import Engine

if __name__ == "__main__":
    game = Engine()
    game.run()
    pygame.quit()