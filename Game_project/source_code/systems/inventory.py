class Inventory:
    def __init__(self, slots=5):
        self.num_slots = slots
        self.active_index = 0  # 0 to 4
        # Start with empty slots (None) or placeholder names
        self.slots = ["Pistol", "Flashlight", None, None, None]

    def select_slot(self, index):
        if 0 <= index < self.num_slots:
            self.active_index = index
            print(f"Selected Slot: {self.active_index + 1} - {self.slots[self.active_index]}")

    def next_slot(self):
        # The modulo % ensures it wraps from 4 back to 0
        self.active_index = (self.active_index + 1) % self.num_slots
        print(f"Cycled to Slot: {self.active_index + 1}")

    def get_active_item(self):
        return self.slots[self.active_index]