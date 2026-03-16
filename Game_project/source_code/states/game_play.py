import pygame
import math
import random
from source_code.states.base_state import BaseState
from source_code.settings import WHITE, GAME_HEIGHT, GAME_WIDTH, BLACK, BAR_HEIGHT
from source_code.characters.player import Player
from source_code.systems.ui import HUD, ElevatorUI, DialogueSystem
from source_code.worlds.elevator import Elevator
from source_code.characters.enemies import Enemy, SlimeEnemy, Boss, BossMinion
from source_code.worlds.level_manager import Platform, LevelManager, NPC, Camp
from source_code.systems.threat import ThreatSystem


class GameplayState(BaseState):
    def __init__(self, engine):
        super().__init__(engine)
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.shake_offset = (0, 0)
        self.show_debug = True
        self.threat_system = ThreatSystem(start_level=2)

        # Win Condition Flags
        self.game_won = False
        self.boss_spawned = False

        # 1. Dialogue System
        self.dialogue_system = DialogueSystem()

        # 2. Setup Floor Position
        floor_y = GAME_HEIGHT - BAR_HEIGHT - 30

        # 3. Font Setup
        pygame.font.init()
        self.ui_font = pygame.font.SysFont("Arial", 12, bold=True)
        self.f_prompt_surf = self.ui_font.render("F", True, WHITE)
        self.f_outline_surf = self.ui_font.render("F", True, BLACK)

        # 4. World Setup
        self.main_floor = Platform(0, floor_y, GAME_WIDTH, 30)
        self.platforms.add(self.main_floor)
        self.all_sprites.add(self.main_floor)

        self.elevator = Elevator(50, floor_y - 120)
        self.elevator.open_doors()

        self.level_manager = LevelManager(self.main_floor, self.elevator)
        self.elevator_ui = ElevatorUI()

        # 5. Initialize Player
        self.player = Player()
        self.all_sprites.add(self.player)

        # Spawn Player INSIDE the elevator
        self.player.rect.x = self.elevator.rect.x + 40
        self.player.pos_x = float(self.player.rect.x)
        self.player.rect.bottom = floor_y + self.player.y_offset

        # 6. Initialize HUD
        self.hud = HUD(self.player)

    def draw_boss_hp(self, surface):
        # Find the boss in the enemies group
        boss = next((e for e in self.enemies if isinstance(e, Boss)), None)

        if boss:
            self.boss_spawned = True  # Mark that we have seen the boss
            bar_width = 400
            bar_height = 20
            x = (GAME_WIDTH - bar_width) // 2
            y = 60

            # Health ratio (Ensure 500 matches your Boss class HP)
            health_ratio = max(0, boss.hp / 500)

            # Draw Bar
            pygame.draw.rect(surface, BLACK, (x - 2, y - 2, bar_width + 4, bar_height + 4))
            pygame.draw.rect(surface, (200, 0, 0), (x, y, bar_width * health_ratio, bar_height))

            # Boss Name
            font = pygame.font.SysFont("Arial", 16, bold=True)
            name_surf = font.render("THE VOID GUARDIAN", True, WHITE)
            surface.blit(name_surf, (x, y - 22))

    def handle_events(self, events):
        if not self.elevator_ui.active and not self.dialogue_system.active:
            self.player.handle_input(events)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.dialogue_system.active:
                    if self.dialogue_system.char_index < len(self.dialogue_system.current_text):
                        self.dialogue_system.char_index = len(self.dialogue_system.current_text)
                    else:
                        self.dialogue_system.next_line()
                elif self.elevator_ui.active and self.elevator_ui.hover_state:
                    direction = self.elevator_ui.hover_state
                    if direction == "UP" and self.threat_system.level <= self.threat_system.min_level:
                        print("Already at the highest floor!")
                    else:
                        if direction == "UP":
                            self.threat_system.decrease()
                        elif direction == "DOWN":
                            self.threat_system.increase()
                        self.enemies.empty()
                        self.level_manager.start_transition(direction)
                        self.elevator_ui.active = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.next_state = "MENU"
                if event.key == pygame.K_f:
                    if self.dialogue_system.active:
                        if self.dialogue_system.char_index < len(self.dialogue_system.current_text):
                            self.dialogue_system.char_index = len(self.dialogue_system.current_text)
                        else:
                            self.dialogue_system.next_line()
                    elif self.elevator_ui.active:
                        self.elevator_ui.active = False
                    elif not self.level_manager.is_fading:
                        if self.player.rect.colliderect(self.elevator.interact_rect):
                            self.elevator_ui.active = True
                        elif self.level_manager.current_interactable:
                            obj = self.level_manager.current_interactable
                            if self.player.rect.colliderect(obj.interact_rect):
                                if isinstance(obj, NPC):
                                    obj.talk(self.dialogue_system)
                                elif isinstance(obj, Camp):
                                    obj.use(self.player, self.level_manager)

                if not self.dialogue_system.active and pygame.K_1 <= event.key <= pygame.K_5:
                    self.player.inventory.select_slot(event.key - pygame.K_1)

    def update(self, dt):
        self.dialogue_system.update()
        mouse_pos = self.engine.get_game_mouse_pos()
        self.threat_system.update(self.player)

        if self.elevator_ui.active:
            self.elevator_ui.update(mouse_pos)
            self.player.animate()
            return

        self.elevator.update()

        if self.level_manager.is_fading:
            self.player.animate()
            self.level_manager.update()
            if self.level_manager.fade_state == "TRAVEL":
                self.enemies.empty()
                if self.elevator.state == "OPEN": self.elevator.close_doors()
            return

        if self.dialogue_system.active:
            self.player.animate()
            return

        if self.level_manager.pending_enemies:
            for enemy in self.level_manager.pending_enemies:
                self.enemies.add(enemy)
            self.level_manager.pending_enemies = []

        self.level_manager.update()

        # Player Movement
        if self.elevator.state == "OPEN":
            self.player.update(self.platforms, self.enemies)
        else:
            self.player.animate()

        # Enemy Updates
        boss_present = False
        for enemy in self.enemies:
            if isinstance(enemy, Boss):
                enemy.update(self.player, self.enemies)
                boss_present = True
                self.boss_spawned = True
            elif isinstance(enemy, (BossMinion, SlimeEnemy)):
                enemy.update(self.player)
            else:
                enemy.update()

        # Win Condition: Only triggers in boss room if boss was spawned and is now gone
        if self.level_manager.last_theme == "boss_room" and self.boss_spawned:
            if not boss_present and len(self.enemies) == 0:
                self.game_won = True
                print("Win")

    def draw(self, surface):
        surface.fill((40, 40, 45))

        # 1. Background Layers
        self.level_manager.bg.draw_back(surface)
        self.platforms.draw(surface)

        # --- STEP 1.5: DRAW THE ITEMS/NPCs ---
        # Add this line so NPCs, Camps, and Chests actually appear!
        if self.level_manager.current_interactable:
            obj = self.level_manager.current_interactable
            surface.blit(obj.image, obj.rect)

        self.enemies.draw(surface)

        # 2. Transition Effects
        if self.level_manager.is_fading and self.level_manager.fade_state == "TRAVEL":
            overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
            overlay.fill(BLACK)
            surface.blit(overlay, (0, 0))
            self.level_manager.draw_travel_effect(surface)

        # 3. Midground (Entities)
        self.draw_entities(surface)  # Draws Player + Elevator Back
        self.draw_elevator_front(surface)
        self.level_manager.bg.draw_fore(surface)

        # 4. Interaction Prompts (Floating 'F' keys)
        if not self.elevator_ui.active and not self.level_manager.is_fading and not self.dialogue_system.active:
            if self.player.rect.colliderect(self.elevator.interact_rect):
                self.draw_interaction_prompt(surface, self.elevator.rect)
            elif self.level_manager.current_interactable:
                obj = self.level_manager.current_interactable
                if not isinstance(obj, Enemy) and self.player.rect.colliderect(obj.interact_rect):
                    self.draw_interaction_prompt(surface, obj.rect)

        # 5. UI LAYER
        if self.elevator_ui.active:
            self.draw_dimmer(surface)
            self.elevator_ui.draw(surface)

        self.draw_boss_hp(surface)
        self.hud.draw(surface, self.threat_system.level)
        self.dialogue_system.draw(surface)

        # 6. WIN SCREEN (Highest Priority)
        if self.game_won:
            overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
            overlay.fill(BLACK)
            overlay.set_alpha(200)
            surface.blit(overlay, (0, 0))

            font = pygame.font.SysFont("Courier", 50, bold=True)
            win_text = font.render("MISSION ACCOMPLISHED", True, (0, 255, 0))
            surface.blit(win_text, (GAME_WIDTH // 2 - 250, GAME_HEIGHT // 2 - 25))

            sub_text = font.render("Press ESC to Return", True, WHITE)
            sub_text_scaled = pygame.transform.scale(sub_text, (200, 30))
            surface.blit(sub_text_scaled, (GAME_WIDTH // 2 - 100, GAME_HEIGHT // 2 + 50))


    def draw_interaction_prompt(self, surface, target_rect):
        px, py = target_rect.centerx, target_rect.top - 5
        pygame.draw.polygon(surface, BLACK, [(px - 7, py - 6), (px + 7, py - 6), (px, py + 2)])
        pygame.draw.polygon(surface, WHITE, [(px - 5, py - 5), (px + 5, py - 5), (px, py)])
        text_x, text_y = px - 3, py - 22
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            surface.blit(self.f_outline_surf, (text_x + ox, text_y + oy))
        surface.blit(self.f_prompt_surf, (text_x, text_y))

    def draw_debug(self, surface):
        pygame.draw.rect(surface, (0, 0, 255), self.elevator.interact_rect, 2)
        pygame.draw.rect(surface, (0, 255, 0), self.player.rect, 2)
        if self.level_manager.current_interactable:
            pygame.draw.rect(surface, (255, 0, 0), self.level_manager.current_interactable.interact_rect, 2)

    def draw_entities(self, surface):
        ox, oy = self.shake_offset
        surface.blit(self.elevator.back_image, (self.elevator.rect.x + ox, self.elevator.rect.y + oy))
        surface.blit(self.player.image, (self.player.pos_x + ox, self.player.pos_y + oy))

    def draw_elevator_front(self, surface):
        ox, oy = self.shake_offset
        surface.blit(self.elevator.image, (self.elevator.rect.x + ox, self.elevator.rect.y + oy))

    def draw_dimmer(self, surface):
        dimmer = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        dimmer.fill(BLACK)
        dimmer.set_alpha(150)
        surface.blit(dimmer, (0, 0))