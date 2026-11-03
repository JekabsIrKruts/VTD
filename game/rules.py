"""Game data and simulation rules, independent from the Pygame user interface."""

import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450

# ROUTE AND WINDOW SETTINGS
PATH_1 = SCREEN_HEIGHT // 2
PATH_1_THICKNESS = 50
PATH_1_END_X = 500

PATH_2_THICKNESS = 50
PATH_2_END_X = 500
PATH_2_END_Y = 80

PATH_3_THICKNESS = 50
PATH_3_END_X = 200
PATH_3_END_Y = 80

PATH_4_THICKNESS = 50
PATH_4_END_X = 200
PATH_4_END_Y = 400

PATH_5_THICKNESS = 50
PATH_5_END_X = 830
PATH_5_END_Y = 400


# Each route entry stores an endpoint and the track width for that segment.
PATH_SEGMENTS = [
    (PATH_1_END_X - 25, PATH_1, PATH_1_THICKNESS),
    (PATH_2_END_X - 25, PATH_2_END_Y, PATH_2_THICKNESS),
    (PATH_3_END_X - 25, PATH_3_END_Y, PATH_3_THICKNESS),
    (PATH_4_END_X - 25, PATH_4_END_Y, PATH_4_THICKNESS),
    (PATH_5_END_X - 25, PATH_5_END_Y, PATH_5_THICKNESS),
]


# ENEMY AI SETTINGS: edit each type's movement, HP, exit damage, reward, and look.
ENEMY_TYPES = {
    "musas": {
        "radius": 14,
        "speed": 200,
        "damage": 20,
        "hp": 75,
        "wing_reward": 55,
        "color": (230, 55, 55)},

    "scorpion_musas": {
        "radius": 17,
        "speed": 250,
        "damage": 60,
        "hp": 130,
        "wing_reward": 110,
        "color": (184, 150, 15)},

    "stalk_eyed_musas": {
        "radius": 10,
        "speed": 350,
        "damage": 15,
        "hp": 40,
        "wing_reward": 60,
        "color": (140, 134, 17)},

    "bee_musas": {
        "radius": 15,
        "speed": 200,
        "damage": 30,
        "hp": 125,
        "wing_reward": 65,
        "color": (250, 238, 12)},

    "mydas_musas": {
        "radius": 25,
        "speed": 100,
        "damage": 150,
        "hp": 700,
        "wing_reward": 200,
        "color": (28, 7, 3)},

    "picture_winged_musas": {
        "radius": 17,
        "speed": 180,
        "damage": 40,
        "hp": 200,
        "wing_reward": 70,
        "color": (250, 246, 245)},

    "mama_musa": {
        "radius": 60,
        "speed": 50,
        "damage": 1000,
        "hp": 10000,
        "wing_reward": 1,
        "color": (112, 111, 105)},
}


# BASE FROG SETTINGS: edit attack stats, price, size, color, and projectile here.
TOWER_TYPES = {
    "hairy_frog": {
        "name": "Hairy Frog",
        "damage": 40,
        "attack_speed": 1.0,
        "range": 120,
        "size": 28,
        "price": 140,
        "color": (65, 180, 75),
        "projectile_speed": 600,
        "projectile_size": 6,
        "projectile_color": (110, 47, 5),
    },
    "flea toad": {
        "name": "Flea Toad",
        "damage": 16,
        "attack_speed": 2.5,
        "range": 155,
        "size": 23,
        "price": 160,
        "color": (35, 220, 110),
        "projectile_speed": 700,
        "projectile_size": 6,
        "projectile_color": (255, 90, 180),
    },
    "black rain frog": {
        "name": "Black Rain Frog",
        "damage": 80,
        "attack_speed": 0.5,
        "range": 240,
        "size": 34,
        "price": 250,
        "color": (30, 105, 45),
        "projectile_speed": 350,
        "projectile_size": 10,
        "projectile_color": (255, 90, 180),
    },
    "surinam horned frog": {
        "name": "Surinam Horned Frog",
        "damage": 180,
        "attack_speed": 0.3,
        "range": 600,
        "size": 40,
        "price": 700,
        "color": (100, 65, 30),
        "projectile_speed": 300,
        "projectile_size": 13,
        "projectile_color": (255, 90, 180),
    },
    "glass frog": {
        "name": "Glass Frog",
        "damage": 10,
        "attack_speed": 4.0,
        "range": 110,
        "size": 26,
        "price": 350,
        "color": (90, 200, 150),
        "projectile_speed": 800,
        "projectile_size": 5,
        "projectile_color": (255, 90, 180),
    }
}


