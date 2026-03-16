# source_code/worlds/level_manager.py
import pygame
import random
from source_code.settings import GAME_WIDTH, GAME_HEIGHT, BAR_HEIGHT, GREEN, BLACK
from source_code.characters.enemies import Enemy, SlimeEnemy, Boss

MAP_DATA = {
    "forest": {
        "bg_path": "Game_project/assets/background/forest_back.png",
        "fg_path": "Game_project/assets/background/forest_fore.png",
        "interactable": "camp",
        "floor_color": None,
        "edge_color": (19, 79, 19),
    },
    "BW": {
        "bg_path": "Game_project/assets/background/BW.png",
        "fg_path": None,
        "interactable": "BW_NPC",
        "floor_color": None,
        "edge_color": None,
    },
    "unfinish": {
        "bg_path": None,
        "fg_path": None,
        "interactable": None,
        "floor_color": (255, 0, 255),
        "edge_color": (0, 0, 0),
    },
    "boss_room": {
        "bg_path": "Game_project/assets/background/boss_bg_back.png",
        "fg_path": None,
        "interactable": None,
        "floor_color": (50, 0, 0), # Ominous Dark Red
        "edge_color": (255, 0, 0),
    },
}

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.w, self.h = w, h
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.change_theme(GREEN, (0, 200, 0))

    def change_theme(self, main_color, edge_color):
        # Clear the previous image
        self.image.fill((0, 0, 0, 0))

        if main_color is not None:
            # If we have a color, fill the whole platform
            self.image.fill(main_color)
            if edge_color:
                pygame.draw.rect(self.image, edge_color, (0, 0, self.w, 5))


