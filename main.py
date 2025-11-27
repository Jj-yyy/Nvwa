import pygame
import random
import sys
import os
from PIL import Image, ImageSequence

pygame.init()

screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h

WINDOW_WIDTH = SCREEN_WIDTH
WINDOW_HEIGHT = SCREEN_HEIGHT
FPS = 60
MAX_ROUNDS = 5
DICE_ANIMATION_FRAMES = 30

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
BLUE = (50, 100, 200)
YELLOW = (220, 200, 50)
LIGHT_BLUE = (173, 216, 230)
ORANGE = (255, 165, 0)
TEXT_COLOR = (208, 107, 55)  # #D06B37

pygame.font.init()

try:

    TITLE_FONT = pygame.font.SysFont('microsoftyahei', 56, bold=True)
    EVENT_FONT = pygame.font.SysFont('microsoftyahei', 40, bold=True)
    TEXT_FONT = pygame.font.SysFont('microsoftyahei', 32, bold=True)
    SMALL_FONT = pygame.font.SysFont('microsoftyahei', 28, bold=True)
    TINY_FONT = pygame.font.SysFont('microsoftyahei', 24, bold=True)
except:

    try:
        TITLE_FONT = pygame.font.SysFont('simsun', 56, bold=True)
        EVENT_FONT = pygame.font.SysFont('simsun', 40, bold=True)
        TEXT_FONT = pygame.font.SysFont('simsun', 32, bold=True)
        SMALL_FONT = pygame.font.SysFont('simsun', 28, bold=True)
        TINY_FONT = pygame.font.SysFont('simsun', 24, bold=True)
    except:

        TITLE_FONT = pygame.font.Font(None, 56)
        TITLE_FONT.set_bold(True)
        EVENT_FONT = pygame.font.Font(None, 40)
        EVENT_FONT.set_bold(True)
        TEXT_FONT = pygame.font.Font(None, 32)
        TEXT_FONT.set_bold(True)
        SMALL_FONT = pygame.font.Font(None, 28)
        SMALL_FONT.set_bold(True)
        TINY_FONT = pygame.font.Font(None, 24)
        TINY_FONT.set_bold(True)

class Race:

    def __init__(self):
        self.population = 5
        self.food = 0
        self.defense = 0
        self.tech = 0
        self.round = 1

    def is_alive(self):
        return self.population > 0

class RandomEvent:

    def __init__(self, name, gif_frames, population_change, description=""):
        self.name = name
        self.gif_frames = gif_frames
        self.population_change = population_change
        self.description = description
        self.current_frame = 0
        self.frame_counter = 0
        self.frame_delay = 3

