# source_code/characters/player.py
import pygame
from source_code.settings import RED, GAME_HEIGHT, PLAYER_SPEED, JUMP_STRENGTH, GRAVITY
from source_code.systems.inventory import Inventory


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((32, 32))  # Red cube
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(100, GAME_HEIGHT - 100))
        self.vel_y = 0
        self.on_ground = False
        self.inventory = Inventory()

        self.hp = 100
        self.max_hp = 100
        self.stamina = 100
        self.max_stamina = 100
        self.sanity = 100

    def update(self, platforms):
        # 1. Movement input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED

        # 3. Apply Gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # 4. Check for floor collisions
        self.check_collisions(platforms)

    def check_collisions(self, platforms):
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0:  # If falling down
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.on_ground = True

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                # 1. Cycle with Q
                if event.key == pygame.K_q:
                    self.inventory.next_slot()

                # 2. Direct select with 1-5 keys
                if event.key == pygame.K_1: self.inventory.select_slot(0)
                if event.key == pygame.K_2: self.inventory.select_slot(1)
                if event.key == pygame.K_3: self.inventory.select_slot(2)
                if event.key == pygame.K_4: self.inventory.select_slot(3)
                if event.key == pygame.K_5: self.inventory.select_slot(4)