class Background:
    def __init__(self):
        self.rect = pygame.Rect(0, BAR_HEIGHT, GAME_WIDTH, GAME_HEIGHT - (BAR_HEIGHT * 2))
        self.back_image = None
        self.fore_image = None

    def update_theme(self, data):
        self.back_image = self.load_and_scale(data["bg_path"])
        self.fore_image = self.load_and_scale(data.get("fg_path")) if data.get("fg_path") else None

    def load_and_scale(self, path):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (self.rect.width, self.rect.height))
        except:
            return None

    def draw_back(self, surface):
        if self.back_image:
            surface.blit(self.back_image, self.rect)
        else:
            # DRAW A CHECKERBOARD (Magenta and Black)
            size = 40
            for row in range(self.rect.top, self.rect.bottom, size):
                for col in range(self.rect.left, self.rect.right, size):
                    color = (255, 0, 255) if (row // size + col // size) % 2 == 0 else (0, 0, 0)
                    pygame.draw.rect(surface, color, (col, row, size, size))

            font = pygame.font.SysFont("Courier", 30, bold=True)
            text = font.render("WORLD ASSETS MISSING", True, (255, 255, 255))
            surface.blit(text, (GAME_WIDTH // 2 - 200, GAME_HEIGHT // 2))

    def draw_fore(self, surface):
        if self.fore_image: surface.blit(self.fore_image, self.rect)

class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_path, scale_factor=0.6):
        super().__init__()
        self.frames = []
        self.frame_index = 0
        self.animation_speed = 0.05  # Adjust this: smaller = slower
        self.animation_timer = 0

        paths = [sprite_path, sprite_path.replace("_1.png", "_2.png")]

        for path in paths:
            try:
                img = pygame.image.load(path).convert_alpha()
                new_w = int(img.get_width() * scale_factor)
                new_h = int(img.get_height() * scale_factor)
                self.frames.append(pygame.transform.scale(img, (new_w, new_h)))
            except:
                print(f"Could not load frame: {path}")

        self.image = self.frames[0]
        self.rect = self.image.get_rect(bottomleft=(x, y))
        # Tighten the interaction hitbox
        self.interact_rect = self.rect.inflate(-10, 0)

    def update(self, dt=1 / 60):
        # Handle simple 2-frame loop
        if len(self.frames) > 1:
            self.animation_timer += self.animation_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = self.frames[self.frame_index]

    def talk(self, dialogue_ui):
        # If dialogue_ui is not active, start a new conversation
        if not dialogue_ui.active:
            lines = [
                "You found me!",
                "This is a test of the instant-skip feature.",
                "Notice how this long sentence appears immediately when you press F?"
            ]
            dialogue_ui.start_dialogue(lines)

class GlitchNPC(NPC):
    def __init__(self, x, y):
        # We use a standard sprite but maybe scale him weirdly to look "broken"
        super().__init__(x, y, "Game_project/assets/sprites/BW_npc/npc_01_1.png", scale_factor=0.3)
        self.image.fill((200, 200, 200), special_flags=pygame.BLEND_RGB_MULT) # Make him gray/ghostly

    def talk(self, dialogue_ui):
        if not dialogue_ui.active:
            lines = [
                "ERROR: DIALOGUE_NOT_FOUND",
                "Wait... is the elevator working already?",
                "I'm not even supposed to have legs yet. Look at my collision box!",
                "Please tell the developer to finish my textures. It's drafty in here."
            ]
            dialogue_ui.start_dialogue(lines)

class Camp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("Game_project/assets/background/forest_camp.png").convert_alpha()
        self.rect = self.image.get_rect(bottomleft=(x, y))
        self.interact_rect = self.rect.inflate(-15, 0)

    def use(self, player, level_manager):
        # Restore stats
        player.hp = player.max_hp
        player.sanity = player.max_sanity

        # Trigger the visual effect
        level_manager.start_sleep_fade()
        print("Rested at camp: Fully Healed!")

class LevelManager:
    def __init__(self, platform_ref, elevator_ref):
        self.last_theme = None  # <--- MOVE THIS TO THE TOP
        self.bg = Background()
        self.floor = platform_ref
        self.elevator = elevator_ref
        self.is_fading = False
        self.travel_timer = 0
        self.travel_duration = 180
        self.fade_alpha = 0
        self.fade_speed = 4
        self.fade_state = "IDLE"
        self.travel_direction = 0
        self.current_interactable = None
        self.pending_enemies = []  # <--- NEW: List to hold enemies for the GameplayState to grab
        self.travel_lines = []
        self.next_level()
        self.show_debug = True
        self.left_wall = pygame.Rect(-10, 0, 10, GAME_HEIGHT)
        self.right_wall = pygame.Rect(GAME_WIDTH, 0, 10, GAME_HEIGHT)


    def start_sleep_fade(self):
        if self.fade_state == "IDLE":
            self.is_fading = True
            self.fade_alpha = 0
            self.fade_state = "SLEEP_OUT"  # Fading to black

    def start_transition(self, direction):
        if self.fade_state == "IDLE":
            self.is_fading = True
            self.fade_state = "TRAVEL"
            self.travel_timer = 0
            self.travel_direction = -1 if direction == "UP" else 1
            self.elevator.close_doors()
            self.travel_lines = [[random.randint(0, GAME_WIDTH), random.randint(0, GAME_HEIGHT),
                                  random.randint(10, 30), random.randint(5, 12)] for _ in range(15)]

    def update(self):
        if self.fade_state == "TRAVEL" and self.travel_lines:
            for line in self.travel_lines:
                line[1] += line[3] * self.travel_direction * -1
                if line[1] > GAME_HEIGHT:
                    line[1] = -30
                elif line[1] < -30:
                    line[1] = GAME_HEIGHT

        if self.fade_state == "TRAVEL":
            self.travel_timer += 1
            if self.travel_timer >= self.travel_duration:
                self.next_level()
                self.fade_alpha = 255
                self.fade_state = "FADE_IN"
                self.elevator.open_doors()

        elif self.fade_state == "FADE_IN":
            self.fade_alpha -= self.fade_speed
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fade_state = "IDLE"
                self.is_fading = False

        if self.current_interactable and isinstance(self.current_interactable, NPC):
            self.current_interactable.update()

        # Inside LevelManager.update
        if self.fade_state == "SLEEP_OUT":
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                # Optional: Add a small delay here if you want the screen to stay black longer
                self.fade_state = "SLEEP_IN"

        elif self.fade_state == "SLEEP_IN":
            self.fade_alpha -= self.fade_speed
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fade_state = "IDLE"
                self.is_fading = False

    def next_level(self):
        # 1. Get all possible themes
        all_themes = list(MAP_DATA.keys())

        # 2. Filter out the last theme so it doesn't repeat
        possible_themes = [t for t in all_themes if t != self.last_theme]

        # 3. Pick from the remaining themes
        theme = random.choice(possible_themes)

        # Update last_theme for the next time
        self.last_theme = theme

        # --- DEBUG OVERRIDE ---
        #theme = "boss_room"

        self.current_data = MAP_DATA[theme]
        self.bg.update_theme(self.current_data)

        # Clear old interactables and pending enemies
        self.current_interactable = None
        self.pending_enemies = []

        # Update Floor Visuals
        self.floor.change_theme(self.current_data.get("floor_color"), self.current_data.get("edge_color"))

        obj_type = self.current_data.get("interactable")

        # --- SPAWN LOGIC ---

        # 1. Spawn Friendly NPCs or Camps
        if theme == "forest":
            spawn_x = random.randint(300, 500)
            spawn_y = self.floor.rect.top + 30
            self.current_interactable = Camp(spawn_x, spawn_y)

        elif theme == "BW":
            spawn_x = random.randint(200, 400)
            spawn_y = self.floor.rect.top + 20
            # Ensure path is correct for your asset
            self.current_interactable = GlitchNPC(spawn_x, spawn_y)

        # 2. Spawn Enemies for Unfinished Level
        if theme == "unfinish":
            for i in range(3):
                spawn_x = random.randint(300, 700)
                spawn_y = self.floor.rect.top
                slime = SlimeEnemy(spawn_x, spawn_y)
                self.pending_enemies.append(slime)

        # 3. Spawn Boss for Boss Room
        if theme == "boss_room":
            spawn_x = GAME_WIDTH // 2
            spawn_y = self.floor.rect.top

            # Import Boss at the top of level_manager.py
            boss = Boss(spawn_x, spawn_y)
            self.pending_enemies.append(boss)

    def draw_travel_effect(self, surface):
        for x, y, length, speed in self.travel_lines:
            pygame.draw.line(surface, (140, 140, 150), (x, y), (x, y + length), 1)