class Game:

    def __init__(self):

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Short-Lived Race Simulator")
        self.clock = pygame.time.Clock()
        self.race = Race()
        self.game_over = False
        self.game_started = False

        self.state = "START"

        self.dice_images = self.load_dice_images()
        self.dice_animating = False
        self.dice_animation_frame = 0
        self.dice_result = 1
        self.resource_points = 0

        self.current_event = None
        self.event_log = []

        self.ui_images = self.load_ui_images()
        self.event_gifs = self.load_event_gifs()
        self.ending_images = self.load_ending_images()
        self.ending_type = None

        self.background_image = self.load_background_image()

        self.random_events = self.create_random_events()

    def load_dice_images(self):

        dice_images = []
        for i in range(1, 7):
            try:
                img_path = os.path.join("static", "骰子", f"{i}.png")
                img = pygame.image.load(img_path)

                img = pygame.transform.scale(img, (200, 200))
                dice_images.append(img)
            except Exception as e:
                print(f"Failed to load dice image {i}.png: {e}")

                placeholder = pygame.Surface((200, 200))
                placeholder.fill(WHITE)
                pygame.draw.rect(placeholder, BLACK, (0, 0, 200, 200), 3)
                font = pygame.font.Font(None, 100)
                text = font.render(str(i), True, TEXT_COLOR)
                placeholder.blit(text, (75, 50))
                dice_images.append(placeholder)
        return dice_images

    def load_ui_images(self):

        ui_images = {}
        ui_files = {
            'title': '标题.png',
            'start_button': '开始按钮.png',
            'text_box': '文字框.png',
            'option_h': '选项框（横板）.png',
            'option_v': '选项框（竖版）.png'
        }
        for key, filename in ui_files.items():
            try:
                img_path = os.path.join("static", "UI", filename)
                img = pygame.image.load(img_path)
                ui_images[key] = img
            except Exception as e:
                print(f"Failed to load UI image {filename}: {e}")
                ui_images[key] = None
        return ui_images

    def load_event_gifs(self):

        event_gifs = {}
        event_files = {
            'drought': '干旱.gif',
            'harvest': '丰收.gif',
            'winter': '寒冬.gif',
            'flood': '洪水.gif',
            'fertile_land': '发现沃土.gif'
        }
        for key, filename in event_files.items():
            try:
                img_path = os.path.join("static", "随机事件gif", filename)

                pil_image = Image.open(img_path)
                frames = []

                for frame in ImageSequence.Iterator(pil_image):

                    frame = frame.convert('RGBA')

                    frame_str = frame.tobytes()
                    frame_surface = pygame.image.fromstring(frame_str, frame.size, 'RGBA')

                    frame_surface = pygame.transform.scale(frame_surface, (400, 300))
                    frames.append(frame_surface)

                event_gifs[key] = frames
                print(f"Successfully loaded {filename}, {len(frames)} frames")
            except Exception as e:
                print(f"Failed to load event image {filename}: {e}")

                placeholder = pygame.Surface((400, 300))
                placeholder.fill(LIGHT_BLUE)
                pygame.draw.rect(placeholder, BLACK, (0, 0, 400, 300), 3)
                text = SMALL_FONT.render(key, True, TEXT_COLOR)
                placeholder.blit(text, (200 - text.get_width()//2, 140))
                event_gifs[key] = [placeholder]
        return event_gifs

    def load_ending_images(self):

        ending_images = {}
        ending_files = {
            'extinction': '种族灭绝.png',
            'primitive': '原始永恒.png',
            'prosperous': '人口繁盛.png',
            'agricultural': '农耕时代.png',
            'scientific': '科学革命.png',
            'utopia': '乌托邦.png',
            'ai_crisis': '智能危机.png',
            'population_overload': '人口过载.png'
        }
        for key, filename in ending_files.items():
            try:
                img_path = os.path.join("static", "游戏结局png", filename)
                img = pygame.image.load(img_path)
                img = pygame.transform.scale(img, (800, 500))
                ending_images[key] = img
            except Exception as e:
                print(f"Failed to load ending image {filename}: {e}")

                placeholder = pygame.Surface((800, 500))
                placeholder.fill(DARK_GRAY)
                pygame.draw.rect(placeholder, BLACK, (0, 0, 800, 500), 3)
                text = EVENT_FONT.render(key, True, WHITE)
                placeholder.blit(text, (400 - text.get_width()//2, 240))
                ending_images[key] = placeholder
        return ending_images

    def load_background_image(self):

        try:
            img_path = os.path.join("static", "游戏结局png", "原始永恒.png")
            img = pygame.image.load(img_path)

            img = pygame.transform.scale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
            print("Successfully loaded background image: 原始永恒.png")
            return img
        except Exception as e:
            print(f"Failed to load background image: {e}")

            background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            background.fill(WHITE)
            return background

    def create_random_events(self):

        events = [
            RandomEvent("Drought", self.event_gifs.get('drought'), -1,
                       "Severe drought strikes the land,\nwithering crops and drying wells"),
            RandomEvent("Harvest", self.event_gifs.get('harvest'), 2,
                       "Abundant harvest brings prosperity,\nfood stores overflow with plenty"),
            RandomEvent("Winter", self.event_gifs.get('winter'), -1,
                       "Harsh winter descends upon the land,\nfreezing temperatures take their toll"),
            RandomEvent("Flooding", self.event_gifs.get('flood'), -2,
                       "Heavy rain triggers flooding,\nsubmerging habitats"),
            RandomEvent("Fertile Land", self.event_gifs.get('fertile_land'), 2,
                       "Discovery of fertile new lands,\nexpanding territory and resources")
        ]
        return events

    def determine_ending(self):

        x = self.race.population
        food = self.race.food
        defense = self.race.defense
        tech = self.race.tech

        if x == 0:
            return 'extinction'

        if 0 < x <= 7:
            return 'primitive'

        if 7 < x <= 10:

            if food >= 8 and tech >= 5:
                return 'agricultural'

            if food >= 10 and 3 <= defense < 5 and tech >= 8:
                return 'scientific'

            if food >= 10 and tech >= 10:
                return 'utopia'

            return 'prosperous'

        if x >= 10:
            # 智能危机: 粮食≥8 且 防御≥25 且 科技≥10
            if food >= 8 and defense >= 25 and tech >= 10:
                return 'ai_crisis'
            # 人口过载: 仅人口≥10
            return 'population_overload'

        return 'prosperous'

    def start_game(self):

        self.game_started = True
        self.state = "DICE_READY"

    def start_dice_animation(self):

        self.dice_animating = True
        self.dice_animation_frame = 0
        self.dice_result = random.randint(1, 6)

    def update_dice_animation(self):

        if self.dice_animating:
            self.dice_animation_frame += 1
            if self.dice_animation_frame >= DICE_ANIMATION_FRAMES:

                self.dice_animating = False
                self.resource_points = self.dice_result
                self.state = "RESOURCE_CHOICE"

    def allocate_resource(self, resource_type):

        if resource_type == "food":
            self.race.food += self.resource_points
        elif resource_type == "defense":
            self.race.defense += self.resource_points
        elif resource_type == "tech":
            self.race.tech += self.resource_points

        self.trigger_random_event()

    def trigger_random_event(self):

        self.current_event = random.choice(self.random_events)

        old_population = self.race.population

        self.race.population += self.current_event.population_change

        if self.race.population < 0:
            self.race.population = 0

        self.state = "EVENT"

        self.event_log.append(f"Round {self.race.round}: {self.current_event.name} (Population {self.current_event.population_change:+d})")

        print(f"Event triggered: {self.current_event.name}, Population change: {old_population} -> {self.race.population}")

    def next_round(self):

        if not self.race.is_alive():
            self.end_game()
            return

        self.race.round += 1

        if self.race.round > MAX_ROUNDS:
            self.end_game()
        else:

            self.state = "DICE_READY"

    def end_game(self):

        self.ending_type = self.determine_ending()
        self.state = "GAME_OVER"
        self.game_over = True

    def draw(self):

        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill(WHITE)

        if self.state in ["DICE_READY", "DICE", "RESOURCE_CHOICE"]:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 100))
            self.screen.blit(overlay, (0, 0))

        if self.state == "START":
            self.draw_start_screen()
        elif self.state == "DICE_READY":
            self.draw_game_screen()
            self.draw_dice()
        elif self.state == "DICE":
            self.draw_game_screen()
            self.draw_dice()
        elif self.state == "RESOURCE_CHOICE":
            self.draw_game_screen()
            self.draw_dice()
            self.draw_resource_choice()
        elif self.state == "EVENT":
            self.draw_event()
        elif self.state == "GAME_OVER":
            self.draw_ending_screen()

        pygame.display.flip()

    def draw_start_screen(self):

        if self.ui_images.get('title'):
            title_img = self.ui_images['title']

            original_width = title_img.get_width()
            original_height = title_img.get_height()
            target_width = int(WINDOW_WIDTH * 0.4)
            scale_ratio = target_width / original_width
            target_height = int(original_height * scale_ratio)

            title_img_scaled = pygame.transform.scale(title_img, (target_width, target_height))
            title_x = WINDOW_WIDTH // 2 - target_width // 2
            title_y = WINDOW_HEIGHT // 3 - target_height // 2
            self.screen.blit(title_img_scaled, (title_x, title_y))
        else:

            title = TITLE_FONT.render("Short-Lived Race Simulator", True, TEXT_COLOR)
            self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, WINDOW_HEIGHT // 3))

        if self.ui_images.get('start_button'):
            start_btn_img = self.ui_images['start_button']

            original_width = start_btn_img.get_width()
            original_height = start_btn_img.get_height()
            target_width = int(WINDOW_WIDTH * 0.1)
            scale_ratio = target_width / original_width
            target_height = int(original_height * scale_ratio)

            start_btn_img_scaled = pygame.transform.scale(start_btn_img, (target_width, target_height))
            btn_x = WINDOW_WIDTH // 2 - target_width // 2
            btn_y = int(WINDOW_HEIGHT * 0.55)
            self.screen.blit(start_btn_img_scaled, (btn_x, btn_y))

            self.start_button_rect = pygame.Rect(btn_x, btn_y, target_width, target_height)
        else:

            button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2, 300, 100)
            mouse_pos = pygame.mouse.get_pos()

            if button_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, GREEN, button_rect, border_radius=10)
            else:
                pygame.draw.rect(self.screen, BLUE, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, BLACK, button_rect, 3, border_radius=10)
            start_text = EVENT_FONT.render("Start Game", True, WHITE)
            self.screen.blit(start_text, (WINDOW_WIDTH // 2 - start_text.get_width() // 2, WINDOW_HEIGHT // 2 + 30))

            self.start_button_rect = button_rect

    def draw_game_screen(self):

        top_height = int(WINDOW_HEIGHT * 0.4)

        status_box_x = int(WINDOW_WIDTH * 0.05)
        status_box_y = int(WINDOW_HEIGHT * 0.05)
        status_box_width = int(WINDOW_WIDTH * 0.18)
        status_box_height = top_height - int(WINDOW_HEIGHT * 0.05)

        if self.ui_images.get('option_v'):
            status_bg = self.ui_images['option_v']
            status_bg = pygame.transform.scale(status_bg, (status_box_width, status_box_height))
            self.screen.blit(status_bg, (status_box_x, status_box_y))
        else:
            pygame.draw.rect(self.screen, (210, 180, 140), (status_box_x, status_box_y, status_box_width, status_box_height), border_radius=10)
            pygame.draw.rect(self.screen, (101, 67, 33), (status_box_x, status_box_y, status_box_width, status_box_height), 3, border_radius=10)

        status_items = [
            f"Round: {self.race.round}/{MAX_ROUNDS}",
            f"Population: {self.race.population}",
            f"Food: {self.race.food}",
            f"Defense: {self.race.defense}",
            f"Technology: {self.race.tech}"
        ]

        total_text_height = 0
        text_surfaces = []
        for text in status_items:
            surf = SMALL_FONT.render(text, True, TEXT_COLOR)
            if surf.get_width() > status_box_width - int(status_box_width * 0.25):
                surf = TINY_FONT.render(text, True, TEXT_COLOR)
            text_surfaces.append(surf)
            total_text_height += surf.get_height()

        line_spacing = int(status_box_height * 0.05)
        total_text_height += line_spacing * (len(status_items) - 1)

        text_x = status_box_x + int(status_box_width * 0.22)
        text_y = status_box_y + (status_box_height - total_text_height) // 2

        for surf in text_surfaces:
            self.screen.blit(surf, (text_x, text_y))
            text_y += surf.get_height() + line_spacing

        hint_box_x = status_box_x + status_box_width + int(WINDOW_WIDTH * 0.03)
        hint_box_y = status_box_y
        hint_box_width = int(WINDOW_WIDTH * 0.95) - hint_box_x
        hint_box_height = status_box_height

        if self.ui_images.get('text_box'):
            hint_bg = self.ui_images['text_box']
            hint_bg = pygame.transform.scale(hint_bg, (hint_box_width, hint_box_height))
            self.screen.blit(hint_bg, (hint_box_x, hint_box_y))
        else:
            pygame.draw.rect(self.screen, (240, 230, 200), (hint_box_x, hint_box_y, hint_box_width, hint_box_height), border_radius=10)
            pygame.draw.rect(self.screen, (101, 67, 33), (hint_box_x, hint_box_y, hint_box_width, hint_box_height), 3, border_radius=10)

    def draw_dice(self):

        status_box_x = int(WINDOW_WIDTH * 0.05)
        status_box_y = int(WINDOW_HEIGHT * 0.05)
        status_box_width = int(WINDOW_WIDTH * 0.18)
        top_height = int(WINDOW_HEIGHT * 0.4)
        status_box_height = top_height - int(WINDOW_HEIGHT * 0.05)

        hint_box_x = status_box_x + status_box_width + int(WINDOW_WIDTH * 0.03)
        hint_box_y = status_box_y
        hint_box_width = int(WINDOW_WIDTH * 0.95) - hint_box_x
        hint_box_height = status_box_height

        if self.state == "DICE_READY":
            hint_text = TEXT_FONT.render("Click the dice to roll!", True, TEXT_COLOR)
            self.screen.blit(hint_text, (hint_box_x + hint_box_width // 2 - hint_text.get_width() // 2,
                                        hint_box_y + hint_box_height // 2 - hint_text.get_height() // 2))
        elif self.dice_animating:
            hint_text = TEXT_FONT.render("Rolling the dice...", True, TEXT_COLOR)
            self.screen.blit(hint_text, (hint_box_x + hint_box_width // 2 - hint_text.get_width() // 2,
                                        hint_box_y + hint_box_height // 2 - hint_text.get_height() // 2))
        else:
            hint_text = TEXT_FONT.render(f"Congratulations on earning {self.dice_result}", True, TEXT_COLOR)
            hint_text2 = TEXT_FONT.render("resource points!", True, TEXT_COLOR)
            hint_text3 = SMALL_FONT.render("Which resource would you like to", True, TEXT_COLOR)
            hint_text4 = SMALL_FONT.render("allocate them to?", True, TEXT_COLOR)

            text_start_y = hint_box_y + int(hint_box_height * 0.25)
            self.screen.blit(hint_text, (hint_box_x + hint_box_width // 2 - hint_text.get_width() // 2, text_start_y))
            self.screen.blit(hint_text2, (hint_box_x + hint_box_width // 2 - hint_text2.get_width() // 2, text_start_y + 40))
            self.screen.blit(hint_text3, (hint_box_x + hint_box_width // 2 - hint_text3.get_width() // 2, text_start_y + 90))
            self.screen.blit(hint_text4, (hint_box_x + hint_box_width // 2 - hint_text4.get_width() // 2, text_start_y + 120))

        total_bottom_width = hint_box_width
        column_spacing = int(WINDOW_WIDTH * 0.02)
        dice_box_width = (total_bottom_width - column_spacing) // 2

        dice_box_x = hint_box_x + dice_box_width + column_spacing
        dice_box_y = top_height + int(WINDOW_HEIGHT * 0.03)
        dice_box_height = int(WINDOW_HEIGHT * 0.95) - dice_box_y

        if self.ui_images.get('option_v'):
            dice_bg = self.ui_images['option_v']
            dice_bg = pygame.transform.scale(dice_bg, (dice_box_width, dice_box_height))
            self.screen.blit(dice_bg, (dice_box_x, dice_box_y))
        else:
            pygame.draw.rect(self.screen, (240, 230, 200), (dice_box_x, dice_box_y, dice_box_width, dice_box_height), border_radius=10)
            pygame.draw.rect(self.screen, (101, 67, 33), (dice_box_x, dice_box_y, dice_box_width, dice_box_height), 3, border_radius=10)

        if self.state == "DICE_READY":
            click_text = SMALL_FONT.render("Click the dice to roll", True, TEXT_COLOR)
        else:
            click_text = SMALL_FONT.render("", True, TEXT_COLOR)
        self.screen.blit(click_text, (dice_box_x + dice_box_width // 2 - click_text.get_width() // 2, dice_box_y + int(dice_box_height * 0.15)))

        if self.dice_animating:

            dice_index = random.randint(0, 5)
            dice_img = self.dice_images[dice_index]
        else:

            dice_img = self.dice_images[self.dice_result - 1]

        dice_size = int(min(dice_box_width, dice_box_height) * 0.45)
        dice_img = pygame.transform.scale(dice_img, (dice_size, dice_size))
        dice_x = dice_box_x + dice_box_width // 2 - dice_size // 2
        dice_y = dice_box_y + dice_box_height // 2 - dice_size // 2 + int(dice_box_height * 0.05)
        self.screen.blit(dice_img, (dice_x, dice_y))

        # Store dice rect for click detection
        self.dice_rect = pygame.Rect(dice_x, dice_y, dice_size, dice_size)

    def draw_resource_choice(self):

        status_box_x = int(WINDOW_WIDTH * 0.05)
        status_box_width = int(WINDOW_WIDTH * 0.18)
        top_height = int(WINDOW_HEIGHT * 0.4)

        hint_box_x = status_box_x + status_box_width + int(WINDOW_WIDTH * 0.03)
        hint_box_width = int(WINDOW_WIDTH * 0.95) - hint_box_x

        total_bottom_width = hint_box_width
        column_spacing = int(WINDOW_WIDTH * 0.02)
        button_width = (total_bottom_width - column_spacing) // 2

        button_x = hint_box_x
        start_y = top_height + int(WINDOW_HEIGHT * 0.03)

        available_height = int(WINDOW_HEIGHT * 0.95) - start_y
        button_spacing = int(available_height * 0.05)
        button_height = (available_height - button_spacing * 2) // 3

        choices = [
            ("Food", "food", GREEN),
            ("Defense", "defense", BLUE),
            ("Technology", "tech", ORANGE)
        ]

        mouse_pos = pygame.mouse.get_pos()

        for i, (label, resource_type, color) in enumerate(choices):
            button_y = start_y + i * (button_height + button_spacing)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            if not hasattr(self, 'resource_buttons'):
                self.resource_buttons = {}
            self.resource_buttons[resource_type] = button_rect

            is_hover = button_rect.collidepoint(mouse_pos)

            if self.ui_images.get('option_h'):
                option_img = self.ui_images['option_h']
                option_img = pygame.transform.scale(option_img, (button_width, button_height))
                self.screen.blit(option_img, (button_x, button_y))

                if is_hover:
                    highlight = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
                    highlight.fill((255, 255, 255, 80))
                    self.screen.blit(highlight, (button_x, button_y))
                text_color = TEXT_COLOR
            else:
                if is_hover:
                    pygame.draw.rect(self.screen, color, button_rect, border_radius=8)
                    text_color = WHITE
                else:
                    pygame.draw.rect(self.screen, (240, 230, 200), button_rect, border_radius=8)
                    pygame.draw.rect(self.screen, (101, 67, 33), button_rect, 3, border_radius=8)
                    text_color = TEXT_COLOR

            text = TEXT_FONT.render(label, True, text_color)
            self.screen.blit(text, (button_x + button_width // 2 - text.get_width() // 2,
                                   button_y + button_height // 2 - text.get_height() // 2))

    def draw_event(self):

        if not self.current_event:
            return

        if self.current_event.gif_frames and len(self.current_event.gif_frames) > 0:

            self.current_event.frame_counter += 1
            if self.current_event.frame_counter >= self.current_event.frame_delay:
                self.current_event.frame_counter = 0
                self.current_event.current_frame = (self.current_event.current_frame + 1) % len(self.current_event.gif_frames)

            current_frame = self.current_event.gif_frames[self.current_event.current_frame]

            current_frame_scaled = pygame.transform.scale(current_frame, (WINDOW_WIDTH, WINDOW_HEIGHT))
            self.screen.blit(current_frame_scaled, (0, 0))

        top_height = int(WINDOW_HEIGHT * 0.4)
        status_box_x = int(WINDOW_WIDTH * 0.05)
        status_box_y = int(WINDOW_HEIGHT * 0.05)
        status_box_width = int(WINDOW_WIDTH * 0.18)
        status_box_height = top_height - int(WINDOW_HEIGHT * 0.05)

        if self.ui_images.get('option_v'):
            status_bg = self.ui_images['option_v']
            status_bg = pygame.transform.scale(status_bg, (status_box_width, status_box_height))
            self.screen.blit(status_bg, (status_box_x, status_box_y))
        else:
            pygame.draw.rect(self.screen, (210, 180, 140), (status_box_x, status_box_y, status_box_width, status_box_height), border_radius=10)
            pygame.draw.rect(self.screen, (101, 67, 33), (status_box_x, status_box_y, status_box_width, status_box_height), 3, border_radius=10)

        status_items = [
            f"Round: {self.race.round}/{MAX_ROUNDS}",
            f"Population: {self.race.population}",
            f"Food: {self.race.food}",
            f"Defense: {self.race.defense}",
            f"Technology: {self.race.tech}"
        ]

        total_text_height = 0
        text_surfaces = []
        for text in status_items:
            surf = SMALL_FONT.render(text, True, TEXT_COLOR)
            if surf.get_width() > status_box_width - int(status_box_width * 0.25):
                surf = TINY_FONT.render(text, True, TEXT_COLOR)
            text_surfaces.append(surf)
            total_text_height += surf.get_height()

        line_spacing = int(status_box_height * 0.05)
        total_text_height += line_spacing * (len(status_items) - 1)

        text_x = status_box_x + int(status_box_width * 0.22)
        text_y = status_box_y + (status_box_height - total_text_height) // 2

        for surf in text_surfaces:
            self.screen.blit(surf, (text_x, text_y))
            text_y += surf.get_height() + line_spacing

        desc_box_width = int(WINDOW_WIDTH * 0.5)
        desc_box_height = int(WINDOW_HEIGHT * 0.35)
        desc_box_x = WINDOW_WIDTH // 2 - desc_box_width // 2
        desc_box_y = WINDOW_HEIGHT // 2 - desc_box_height // 2

        if self.ui_images.get('text_box'):
            desc_bg = self.ui_images['text_box']
            desc_bg = pygame.transform.scale(desc_bg, (desc_box_width, desc_box_height))
            self.screen.blit(desc_bg, (desc_box_x, desc_box_y))
        else:
            pygame.draw.rect(self.screen, (240, 230, 200), (desc_box_x, desc_box_y, desc_box_width, desc_box_height), border_radius=10)
            pygame.draw.rect(self.screen, (101, 67, 33), (desc_box_x, desc_box_y, desc_box_width, desc_box_height), 3, border_radius=10)

        event_title = EVENT_FONT.render(self.current_event.name, True, TEXT_COLOR)

        desc_lines = []
        if hasattr(self.current_event, 'description') and self.current_event.description:
            desc_lines = self.current_event.description.split('\n')

        if self.current_event.population_change < 0:
            pop_change_text = "The event causes significant losses:"
        else:
            pop_change_text = "The event brings prosperity:"
        pop_change_text2 = f"{self.current_event.population_change:+d} Population"

        total_content_height = event_title.get_height() + 30
        total_content_height += len(desc_lines) * 35
        total_content_height += 20
        total_content_height += SMALL_FONT.get_height() + 10
        total_content_height += TEXT_FONT.get_height()

        content_start_y = desc_box_y + (desc_box_height - total_content_height) // 2
        current_y = content_start_y

        self.screen.blit(event_title, (desc_box_x + desc_box_width // 2 - event_title.get_width() // 2, current_y))
        current_y += event_title.get_height() + 30

        for line in desc_lines:
            desc_surf = SMALL_FONT.render(line, True, TEXT_COLOR)
            self.screen.blit(desc_surf, (desc_box_x + desc_box_width // 2 - desc_surf.get_width() // 2, current_y))
            current_y += 35

        current_y += 20

        pop_surf = SMALL_FONT.render(pop_change_text, True, TEXT_COLOR)
        self.screen.blit(pop_surf, (desc_box_x + desc_box_width // 2 - pop_surf.get_width() // 2, current_y))
        current_y += pop_surf.get_height() + 10

        pop_surf2 = TEXT_FONT.render(pop_change_text2, True, RED if self.current_event.population_change < 0 else GREEN)
        self.screen.blit(pop_surf2, (desc_box_x + desc_box_width // 2 - pop_surf2.get_width() // 2, current_y))

        confirm_btn_width = int(WINDOW_WIDTH * 0.15)
        confirm_btn_height = int(WINDOW_HEIGHT * 0.08)
        confirm_btn_x = WINDOW_WIDTH // 2 - confirm_btn_width // 2
        confirm_btn_y = desc_box_y + desc_box_height + int(WINDOW_HEIGHT * 0.05)

        confirm_btn_rect = pygame.Rect(confirm_btn_x, confirm_btn_y, confirm_btn_width, confirm_btn_height)
        mouse_pos = pygame.mouse.get_pos()
        is_hover = confirm_btn_rect.collidepoint(mouse_pos)

        if self.ui_images.get('option_h'):
            confirm_bg = self.ui_images['option_h']
            confirm_bg = pygame.transform.scale(confirm_bg, (confirm_btn_width, confirm_btn_height))
            self.screen.blit(confirm_bg, (confirm_btn_x, confirm_btn_y))
            if is_hover:
                highlight = pygame.Surface((confirm_btn_width, confirm_btn_height), pygame.SRCALPHA)
                highlight.fill((255, 255, 255, 80))
                self.screen.blit(highlight, (confirm_btn_x, confirm_btn_y))
        else:
            pygame.draw.rect(self.screen, (240, 230, 200), confirm_btn_rect, border_radius=8)
            pygame.draw.rect(self.screen, (101, 67, 33), confirm_btn_rect, 3, border_radius=8)

        confirm_text = TEXT_FONT.render("Confirm", True, TEXT_COLOR)
        self.screen.blit(confirm_text, (confirm_btn_x + confirm_btn_width // 2 - confirm_text.get_width() // 2,
                                       confirm_btn_y + confirm_btn_height // 2 - confirm_text.get_height() // 2))

        self.confirm_button_rect = confirm_btn_rect

    def draw_ending_screen(self):

        if not self.ending_type:
            return

        ending_img = self.ending_images.get(self.ending_type)
        if ending_img:

            ending_img_scaled = pygame.transform.scale(ending_img, (WINDOW_WIDTH, WINDOW_HEIGHT))
            self.screen.blit(ending_img_scaled, (0, 0))

        left_box_width = int(WINDOW_WIDTH * 0.45)
        left_box_height = int(WINDOW_HEIGHT * 0.5)
        left_box_x = int(WINDOW_WIDTH * 0.08)
        left_box_y = WINDOW_HEIGHT // 2 - left_box_height // 2

        if self.ui_images.get('text_box'):
            left_bg = self.ui_images['text_box']
            left_bg = pygame.transform.scale(left_bg, (left_box_width, left_box_height))
            self.screen.blit(left_bg, (left_box_x, left_box_y))
        else:
            pygame.draw.rect(self.screen, (240, 230, 200), (left_box_x, left_box_y, left_box_width, left_box_height), border_radius=10)
            pygame.draw.rect(self.screen, (101, 67, 33), (left_box_x, left_box_y, left_box_width, left_box_height), 3, border_radius=10)

        ending_title = EVENT_FONT.render(self.ending_type, True, TEXT_COLOR)
        title_x = left_box_x + left_box_width // 2 - ending_title.get_width() // 2
        title_y = left_box_y + int(left_box_height * 0.15)
        self.screen.blit(ending_title, (title_x, title_y))

        desc_y = title_y + ending_title.get_height() + 40
        ending_descriptions = {
            "extinction": [
                "Your civilization has fallen into darkness.",
                "The population has dwindled to zero,",
                "leaving only ruins and memories.",
                "",
                "Perhaps with better resource management,",
                "a different fate could have been achieved."
            ],
            "primitive": [
                "Your people remain in a primitive state.",
                "Though survival is achieved,",
                "progress has been slow and difficult.",
                "",
                "With more resources and development,",
                "a brighter future may be possible."
            ],
            "agricultural": [
                "Your civilization has entered the Agricultural Age!",
                "Through farming and basic technology,",
                "your people have established a stable society.",
                "",
                "Food is abundant and knowledge grows,",
                "laying the foundation for future prosperity."
            ],
            "scientific": [
                "A Scientific Revolution has transformed your world!",
                "Through research and innovation,",
                "your people have unlocked new possibilities.",
                "",
                "Technology advances rapidly,",
                "ushering in an age of discovery and progress."
            ],
            "utopia": [
                "Your civilization has achieved Utopia!",
                "Perfect harmony between resources and population,",
                "advanced technology and abundant food.",
                "",
                "Your people live in peace and prosperity,",
                "a shining example for all civilizations."
            ],
            "prosperous": [
                "Your civilization has achieved Population Prosperity!",
                "Through careful management and growth,",
                "your people have thrived and multiplied.",
                "",
                "The future is bright with possibilities,",
                "as your civilization continues to flourish."
            ],
            "ai_crisis": [
                "An AI Crisis threatens your civilization!",
                "Advanced technology has grown beyond control,",
                "creating unforeseen dangers and challenges.",
                "",
                "Your people face an uncertain future,",
                "as they struggle with their own creations."
            ],
            "population_overload": [
                "Population Overload has strained your civilization!",
                "The rapid growth in numbers has exceeded",
                "the capacity of available resources.",
                "",
                "Your people struggle to sustain themselves,",
                "facing challenges of overcrowding and scarcity."
            ]
        }

        desc_lines = ending_descriptions.get(self.ending_type, ["Game Over", "", "Your journey has ended."])
        for line in desc_lines:
            if line:
                desc_surf = SMALL_FONT.render(line, True, TEXT_COLOR)
                desc_x = left_box_x + left_box_width // 2 - desc_surf.get_width() // 2
                self.screen.blit(desc_surf, (desc_x, desc_y))
            desc_y += 35

        right_box_width = int(WINDOW_WIDTH * 0.25)
        right_box_height = left_box_height
        right_box_x = left_box_x + left_box_width + int(WINDOW_WIDTH * 0.05)
        right_box_y = left_box_y

        if self.ui_images.get('option_v'):
            right_bg = self.ui_images['option_v']
            right_bg = pygame.transform.scale(right_bg, (right_box_width, right_box_height))
            self.screen.blit(right_bg, (right_box_x, right_box_y))
        else:
            pygame.draw.rect(self.screen, (210, 180, 140), (right_box_x, right_box_y, right_box_width, right_box_height), border_radius=10)
            pygame.draw.rect(self.screen, (101, 67, 33), (right_box_x, right_box_y, right_box_width, right_box_height), 3, border_radius=10)

        final_stats = [
            f"Round: {self.race.round}/{MAX_ROUNDS}",
            f"Population: {self.race.population}",
            f"Food: {self.race.food}",
            f"Defense: {self.race.defense}",
            f"Technology: {self.race.tech}"
        ]

        total_text_height = 0
        text_surfaces = []
        for text in final_stats:
            surf = SMALL_FONT.render(text, True, TEXT_COLOR)
            if surf.get_width() > right_box_width - int(right_box_width * 0.25):
                surf = TINY_FONT.render(text, True, TEXT_COLOR)
            text_surfaces.append(surf)
            total_text_height += surf.get_height()

        line_spacing = int(right_box_height * 0.05)
        total_text_height += line_spacing * (len(final_stats) - 1)

        text_x = right_box_x + int(right_box_width * 0.15)
        text_y = right_box_y + (right_box_height - total_text_height) // 2

        for surf in text_surfaces:
            self.screen.blit(surf, (text_x, text_y))
            text_y += surf.get_height() + line_spacing

        restart_btn_width = right_box_width
        restart_btn_height = int(WINDOW_HEIGHT * 0.1)
        restart_btn_x = right_box_x
        restart_btn_y = right_box_y + right_box_height + int(WINDOW_HEIGHT * 0.03)

        restart_button_rect = pygame.Rect(restart_btn_x, restart_btn_y, restart_btn_width, restart_btn_height)

        self.restart_button_rect = restart_button_rect

        mouse_pos = pygame.mouse.get_pos()
        is_hover = restart_button_rect.collidepoint(mouse_pos)

        if self.ui_images.get('option_h'):
            restart_bg = self.ui_images['option_h']
            restart_bg = pygame.transform.scale(restart_bg, (restart_btn_width, restart_btn_height))
            self.screen.blit(restart_bg, (restart_btn_x, restart_btn_y))
            if is_hover:
                highlight = pygame.Surface((restart_btn_width, restart_btn_height), pygame.SRCALPHA)
                highlight.fill((255, 255, 255, 80))
                self.screen.blit(highlight, (restart_btn_x, restart_btn_y))
        else:
            pygame.draw.rect(self.screen, (240, 230, 200), restart_button_rect, border_radius=8)
            pygame.draw.rect(self.screen, (101, 67, 33), restart_button_rect, 3, border_radius=8)

        restart_text = TEXT_FONT.render("Restart", True, TEXT_COLOR)
        self.screen.blit(restart_text, (restart_btn_x + restart_btn_width // 2 - restart_text.get_width() // 2,
                                       restart_btn_y + restart_btn_height // 2 - restart_text.get_height() // 2))

    def reset_game(self):

        self.race = Race()
        self.game_over = False
        self.game_started = False
        self.state = "START"
        self.dice_animating = False
        self.dice_animation_frame = 0
        self.dice_result = 1
        self.resource_points = 0
        self.current_event = None
        self.event_log = []
        self.ending_type = None
        if hasattr(self, 'dice_rect'):
            delattr(self, 'dice_rect')

    def run(self):

        running = True
        while running:
            self.clock.tick(FPS)

            if self.state == "DICE":
                self.update_dice_animation()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:
                        running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if self.state == "START":

                        if hasattr(self, 'start_button_rect') and self.start_button_rect.collidepoint(mouse_pos):
                            self.start_game()

                    elif self.state == "DICE_READY":
                        # Click dice to start rolling
                        if hasattr(self, 'dice_rect') and self.dice_rect.collidepoint(mouse_pos):
                            self.state = "DICE"
                            self.start_dice_animation()

                    elif self.state == "RESOURCE_CHOICE":

                        if hasattr(self, 'resource_buttons'):
                            for resource_type, button_rect in self.resource_buttons.items():
                                if button_rect.collidepoint(mouse_pos):
                                    self.allocate_resource(resource_type)
                                    break

                    elif self.state == "EVENT":

                        if hasattr(self, 'confirm_button_rect') and self.confirm_button_rect.collidepoint(mouse_pos):
                            self.next_round()

                    elif self.state == "GAME_OVER":

                        if hasattr(self, 'restart_button_rect') and self.restart_button_rect.collidepoint(mouse_pos):
                            self.reset_game()

            self.draw()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
