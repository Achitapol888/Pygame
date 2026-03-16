import pygame

class ThreatSystem:
    def __init__(self, start_level=2):
        self.level = start_level
        self.min_level = 1
        self.max_level = 10  # Increased to 10
        self.last_drain_time = pygame.time.get_ticks()
        self.is_climax = False
        # Timer for draining sanity slowly over time
        self.last_drain_time = pygame.time.get_ticks()

    def increase(self):
        if self.level < self.max_level:
            self.level += 1
            print(f"Elevator went DOWN. Threat increased to {self.level}")

    def decrease(self):
        if self.level > self.min_level:
            self.level -= 1
            print(f"Elevator went UP. Threat decreased to {self.level}")

    def handle_climax_event(self, player):
        """ Template for Level 10 logic """
        # Example: Constant Sanity drain every frame or Screen Shake trigger
        player.sanity -= 0.01
        # print("MAX THREAT REACHED: Reality is breaking...")

    def update(self, player):
        now = pygame.time.get_ticks()

        # Trigger Level 10 Event
        if self.level >= 10:
            self.is_climax = True
            self.handle_climax_event(player)
        else:
            self.is_climax = False

        # --- DYNAMIC TIMER LOGIC ---
        # Level 1 & 2: 10 seconds (10000ms)
        # Level 3: 9 seconds (9000ms)
        # Level 4: 8 seconds (8000ms)
        # Level 5: 7 seconds (7000ms)

        # Calculation: Base 10s, minus 1s for every level above 2
        if self.level <= 2:
            interval = 10000
        else:
            # Subtract 1000ms for every level past Level 2
            reduction = (self.level - 2) * 1000
            interval = 10000 - reduction

        # --- CHECK TIMER ---
        if now - self.last_drain_time > interval:
            # We always decrease by 1 at level 2 or higher
            if self.level >= 2:
                player.sanity -= 1

                # Safety clamp
                if player.sanity < 0:
                    player.sanity = 0

                print(f"Drain triggered! Threat: {self.level}, Interval: {interval / 1000}s")

            self.last_drain_time = now