# FROG UPGRADE SETTINGS: each tier stores its own stats, description, and price.
TOWER_T1_TYPES = {
    "hairy_frog": {
        "name": "Stronger hairs",
        "description": [
            "Damage: 40 -> 50",
            "Attack speed: 1.0 -> 1.3 shots/s",
            "Range: 120 -> 100",
        ],
        "damage": 50,
        "attack_speed": 1.3,
        "range": 100,
        "size": 30,
        "price": 200,
        "color": (55, 153, 64),
        "projectile_speed": 600,
        "projectile_size": 6,
        "projectile_color": (110, 47, 5),
    },
    "flea toad": {
        "name": "Even Smaller",
        "description": [
            "Damage: 16 -> 15",
            "Attack speed: 2.5 -> 3.2 shots/s",
            "Range: 155 -> 130",
            "Frog size: 23 -> 19",
            "Projectile size: 6 -> 4",
        ],
        "damage": 15,
        "attack_speed": 3.2,
        "range": 130,
        "size": 19,
        "price": 175,
        "color": (30, 187, 94),
        "projectile_speed": 700,
        "projectile_size": 4,
        "projectile_color": (255, 90, 180),
    },
    "black rain frog": {
        "name": "Heavy Hitter",
        "description": [
            "Damage: 80 -> 110",
            "Attack speed: 0.5 -> 0.4 shots/s",
            "Range: 240 -> 280",
            "Frog size: 34 -> 37",
            "Projectile speed: 350 -> 320",
            "Projectile size: 10 -> 13",
        ],
        "damage": 110,
        "attack_speed": 0.4,
        "range": 280,
        "size": 37,
        "price": 340,
        "color": (26, 89, 38),
        "projectile_speed": 320,
        "projectile_size": 13,
        "projectile_color": (255, 90, 180),
    },
    "surinam horned frog": {
        "name": "Spikier Spikes",
        "description": [
            "Damage: 180 -> 210",
            "Attack speed: 0.3 -> 0.4 shots/s",
            "Range: 600 -> 650",
            "Frog size: 40 -> 44",
            "Projectile speed: 300 -> 600",
            "Projectile size: 13 -> 15",
        ],
        "damage": 210,
        "attack_speed": 0.4,
        "range": 650,
        "size": 44,
        "price": 700,
        "color": (85, 55, 26),
        "projectile_speed": 600,
        "projectile_size": 15,
        "projectile_color": (0, 23, 1),
    },
    "glass frog": {
        "name": "Clearer Glass",
        "description": [
            "Attack speed: 4 -> 5 shots/s",
            "Range: 110 -> 130",
            "Frog size: 26 -> 29",
        ],
        "damage": 10,
        "attack_speed": 5.0,
        "range": 130,
        "size": 29,
        "price": 450,
        "color": (77, 170, 128),
        "projectile_speed": 800,
        "projectile_size": 5,
        "projectile_color": (227, 255, 227),
    },
}

