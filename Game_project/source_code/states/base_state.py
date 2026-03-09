import pygame

class BaseState:
    def __init__(self, engine):
        self.engine = engine
        self.next_state = None  # Set this to a string to trigger a switch
        self.quit = False

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass