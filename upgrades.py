import pygame
import random
from settings import *

PASSIVE_MAX_LEVEL = 5
WEAPON_MAX_LEVEL = 5

ALL_UPGRADES = [
    {"name": "Speed Boost",  "desc": "+15% movement speed",          "type": "passive", "color": (50, 200, 100)},
    {"name": "Damage Boost", "desc": "+20% damage",                  "type": "passive", "color": (220, 80, 80)},
    {"name": "Rapid Fire",   "desc": "+15% fire rate",               "type": "passive", "color": (220, 180, 50)},
    {"name": "Piercing",     "desc": "Bullets pierce +1 enemy",      "type": "passive", "color": (150, 100, 220)},
    {"name": "Max Health",   "desc": "+20% max HP",                  "type": "passive", "color": (220, 50, 50)},
    {"name": "Vampirism",    "desc": "10% lifesteal",                "type": "passive", "color": (180, 30, 30)},
    {"name": "Armor",        "desc": "-10% damage taken",            "type": "passive", "color": (100, 150, 220)},
    {"name": "Regeneration", "desc": "+1 HP regen per second",       "type": "passive", "color": (50, 220, 150)},
    {"name": "Magnet",       "desc": "+50% pickup radius",           "type": "passive", "color": (220, 150, 50)},
    {"name": "XP Boost",     "desc": "+50% XP gained",               "type": "passive", "color": (100, 220, 220)},
    {"name": "Knife",        "desc": "Throws knife at nearest enemy","type": "weapon",  "color": (180, 180, 180)},
    {"name": "Magic Orb",    "desc": "Orbs orbit around you",        "type": "weapon",  "color": (100, 150, 255)},
    {"name": "Sand Spike",   "desc": "Spikes burst under enemies",   "type": "weapon",  "color": (200, 150, 50)},
    {"name": "Boomerang",    "desc": "Returns and pierces enemies",  "type": "weapon",  "color": (150, 100, 50)},
]