TOWER_T2_TYPES = {
    "hairy_frog": {
        "name": "Master of the Hairs",
        "description": [
            "Damage: 50 -> 80",
            "Attack speed: 1.3 -> 1.6 shots/s",
            "Range: 100 -> 80",
            "Projectile size: 6 -> 7",
        ],
        "damage": 80,
        "attack_speed": 1.6,
        "range": 80,
        "size": 30,
        "price": 300,
        "color": (46, 126, 53),
        "projectile_speed": 600,
        "projectile_size": 7,
        "projectile_color": (110, 47, 5),
    },
    "flea toad": {
        "name": "Microscopically Small",
        "description": [
            "Damage: 15 -> 18",
            "Attack speed: 3.2 -> 3.8 shots/s",
            "Range: 130 -> 120",
            "Frog size: 19 -> 15",
            "Projectile size: 4 -> 3",
        ],
        "damage": 16,
        "attack_speed": 3.8,
        "range": 120,
        "size": 15,
        "price": 400,
        "color": (25, 154, 77),
        "projectile_speed": 700,
        "projectile_size": 3,
        "projectile_color": (255, 90, 180),
    },
    "black rain frog": {
        "name": "The Rain is Coming",
        "description": [
            "Damage: 110 -> 140",
            "Range: 280 -> 310",
            "Frog size: 37 -> 40",
            "Projectile size: 13 -> 10",
            "Projectile color changes",
        ],
        "damage": 140,
        "attack_speed": 0.4,
        "range": 310,
        "size": 40,
        "price": 500,
        "color": (21, 74, 32),
        "projectile_speed": 350,
        "projectile_size": 10,
        "projectile_color": (33, 0, 18),
    },
    "surinam horned frog": {
        "name": "Speedy Spikes",
        "description": [
            "Damage: 210 -> 220",
            "Attack speed: 0.4 -> 0.5 shots/s",
            "Projectile speed: 600 -> 800",
            "Projectile size: 15 -> 16",
        ],
        "damage": 220,
        "attack_speed": 0.5,
        "range": 650,
        "size": 44,
        "price": 400,
        "color": (85, 55, 26),
        "projectile_speed": 800,
        "projectile_size": 16,
        "projectile_color": (0, 23, 1),
    },
    "glass frog": {
        "name": "Glisterring Glossy Glass",
        "description": [
            "Damage: 10 -> 12",
            "Attack speed: 5 -> 6.5 shots/s",
            "Range: 130 -> 160",
            "Projectile speed: 800 -> 900",
            "Frog size: 29 -> 31",
        ],
        "damage": 12,
        "attack_speed": 6.5,
        "range": 160,
        "size": 31,
        "price": 610,
        "color": (77, 170, 128),
        "projectile_speed": 900,
        "projectile_size": 5,
        "projectile_color": (227, 255, 227),
    },
}

TOWER_T3_TYPES = {
    "hairy_frog": {
        "name": "Herald of the Hairs",
        "description": [
            "Damage: 80 -> 140",
            "Attack speed: 1.6 -> 2 shots/s",
            "Range: 80 -> 70",
            "Frog size: 30 -> 34",
            "Projectile speed: 600 -> 1000",
            "Projectile size: 7 -> 12",
            "Aura: 50% slow + 20 damage/s in range",
        ],
        "damage": 140,
        "attack_speed": 2.0,
        "range": 70,
        "size": 34,
        "price": 1400,
        "color": (46, 126, 53),
        "projectile_speed": 1000,
        "projectile_size": 12,
        "projectile_color": (110, 47, 5),
        "zone_damage_per_second": 20.0,
        "zone_slow_multiplier": 0.5,
        "zone_color": (130, 74, 35),
        "zone_alpha": 75,
        "special_effect": "hair_zone",
    },
    "flea toad": {
        "name": "Giant Killer",
        "description": [
            "Damage: 16 -> 22",
            "Attack speed: 3.8 -> 4.5 shots/s",
            "Frog size: 15 -> 12",
            "Bonus: each hit adds damage equal to 1.5% of target max HP",
        ],
        "damage": 22,
        "attack_speed": 4.5,
        "range": 120,
        "size": 12,
        "price": 1100,
        "color": (25, 154, 77),
        "projectile_speed": 700,
        "projectile_size": 3,
        "projectile_color": (255, 90, 180),
        "bonus_max_hp_damage_percent": 0.015,
        "special_effect": "max_hp_bonus_damage",
    },
    "black rain frog": {
        "name": "Notorious F.R.O.G.",
        "description": [
            "Damage: 140 -> 200",
            "Attack speed: 0.4 -> 0.45 shots/s",
            "Range: 310 -> 400",
            "Frog size: 40 -> 53",
            "Projectile size: 10 -> 21",
            "Effect: bounces to 6 more enemies, full damage each",
        ],
        "damage": 200,
        "attack_speed": 0.45,
        "range": 400,
        "size": 53,
        "price": 830,
        "color": (21, 74, 32),
        "projectile_speed": 350,
        "projectile_size": 21,
        "projectile_color": (33, 0, 18),
        "bounce_targets": 6,
        "special_effect": "bouncing_boulder",
    },
    "surinam horned frog": {
        "name": "Pointy Missiles",
        "description": [
            "Damage: 220 -> 420",
            "Attack speed: 0.5 -> 2 shots/s",
            "Range: 650 -> 750",
            "Frog size: 44 -> 50",
            "Projectile speed: 800 -> 850",
            "Effect: 2 other enemies within 100 take 50% damage",
        ],
        "damage": 420,
        "attack_speed": 2.0,
        "range": 750,
        "size": 50,
        "price": 2000,
        "color": (85, 55, 26),
        "projectile_speed": 850,
        "projectile_size": 16,
        "projectile_color": (0, 23, 1),
        "explosion_radius": 100,
        "explosion_targets": 2,
        "explosion_damage_multiplier": 0.5,
        "special_effect": "homing_splash_missile",
    },
    "glass frog": {
        "name": "Invisifrog",
        "description": [
            "Damage: 12 -> 15",
            "Attack speed: 6.5 -> 7 shots/s",
            "Range: 160 -> 200",
            "Effect: stuns target for 0.1 seconds",
        ],
        "damage": 15,
        "attack_speed": 7.0,
        "range": 200,
        "size": 31,
        "price": 1650,
        "color": (77, 170, 128),
        "projectile_speed": 900,
        "projectile_size": 4,
        "projectile_color": (227, 255, 227),
        "stun_duration": 0.1,
        "special_effect": "stun",
    },
}

