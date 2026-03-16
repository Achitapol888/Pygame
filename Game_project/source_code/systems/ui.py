# source_code/systems/ui.py
import pygame
from source_code.settings import BLACK, WHITE, RED, GAME_WIDTH, GAME_HEIGHT, BAR_HEIGHT

class HUD:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.SysFont("Arial", 14, bold=True)
        self.slot_size = 32
        self.padding = 5

        # --- Load All Item Icons from Assets ---
        base_path = "Game_project/assets/icons/"

        self.icons = {
            "Pistol": pygame.image.load(f"{base_path}handgun.png").convert_alpha(),
            "Knife": pygame.image.load(f"{base_path}knife.png").convert_alpha(),
            "Ammo": pygame.image.load(f"{base_path}handgun_ammo.png").convert_alpha(),
            "Adrenaline": pygame.image.load(f"{base_path}adrenaline.png").convert_alpha(),
            "Chip": pygame.image.load(f"{base_path}chip.png").convert_alpha(),
            "Coke": pygame.image.load(f"{base_path}coke.png").convert_alpha(),
            "First Aid": pygame.image.load(f"{base_path}first_aid.png").convert_alpha(),
            "Medkit": pygame.image.load(f"{base_path}medkit.png").convert_alpha(),
            "Painkiller": pygame.image.load(f"{base_path}painkiller.png").convert_alpha(),
            "Sedative": pygame.image.load(f"{base_path}sedative.png").convert_alpha(),
            "Snack": pygame.image.load(f"{base_path}snack.png").convert_alpha()
        }

    def draw(self, surface, threat_level):
        # 1. Draw the Black Focus Bars (Letterboxing)
        pygame.draw.rect(surface, BLACK, (0, 0, GAME_WIDTH, BAR_HEIGHT))
        pygame.draw.rect(surface, BLACK, (0, GAME_HEIGHT - BAR_HEIGHT, GAME_WIDTH, BAR_HEIGHT))

        # 2. Draw Components
        self.draw_stats(surface)
        self.draw_hotbar(surface)
        self.draw_ammo_ui(surface)
        # Pass the threat_level to the UI drawer
        self.draw_threat_ui(surface, threat_level)

    def draw_threat_ui(self, surface, threat_level):
        # Position at Bottom Right
        ui_x = GAME_WIDTH - 150
        ui_y = GAME_HEIGHT - BAR_HEIGHT + 12

        # 1. Separator Line
        pygame.draw.line(surface, (60, 60, 60), (ui_x - 10, ui_y), (ui_x - 10, ui_y + 30), 1)

        # 2. Dynamic Color based on Threat Level
        colors = {
            1: (0, 255, 0),    # Green
            2: (255, 255, 0),  # Yellow
            3: (255, 150, 0),  # Orange
            4: (255, 0, 0),    # Red
            5: (150, 0, 0)     # Dark Red
        }
        color = colors.get(threat_level, RED)

        # 3. Draw "THREAT LEVEL" Text
        label_font = pygame.font.SysFont("Arial", 10, bold=True)
        label = label_font.render("THREAT LEVEL", True, (150, 150, 150))
        surface.blit(label, (ui_x, ui_y + 22))

        # 4. Draw the Number
        val_font = pygame.font.SysFont("Courier", 28, bold=True)

        # Max threat visual effect
        y_offset = 0
        if threat_level == 5 and (pygame.time.get_ticks() // 100) % 2 == 0:
            y_offset = 1
            color = WHITE

        val_text = val_font.render(f"0{threat_level}", True, color)
        surface.blit(val_text, (ui_x + 85, ui_y + y_offset))

    # ... Include draw_stats, draw_hotbar, and draw_ammo_ui below ...

    def draw_ammo_ui(self, surface):
        ui_x = 20
        ui_y = GAME_HEIGHT - BAR_HEIGHT + 12

        # 1. Separator Line
        pygame.draw.line(surface, (60, 60, 60), (ui_x - 10, ui_y), (ui_x - 10, ui_y + 30), 1)

        # 2. Icon
        icon = self.icons.get("Pistol")
        if icon:
            scaled_icon = pygame.transform.scale(icon, (48, 48))
            surface.blit(scaled_icon, (ui_x -10, ui_y -10))

        # 3. Main Mag Number (Current Ammo)
        ammo_font = pygame.font.SysFont("Courier", 28, bold=True)
        ammo_color = WHITE

        # Flash Mag number red when low (3 or less)
        if self.player.pistol_ammo <= 3:
            ammo_color = RED if (pygame.time.get_ticks() // 250) % 2 == 0 else (100, 0, 0)

        mag_text = ammo_font.render(f"{self.player.pistol_ammo:02d}", True, ammo_color)
        surface.blit(mag_text, (ui_x + 35, ui_y - 3))

        # 4. Reserve Number (Total Ammo)
        reserve_font = pygame.font.SysFont("Courier", 16, bold=True)
        reserve_text = reserve_font.render(f"/{self.player.pistol_reserve:02d}", True, (150, 150, 150))
        surface.blit(reserve_text, (ui_x + 70, ui_y + 8))

        # 5. Dynamic Status Text
        sub_font = pygame.font.SysFont("Arial", 9, bold=True)

        if self.player.is_reloading:
            status = "RELOADING..."
            color = (255, 200, 0)  # Yellow
        elif self.player.pistol_ammo > 0:
            status = "READY"
            color = (120, 120, 120)  # Grey
        else:
            status = "EMPTY - PRESS R"
            color = RED

        sub_text = sub_font.render(f"STATUS: {status}", True, color)
        surface.blit(sub_text, (ui_x + 37, ui_y + 25))

    def draw_stats(self, surface):
        # (Your HP, Stamina, and Sanity code remains the same...)
        hp_x, hp_y = 10, 15
        hp_width = 100
        current_hp_width = (self.player.hp / self.player.max_hp) * hp_width
        pygame.draw.rect(surface, WHITE, (hp_x, hp_y, hp_width + 4, 14), 1)
        pygame.draw.rect(surface, RED, (hp_x + 2, hp_y + 2, current_hp_width, 10))

        stamina_x, stamina_y = 10, 32
        stamina_width = 100
        stamina_ratio = self.player.stamina / self.player.max_stamina
        current_stamina_width = stamina_ratio * stamina_width
        stamina_color = (0, 150, 255) if stamina_ratio > 0.75 else (255, 200, 0) if stamina_ratio > 0.3 else RED
        pygame.draw.rect(surface, WHITE, (stamina_x, stamina_y, stamina_width + 4, 10), 1)
        pygame.draw.rect(surface, stamina_color, (stamina_x + 2, stamina_y + 2, current_stamina_width, 6))

        sanity_label = self.font.render(f"MIND: {int(self.player.sanity)}%", True, WHITE)
        surface.blit(sanity_label, (120, 20))

    def draw_hotbar(self, surface):
        inv = self.player.inventory
        start_x = GAME_WIDTH - (inv.num_slots * (self.slot_size + self.padding)) - 10
        start_y = (BAR_HEIGHT // 2) - (self.slot_size // 2)

        for i in range(inv.num_slots):
            x = start_x + (i * (self.slot_size + self.padding))
            rect = pygame.Rect(x, start_y, self.slot_size, self.slot_size)

            color = RED if i == inv.active_index else WHITE
            pygame.draw.rect(surface, color, rect, 2 if i == inv.active_index else 1)

            item_data = inv.slots[i]
            if item_data:
                name = item_data["name"]
                if name in self.icons:
                    icon_img = self.icons[name]
                    scaled_icon = pygame.transform.scale(icon_img, (self.slot_size - 8, self.slot_size - 8))
                    surface.blit(scaled_icon, (rect.x + 4, rect.y + 4))

                # Draw count ONLY for consumables (Stackable items)
                # Pistol/Knife don't need a "1" underneath them
                if item_data["count"] > 1:
                    count_text = self.font.render(str(item_data["count"]), True, WHITE)
                    surface.blit(count_text, (rect.right - 10, rect.bottom - 12))

class ElevatorUI:
    def __init__(self):
        # Load your 54x100 asset
        self.image = pygame.image.load("Game_project/assets/UI/elevator_UI.png").convert_alpha()
        self.width, self.height = 54, 100
        self.rect = self.image.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2))

        self.active = False
        self.hover_state = None  # "UP", "DOWN", or None

    def update(self, mouse_pos):
        if not self.active: return

        if self.rect.collidepoint(mouse_pos):
            # Logic: Divide 100px height by 2.
            # Top 50px is UP, Bottom 50px is DOWN.
            relative_y = mouse_pos[1] - self.rect.top
            if relative_y < self.height // 2:
                self.hover_state = "UP"
            else:
                self.hover_state = "DOWN"
        else:
            self.hover_state = None


    def draw(self, surface):
        if not self.active: return

        # Optional: Draw a dark overlay behind the UI
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        # Draw the main arrow asset
        surface.blit(self.image, self.rect)

        # Visual feedback: Highlight the half we are hovering over
        if self.hover_state == "UP":
            highlight = pygame.Rect(self.rect.x, self.rect.y, self.width, self.height // 2)
            pygame.draw.rect(surface, (255, 255, 255), highlight, 2)
        elif self.hover_state == "DOWN":
            highlight = pygame.Rect(self.rect.x, self.rect.centery, self.width, self.height // 2)
            pygame.draw.rect(surface, (255, 255, 255), highlight, 2)

class DialogueSystem:
    def __init__(self):
        self.active = False
        self.text_queue = []
        self.current_text = ""
        self.display_text = ""
        self.char_index = 0
        self.typing_speed = 0.5  # Higher = faster typing

        # UI Styling
        self.font = pygame.font.SysFont("Arial", 18)
        self.box_rect = pygame.Rect(50, GAME_HEIGHT - 150, GAME_WIDTH - 100, 100)

    def start_dialogue(self, lines):
        self.text_queue = lines
        self.active = True
        self.next_line()

    def next_line(self):
        if self.text_queue:
            self.current_text = self.text_queue.pop(0)
            self.display_text = ""
            self.char_index = 0
        else:
            self.active = False  # No more text

    def update(self):
        if not self.active: return

        # 1. Increment the timer if there's still text to type
        if self.char_index < len(self.current_text):
            self.char_index += self.typing_speed

        # 2. ALWAYS update the display text based on the index.
        # Moving this here ensures that when you skip, the full text shows up.
        self.display_text = self.current_text[:int(self.char_index)]

    def draw(self, surface):
        if not self.active: return

        # 1. Draw Semi-transparent Box
        overlay = pygame.Surface((self.box_rect.width, self.box_rect.height))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 25))
        surface.blit(overlay, self.box_rect)

        # 2. Draw Border
        pygame.draw.rect(surface, WHITE, self.box_rect, 2)

        # 3. Draw Text
        text_surf = self.font.render(self.display_text, True, WHITE)
        surface.blit(text_surf, (self.box_rect.x + 20, self.box_rect.y + 20))

        # 4. "Press F" hint (if typing is done)
        if self.char_index >= len(self.current_text):
            hint = self.font.render("▼ [F]", True, (200, 200, 200))
            surface.blit(hint, (self.box_rect.right - 60, self.box_rect.bottom - 30))