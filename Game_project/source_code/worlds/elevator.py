# source_code/worlds/elevator.py

import pygame


class Elevator(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        x = -8
        y = 182
        self.base_size = (200, 240)
        self.scale_factor = 0.5
        self.size = (int(self.base_size[0] * self.scale_factor),
                     int(self.base_size[1] * self.scale_factor))

        # 1. Load 5 frames for the BACK (Behind player)
        self.back_frames = [
            pygame.transform.scale(
                pygame.image.load(f"Game_project/assets/sprites/elevator_anim/elevator_back{i}.png").convert_alpha(),
                self.size
            ) for i in range(1, 6)
        ]

        # 2. Load 5 frames for the FRONT (In front of player)
        self.front_frames = [
            pygame.transform.scale(
                pygame.image.load(f"Game_project/assets/sprites/elevator_anim/elevator_front{i}.png").convert_alpha(),
                self.size
            ) for i in range(1, 6)
        ]

        self.state = "CLOSED"
        self.current_frame = 0

        # 'self.image' usually refers to the front layer for Sprite group drawing
        self.image = self.front_frames[0]
        # This will hold the current back frame
        self.back_image = self.back_frames[0]

        self.rect = self.image.get_rect(topleft=(x, y))
        self.last_update = pygame.time.get_ticks()
        self.frame_delay = 120
        self.interact_rect = pygame.Rect(self.rect.x + 15, self.rect.y + 40, 15, 50)

        self.rect = self.image.get_rect(topleft=(x, y))

    def open_doors(self):
        if self.state == "CLOSED": self.state = "OPENING"

    def close_doors(self):
        if self.state == "OPEN": self.state = "CLOSING"

    def update(self):
        now = pygame.time.get_ticks()

        # Only run animation logic if we are actually moving the doors
        if self.state in ["OPENING", "CLOSING"]:
            if now - self.last_update > self.frame_delay:
                self.last_update = now

                if self.state == "OPENING":
                    if self.current_frame < 4:
                        self.current_frame += 1
                    else:
                        self.state = "OPEN"

                elif self.state == "CLOSING":
                    if self.current_frame > 0:
                        self.current_frame -= 1
                    else:
                        self.state = "CLOSED"

                # Update images immediately when frame changes
                self.image = self.front_frames[self.current_frame]
                self.back_image = self.back_frames[self.current_frame]

        # Always keep the interaction box synced
        self.interact_rect.topleft = (self.rect.x + 34, self.rect.y + 40)

    def draw_debug(self, surface):
        # Draw the interaction zone in Blue
        pygame.draw.rect(surface, (0, 0, 255), self.interact_rect, 1)