TOWER_UPGRADE_TIERS = [TOWER_TYPES, TOWER_T1_TYPES, TOWER_T2_TYPES, TOWER_T3_TYPES]

# WAVE SCHEDULE: edit enemy keys, counts, and spawn delays for each wave.
WAVES = [
    {"enemies": [("musas", 10)], "spawn_interval": 0.7},
    {"enemies": [("musas", 8), ("bee_musas", 6)], "spawn_interval": 0.6},
    {"enemies": [("musas", 3), ("bee_musas", 3), ("musas", 3), ("bee_musas", 3), ("musas", 3), ("bee_musas", 3), ("musas", 3), ("bee_musas", 3), ("musas", 3), ("bee_musas", 3), ("musas", 3), ("bee_musas", 3), ("musas", 3), ("bee_musas", 3), ], "spawn_interval": 0.1},
    {"enemies": [("stalk_eyed_musas", 12)], "spawn_interval": 0.8},
    {"enemies": [("bee_musas", 10), ("stalk_eyed_musas", 5), ("bee_musas", 10), ("stalk_eyed_musas", 5), ("bee_musas", 10), ("stalk_eyed_musas", 5), ], "spawn_interval": 0.5},
    {"enemies": [("bee_musas", 15), ("picture_winged_musas", 3), ("bee_musas", 15)], "spawn_interval": 0.3},
    {"enemies": [("scorpion_musas", 20)], "spawn_interval": 0.15},
    {"enemies": [("mydas_musas", 5), ("scorpion_musas", 15)], "spawn_interval": 0.3},
    {"enemies": [("mydas_musas", 6), ("picture_winged_musas", 20), ("stalk_eyed_musas", 30)], "spawn_interval": 0.1},
    {"enemies": [("mama_musa", 1)], "spawn_interval": 0.35},
]


# GLOBAL GAME BALANCE: colors, scores, player HP, and defeated-enemy fade time.
GRASS_GREEN = (30, 112, 57)
ROAD_BLUE = (112, 148, 190)
ROUND_SCORE_MAX = 10_000
ROUND_SCORE_DECAY_PER_SECOND = 1_000
PLAYER_MAX_HP = 1_000
DEFEATED_ENEMY_FADE_SECONDS = 0.5


# CURRENCY SETTINGS: wings pay for frogs/upgrades and HP trades.
STARTING_WINGS = 1000
WINGS_PER_HP = 1

