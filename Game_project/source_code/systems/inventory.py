class Inventory:
    def __init__(self, slots=6):
        self.num_slots = slots
        self.active_index = 0
        # REMOVED Ammo from here - it's now just a number on the Player
        self.slots = [
            {"name": "Pistol", "count": 1},
            {"name": "Knife", "count": 1},
            {"name": "Chip", "count": 2},
            {"name": "Adrenaline", "count": 1},
            None,
            None
        ]

    def use_active_item(self, player):
        item = self.slots[self.active_index]
        if not item: return

        # 1. Ammo is used automatically when shooting, not from hotbar use
        # 2. Consumable Logic
        if item["name"] in ["Chip", "Adrenaline", "Snack", "Medkit"]:
            self.apply_effect(item["name"], player)
            item["count"] -= 1

            # Remove item if empty
            if item["count"] <= 0:
                self.slots[self.active_index] = None

    def apply_effect(self, name, player):
        if name == "Chip":
            player.sanity = min(player.max_sanity, player.sanity + 10)
        elif name == "Adrenaline":
            player.stamina = player.max_stamina
            player.adrenaline_timer = 300  # 5 seconds of infinite stamina
        if name == "Ammo":
            # Picking up a box of ammo gives you a full mag's worth to your pocket
            player.pistol_reserve += 8

    def select_slot(self, index):
        if 0 <= index < self.num_slots: self.active_index = index

    def next_slot(self):
        self.active_index = (self.active_index + 1) % self.num_slots

    def get_active_item(self):
        item = self.slots[self.active_index]
        return item["name"] if item else None