class UpgradeScreen:
    def __init__(self):
        self.cards = []
        self.card_rects = []
        self.visible = False

    WEAPON_CLASSES = {}

    def _get_weapon_classes(self):
        if not UpgradeScreen.WEAPON_CLASSES:
            from weapons import Knife, MagicOrb, SandSpike, Boomerang
            UpgradeScreen.WEAPON_CLASSES = {
                "Knife": Knife,
                "Magic Orb": MagicOrb,
                "Sand Spike": SandSpike,
                "Boomerang": Boomerang,
            }
        return UpgradeScreen.WEAPON_CLASSES

    def show(self, player=None):
        available = list(ALL_UPGRADES)

        if player:
            weapon_classes = self._get_weapon_classes()
            filtered = []
            for card in available:
                if card["type"] == "weapon":
                    weapon_class = weapon_classes.get(card["name"])
                    existing = next((w for w in player.weapons if isinstance(w, weapon_class)), None)
                    if existing and existing.level >= WEAPON_MAX_LEVEL:
                        continue
                if card["type"] == "passive":
                    if player.passive_levels.get(card["name"], 0) >= PASSIVE_MAX_LEVEL:
                        continue
                filtered.append(card)
            available = filtered

        self.cards = random.sample(available, min(3, len(available)))
        self.visible = True

    def draw(self, screen, player=None):
        if not self.visible:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        font_title = pygame.font.SysFont(None, 60)
        font_name  = pygame.font.SysFont(None, 44)
        font_desc  = pygame.font.SysFont(None, 30)
        font_type  = pygame.font.SysFont(None, 26)

        title = font_title.render("Choose Upgrade", True, (255, 220, 0))
        tr = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200))
        screen.blit(title, tr)

        card_w = 240
        card_h = 320
        gap = 50
        total_w = card_w * 3 + gap * 2
        start_x = (SCREEN_WIDTH - total_w) // 2
        start_y = SCREEN_HEIGHT // 2 - card_h // 2

        self.card_rects = []
        mouse_pos = pygame.mouse.get_pos()

        for i, card in enumerate(self.cards):
            x = start_x + i * (card_w + gap)
            y = start_y
            rect = pygame.Rect(x, y, card_w, card_h)
            self.card_rects.append(rect)

            hovered = rect.collidepoint(mouse_pos)
            bg_color = (60, 60, 90) if hovered else (35, 35, 55)
            border_color = card["color"] if hovered else (80, 80, 120)

            current_level = 0
            if player:
                if card["type"] == "passive":
                    current_level = player.passive_levels.get(card["name"], 0)
                else:
                    weapon_classes = self._get_weapon_classes()
                    weapon_class = weapon_classes.get(card["name"])
                    existing = next((w for w in player.weapons if isinstance(w, weapon_class)), None)
                    current_level = existing.level if existing else 0
            next_level = current_level + 1

            pygame.draw.rect(screen, bg_color, rect, border_radius=16)
            pygame.draw.rect(screen, border_color, rect, 3, border_radius=16)

            type_text = "WEAPON" if card["type"] == "weapon" else "PASSIVE"
            type_surf = font_type.render(type_text, True, card["color"])
            type_r = type_surf.get_rect(centerx=x + card_w // 2, top=y + 15)
            screen.blit(type_surf, type_r)

            pygame.draw.rect(screen, card["color"], (x + 20, y + 38, card_w - 40, 3))
            pygame.draw.circle(screen, card["color"], (x + card_w // 2, y + 130), 40)
            pygame.draw.circle(screen, WHITE, (x + card_w // 2, y + 130), 40, 2)

            name_surf = font_name.render(card["name"], True, WHITE)
            name_r = name_surf.get_rect(centerx=x + card_w // 2, top=y + 185)
            screen.blit(name_surf, name_r)

            level_text = f"{current_level} -> {next_level}"
            level_surf = font_type.render(level_text, True, (220, 220, 100))
            level_r = level_surf.get_rect(centerx=x + card_w // 2, top=y + 215)
            screen.blit(level_surf, level_r)

            words = card["desc"].split()
            lines = []
            current_line = ""
            for word in words:
                test = current_line + " " + word if current_line else word
                if font_desc.size(test)[0] < card_w - 20:
                    current_line = test
                else:
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)

            for j, line in enumerate(lines):
                desc_surf = font_desc.render(line, True, (180, 180, 180))
                desc_r = desc_surf.get_rect(centerx=x + card_w // 2, top=y + 240 + j * 28)
                screen.blit(desc_surf, desc_r)

    def handle_click(self, pos, player):
        if not self.visible:
            return False
        for i, rect in enumerate(self.card_rects):
            if rect.collidepoint(pos):
                self.apply(self.cards[i], player)
                self.visible = False
                return True
        return False

    def apply(self, card, player):
        name = card["name"]
        if card["type"] == "passive":
            player.passive_levels[name] = player.passive_levels.get(name, 0) + 1
        if name == "Speed Boost":
            player.speed *= 1.15
        elif name == "Damage Boost":
            player.damage_multiplier *= 1.20
        elif name == "Rapid Fire":
            for weapon in player.weapons:
                weapon.cooldown = int(weapon.cooldown * 0.85) if hasattr(weapon, 'cooldown') else None
        elif name == "Max Health":
            player.max_hp += 20
            player.hp = min(player.hp + 20, player.max_hp)
        elif name == "Vampirism":
            player.vampirism += 0.05
        elif name == "Armor":
            player.armor = min(player.armor + 0.10, 0.9)
        elif name == "Regeneration":
            player.regen_rate += 1
        elif name == "Magnet":
            player.pickup_radius *= 1.5
        elif name == "XP Boost":
            player.xp_multiplier *= 1.5
        elif name == "Knife":
            from weapons import Knife
            if not any(isinstance(w, Knife) for w in player.weapons):
                player.weapons.append(Knife())
            else:
                for w in player.weapons:
                    if isinstance(w, Knife):
                        w.level_up()
        elif name == "Magic Orb":
            from weapons import MagicOrb
            if not any(isinstance(w, MagicOrb) for w in player.weapons):
                player.weapons.append(MagicOrb())
            else:
                for w in player.weapons:
                    if isinstance(w, MagicOrb):
                        w.level_up()

        elif name == "Sand Spike":
            from weapons import SandSpike
            if not any(isinstance(w, SandSpike) for w in player.weapons):
                player.weapons.append(SandSpike())
            else:
                for w in player.weapons:
                    if isinstance(w, SandSpike):
                        w.level_up()

        elif name == "Boomerang":
            from weapons import Boomerang
            if not any(isinstance(w, Boomerang) for w in player.weapons):
                player.weapons.append(Boomerang())
            else:
                for w in player.weapons:
                    if isinstance(w, Boomerang):
                        w.level_up()