# QUIZ CONTENT: edit prompts and answers; `correct` is an answer index from 0 to 2.
FROG_QUESTIONS = [
    {
        "question": "Placeholder frog question 1",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder frog question 2",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder frog question 3",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder frog question 4",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder frog question 5",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder frog question 6",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder frog question 7",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder frog question 8",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder frog question 9",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder frog question 10",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder frog question 11",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder frog question 12",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder frog question 13",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder frog question 14",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder frog question 15",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
]
FLY_QUESTIONS = [
    {
        "question": "Placeholder fly question 1",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder fly question 2",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder fly question 3",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder fly question 4",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder fly question 5",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder fly question 6",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder fly question 7",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder fly question 8",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder fly question 9",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
    {
        "question": "Placeholder fly question 10",
        "answers": ["wrong answer", "wrong answer", "correct answer"],
        "correct": 2,
    },
]


class Game:
    """Store match state and apply game rules without drawing the screen."""

    def __init__(self):
        """Build route geometry and initialize a new match."""
        self.route_segments = []
        self.total_path_length = 0.0
        start = (0.0, float(PATH_1))
        for end_x, end_y, _width in PATH_SEGMENTS:
            end = (float(end_x), float(end_y))
            length = math.hypot(end[0] - start[0], end[1] - start[1])
            self.route_segments.append((start, end, length))
            self.total_path_length += length
            start = end

        self.track_segments = [
            ((0.0, float(PATH_1)), (float(PATH_1_END_X), float(PATH_1)), PATH_1_THICKNESS)
        ]
        start = (float(PATH_1_END_X - 25), float(PATH_1))
        for end_x, end_y, width in PATH_SEGMENTS[1:]:
            end = (float(end_x), float(end_y))
            self.track_segments.append((start, end, width))
            start = end

        self.enemies = []
        self.defeated_enemies = []
        self.current_wave = 0
        self.wave_enemy_queue = []
        self.spawn_timer = 0.0
        self.total_score = 0
        self.wings = STARTING_WINGS
        self.player_hp = PLAYER_MAX_HP
        self.round_score = ROUND_SCORE_MAX
        self.wave_active = False
        self.planning_phase = False
        self.round_timer_started = False
        self.round_speed_multiplier = 1.0
        self.round_clear_bonus = 0
        self.next_frog_question = 0
        self.next_fly_question = 0
        self.fly_question_next_round = False
        self.towers = []
        self.projectiles = []
        self.effects = []
        self.mama_frog_blessing = False
        self.mama_offer_completed = False
        self.game_over = False
        self.game_finished = False

    def enemy_position(self, enemy):
        """Map an enemy's distance along the route to its screen coordinate."""
        distance = enemy["distance"]
        position = self.route_segments[-1][1]
        for start, end, length in self.route_segments:
            if distance <= length:
                progress = distance / length if length else 1.0
                return (
                    start[0] + (end[0] - start[0]) * progress,
                    start[1] + (end[1] - start[1]) * progress,
                )
            distance -= length
        return position

    def needs_round_question(self):
        """Return whether the next wave needs its quiz before planning begins."""
        return (
            not self.game_over
            and not self.game_finished
            and not self.wave_active
            and not self.planning_phase
            and not self.enemies
            and not self.defeated_enemies
            and not self.wave_enemy_queue
            and self.current_wave < len(WAVES)
        )

    @property
    def wave_count(self):
        """Return the number of waves in the configured schedule."""
        return len(WAVES)

    def mama_offer_is_due(self):
        """Return whether the Varžu māte offer is waiting before wave six."""
        return self.current_wave == 5 and not self.mama_offer_completed

    def next_wave_summary(self):
        """Group the next wave's queued enemies by type for the preview popup."""
        if self.current_wave >= len(WAVES):
            return []
        counts = {}
        for enemy_type, amount in WAVES[self.current_wave]["enemies"]:
            counts[enemy_type] = counts.get(enemy_type, 0) + amount
        return list(counts.items())

    def next_question(self):
        """Return the next quiz, its topic, and whether skipping is allowed."""
        if self.fly_question_next_round:
            question = FLY_QUESTIONS[self.next_fly_question]
            self.next_fly_question += 1
            self.fly_question_next_round = False
            return question, "Fly question", False
        question = FROG_QUESTIONS[self.next_frog_question]
        self.next_frog_question += 1
        return question, "Frog question", True

    def resolve_question(self, result, is_fly_question):
        """Apply quiz points, wave speed changes, clear bonuses, and planning state."""
        self.round_speed_multiplier = 1.0
        self.round_clear_bonus = 0
        if result == "correct":
            self.total_score += 6_000 if is_fly_question else 2_000
        elif result == "incorrect":
            if is_fly_question:
                self.round_speed_multiplier = 2.0
                self.round_clear_bonus = 3_000
            else:
                self.round_speed_multiplier = 1.5
                self.round_clear_bonus = 1_000
        elif result == "skip":
            self.fly_question_next_round = True
        self.planning_phase = True

    def apply_mama_frog_offer(self, action, amount=0):
        """Apply an HP trade, full-health blessing, or continue choice."""
        if action == "blessing":
            if self.player_hp != PLAYER_MAX_HP:
                return 0
            self.player_hp = 1
            self.mama_frog_blessing = True
            self.mama_offer_completed = True
        elif action == "trade":
            amount = max(0, min(int(amount), self.player_hp - 1))
            self.player_hp -= amount
            self.wings += amount * WINGS_PER_HP
            self.mama_offer_completed = True
            return amount * WINGS_PER_HP
        elif action == "continue":
            self.mama_offer_completed = True
        return 0

    def start_next_wave(self):
        """Queue the configured wave and switch from planning to active play."""
        if not self.planning_phase or self.current_wave >= len(WAVES):
            return False
        wave = WAVES[self.current_wave]
        self.wave_enemy_queue = [
            enemy_type
            for enemy_type, count in wave["enemies"]
            for _ in range(count)
        ]
        self.spawn_timer = 0.0
        self.current_wave += 1
        self.round_score = ROUND_SCORE_MAX
        self.wave_active = True
        self.round_timer_started = False
        self.planning_phase = False
        return True

    def destroy_all_enemies(self):
        """Clear active, fading, and queued enemies for the debug button."""
        self.enemies.clear()
        self.defeated_enemies.clear()
        self.wave_enemy_queue.clear()

    def enemy_is_present(self, enemy):
        """Check whether a live enemy or fading body can still receive a projectile."""
        return any(current is enemy for current in self.enemies) or any(
            current is enemy for current in self.defeated_enemies
        )

    def tower_data(self, tower):
        """Return the stat dictionary for a placed frog's current upgrade tier."""
        return TOWER_UPGRADE_TIERS[tower["upgrade_tier"]][tower["type"]]

    def damage_enemy(self, enemy, damage):
        """Damage a live enemy and start its fade/reward when HP reaches zero."""
        if not any(live_enemy is enemy for live_enemy in self.enemies):
            return
        enemy["hp"] -= damage
        if enemy["hp"] <= 0:
            self.wings += ENEMY_TYPES[enemy["type"]]["wing_reward"]
            self.enemies[:] = [live_enemy for live_enemy in self.enemies if live_enemy is not enemy]
            enemy["hp"] = 0
            enemy["fade_duration"] = DEFEATED_ENEMY_FADE_SECONDS
            enemy["fade_remaining"] = DEFEATED_ENEMY_FADE_SECONDS
            self.defeated_enemies.append(enemy)

    def next_upgrade_data(self, tower):
        """Return the next tier's editable data, or None when fully upgraded."""
        next_tier = tower["upgrade_tier"] + 1
        if next_tier >= len(TOWER_UPGRADE_TIERS):
            return None
        return TOWER_UPGRADE_TIERS[next_tier][tower["type"]]

    def upgrade_tower(self, tower_index):
        """Spend wings to upgrade one placed frog by one tier."""
        if not 0 <= tower_index < len(self.towers):
            return False
        tower = self.towers[tower_index]
        upgrade = self.next_upgrade_data(tower)
        if upgrade is None or self.wings < upgrade["price"]:
            return False
        self.wings -= upgrade["price"]
        tower["upgrade_tier"] += 1
        return True

    def can_place_tower(self, center, tower_type, forbidden_rects=()):
        """Check board bounds, track overlap, UI zones, and frog collisions."""
        data = TOWER_TYPES[tower_type]
        size = data["size"]
        half = size / 2
        half_diagonal = half * math.sqrt(2)
        x, y = center
        if x - half < 0 or x + half > SCREEN_WIDTH or y - half < 55 or y + half > SCREEN_HEIGHT:
            return False
        candidate = (x - half, y - half, size, size)
        for fx, fy, fw, fh in forbidden_rects:
            if candidate[0] < fx + fw and candidate[0] + size > fx and candidate[1] < fy + fh and candidate[1] + size > fy:
                return False
        for start, end, road_width in self.track_segments:
            if point_to_segment_distance(center, start, end) <= half_diagonal + road_width / 2:
                return False
        for tower in self.towers:
            other_size = self.tower_data(tower)["size"]
            if abs(x - tower["x"]) < half + other_size / 2 and abs(y - tower["y"]) < half + other_size / 2:
                return False
        return True

    def place_tower(self, center, tower_type, forbidden_rects=()):
        """Spend wings and place a base frog when the position is valid."""
        data = TOWER_TYPES[tower_type]
        if self.wings < data["price"] or not self.can_place_tower(center, tower_type, forbidden_rects):
            return False
        self.wings -= data["price"]
        self.towers.append({"type": tower_type, "upgrade_tier": 0, "x": center[0], "y": center[1], "attack_cooldown": 0.0})
        return True

    def update(self, dt):
        """Advance fades, spawning, enemy AI, frog attacks, projectiles, and scoring."""
        for enemy in self.defeated_enemies[:]:
            enemy["fade_remaining"] -= dt
            if enemy["fade_remaining"] <= 0:
                self.defeated_enemies.remove(enemy)
        for effect in self.effects[:]:
            effect["remaining"] -= dt
            if effect["remaining"] <= 0:
                self.effects.remove(effect)
        if not self.wave_active or self.game_over or self.game_finished:
            return

        if not self.wave_enemy_queue and self.enemies:
            self.round_timer_started = True
        if self.round_timer_started:
            self.round_score = max(0, self.round_score - ROUND_SCORE_DECAY_PER_SECOND * dt)

        if self.wave_enemy_queue:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                enemy_type = self.wave_enemy_queue.pop(0)
                base_hp = ENEMY_TYPES[enemy_type]["hp"]
                multiplier = 0.9 if self.mama_frog_blessing else 1.0
                max_hp = max(1, round(base_hp * multiplier))
                self.enemies.append({
                    "type": enemy_type,
                    "distance": 0.0,
                    "hp": max_hp,
                    "max_hp": max_hp,
                    "stun_remaining": 0.0,
                })
                self.spawn_timer = WAVES[self.current_wave - 1]["spawn_interval"]

        # ENEMY AI: apply aura damage/slow, stun timers, route movement, and exit damage.
        for enemy in self.enemies[:]:
            data = ENEMY_TYPES[enemy["type"]]
            enemy_x, enemy_y = self.enemy_position(enemy)
            slow_multiplier = 1.0
            zone_damage_per_second = 0.0
            for tower in self.towers:
                tower_data = self.tower_data(tower)
                if "zone_damage_per_second" not in tower_data:
                    continue
                distance = math.hypot(tower["x"] - enemy_x, tower["y"] - enemy_y)
                if distance <= tower_data["range"]:
                    slow_multiplier = min(
                        slow_multiplier,
                        tower_data["zone_slow_multiplier"],
                    )
                    zone_damage_per_second += tower_data["zone_damage_per_second"]

            if zone_damage_per_second:
                self.damage_enemy(enemy, zone_damage_per_second * dt)
                if not any(live_enemy is enemy for live_enemy in self.enemies):
                    continue

            if enemy.get("stun_remaining", 0.0) > 0:
                enemy["stun_remaining"] = max(0.0, enemy["stun_remaining"] - dt)
            else:
                enemy["distance"] = min(
                    enemy["distance"]
                    + data["speed"]
                    * self.round_speed_multiplier
                    * slow_multiplier
                    * dt,
                    self.total_path_length,
                )
            if enemy["distance"] >= self.total_path_length:
                self.player_hp -= data["damage"]
                self.enemies.remove(enemy)
                if self.player_hp <= 0:
                    self.game_over = True
                    self.enemies.clear()
                    self.defeated_enemies.clear()
                    self.wave_enemy_queue.clear()
                    self.projectiles.clear()
                    self.wave_active = False
                    return

        # FROG TARGETING: aim at the furthest-along live enemy inside attack range.
        for tower in self.towers:
            data = self.tower_data(tower)
            tower["attack_cooldown"] = max(0.0, tower["attack_cooldown"] - dt)
            if tower["attack_cooldown"] > 0:
                continue
            in_range = []
            for enemy in self.enemies:
                ex, ey = self.enemy_position(enemy)
                if math.hypot(tower["x"] - ex, tower["y"] - ey) <= data["range"]:
                    in_range.append(enemy)
            if in_range:
                target = max(in_range, key=lambda item: item["distance"])
                self.projectiles.append({
                    "x": tower["x"], "y": tower["y"], "target": target,
                    "damage": data["damage"], "speed": data["projectile_speed"],
                    "size": data["projectile_size"], "color": data["projectile_color"],
                    "bonus_max_hp_damage_percent": data.get("bonus_max_hp_damage_percent", 0.0),
                    "stun_duration": data.get("stun_duration", 0.0),
                    "bounce_targets_remaining": data.get("bounce_targets", 0),
                    "bounce_range": data.get("range", 0),
                    "hit_targets": [target],
                    "origin_x": tower["x"],
                    "origin_y": tower["y"],
                    "explosion_radius": data.get("explosion_radius", 0),
                    "explosion_targets": data.get("explosion_targets", 0),
                    "explosion_damage_multiplier": data.get("explosion_damage_multiplier", 0.0),
                })
                tower["attack_cooldown"] = 1 / data["attack_speed"]

        # PROJECTILE AI: move, hit, apply special effects, bounce, or remove each shot.
        for projectile in self.projectiles[:]:
            target = projectile["target"]
            if not self.enemy_is_present(target):
                self.projectiles.remove(projectile)
                continue
            tx, ty = self.enemy_position(target)
            dx, dy = tx - projectile["x"], ty - projectile["y"]
            distance = math.hypot(dx, dy)
            travel = projectile["speed"] * dt
            if distance <= travel or distance == 0:
                extra_damage = target["max_hp"] * projectile["bonus_max_hp_damage_percent"]
                self.damage_enemy(target, projectile["damage"] + extra_damage)
                if projectile["stun_duration"] > 0:
                    if any(enemy is target for enemy in self.enemies):
                        target["stun_remaining"] = max(
                            target.get("stun_remaining", 0.0),
                            projectile["stun_duration"],
                        )

                if projectile["explosion_radius"] > 0:
                    self.effects.append({
                        "x": tx,
                        "y": ty,
                        "radius": projectile["explosion_radius"],
                        "color": (255, 190, 75),
                        "duration": 0.18,
                        "remaining": 0.18,
                    })
                    splash_targets = []
                    for enemy in self.enemies:
                        if enemy is target:
                            continue
                        ex, ey = self.enemy_position(enemy)
                        splash_distance = math.hypot(ex - tx, ey - ty)
                        if splash_distance <= projectile["explosion_radius"]:
                            splash_targets.append((splash_distance, enemy))
                    splash_targets.sort(key=lambda entry: entry[0])
                    for _distance, enemy in splash_targets[:projectile["explosion_targets"]]:
                        self.damage_enemy(
                            enemy,
                            projectile["damage"]
                            * projectile["explosion_damage_multiplier"],
                        )

                if projectile["bounce_targets_remaining"] > 0:
                    projectile["hit_targets"].append(target)
                    next_targets = []
                    for enemy in self.enemies:
                        if any(enemy is hit_target for hit_target in projectile["hit_targets"]):
                            continue
                        ex, ey = self.enemy_position(enemy)
                        if math.hypot(
                            ex - projectile["origin_x"],
                            ey - projectile["origin_y"],
                        ) <= projectile["bounce_range"]:
                            next_targets.append((math.hypot(ex - tx, ey - ty), enemy))
                    if next_targets:
                        next_targets.sort(key=lambda entry: entry[0])
                        projectile["x"], projectile["y"] = tx, ty
                        projectile["target"] = next_targets[0][1]
                        projectile["bounce_targets_remaining"] -= 1
                        continue

                self.projectiles.remove(projectile)
            else:
                projectile["x"] += dx / distance * travel
                projectile["y"] += dy / distance * travel

        # SCORE TIMER: stop point decay once no queued or live enemies remain.
        if not self.wave_enemy_queue and not self.enemies:
            self.round_timer_started = False

        # WAVE COMPLETION: wait for enemies, fade-outs, and projectiles to clear.
        if (
            self.wave_active
            and not self.wave_enemy_queue
            and not self.enemies
            and not self.defeated_enemies
            and not self.projectiles
        ):
            self.total_score += round(self.round_score) + self.round_clear_bonus
            self.wave_active = False
            if self.current_wave >= len(WAVES):
                self.game_finished = True


def point_to_segment_distance(point, start, end):
    """Return the shortest distance from a point to a finite route segment."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length_squared = dx * dx + dy * dy
    if length_squared == 0:
        return math.hypot(point[0] - start[0], point[1] - start[1])
    progress = ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / length_squared
    progress = max(0.0, min(1.0, progress))
    nearest = (start[0] + progress * dx, start[1] + progress * dy)
    return math.hypot(point[0] - nearest[0], point[1] - nearest[1])
