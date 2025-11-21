import pygame
import random
import sys
import os
from PIL import Image, ImageSequence

# 初始化 Pygame
pygame.init()

# 获取屏幕分辨率
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h

# 常量定义
WINDOW_WIDTH = SCREEN_WIDTH
WINDOW_HEIGHT = SCREEN_HEIGHT
FPS = 60
MAX_ROUNDS = 5
DICE_ANIMATION_FRAMES = 30  # 骰子动画帧数

# 颜色定义
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

# 字体设置
pygame.font.init()
# 使用系统中文字体
try:
    # Windows 系统字体
    TITLE_FONT = pygame.font.SysFont('microsoftyahei', 56)
    EVENT_FONT = pygame.font.SysFont('microsoftyahei', 40)
    TEXT_FONT = pygame.font.SysFont('microsoftyahei', 32)
    SMALL_FONT = pygame.font.SysFont('microsoftyahei', 28)
    TINY_FONT = pygame.font.SysFont('microsoftyahei', 24)
except:
    # 备用字体
    try:
        TITLE_FONT = pygame.font.SysFont('simsun', 56)
        EVENT_FONT = pygame.font.SysFont('simsun', 40)
        TEXT_FONT = pygame.font.SysFont('simsun', 32)
        SMALL_FONT = pygame.font.SysFont('simsun', 28)
        TINY_FONT = pygame.font.SysFont('simsun', 24)
    except:
        # 最后备用
        TITLE_FONT = pygame.font.Font(None, 56)
        EVENT_FONT = pygame.font.Font(None, 40)
        TEXT_FONT = pygame.font.Font(None, 32)
        SMALL_FONT = pygame.font.Font(None, 28)
        TINY_FONT = pygame.font.Font(None, 24)


class Race:
    """短命种族类"""
    def __init__(self):
        self.population = 5  # 初始人口为5
        self.food = 0  # 粮食
        self.defense = 0  # 防御
        self.tech = 0  # 科技
        self.round = 1  # 当前回合

    def is_alive(self):
        return self.population > 0


class RandomEvent:
    """随机事件类"""
    def __init__(self, name, gif_frames, population_change):
        self.name = name
        self.gif_frames = gif_frames  # GIF动画帧列表
        self.population_change = population_change  # 人口变化量
        self.current_frame = 0  # 当前帧索引
        self.frame_counter = 0  # 帧计数器
        self.frame_delay = 3  # 每3帧切换一次GIF帧


class Game:
    """游戏主类"""
    def __init__(self):
        # 创建全屏窗口
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("短命种族模拟器")
        self.clock = pygame.time.Clock()
        self.race = Race()
        self.game_over = False
        self.game_started = False  # 游戏是否开始

        # 游戏状态
        self.state = "START"  # START, DICE, RESOURCE_CHOICE, EVENT, GAME_OVER

        # 骰子相关
        self.dice_images = self.load_dice_images()
        self.dice_animating = False
        self.dice_animation_frame = 0
        self.dice_result = 1
        self.resource_points = 0  # 本回合可分配资源点

        # 事件相关
        self.current_event = None
        self.event_log = []

        # UI素材
        self.ui_images = self.load_ui_images()
        self.event_gifs = self.load_event_gifs()
        self.ending_images = self.load_ending_images()
        self.ending_type = None  # 结局类型

        # 随机事件列表
        self.random_events = self.create_random_events()

    def load_dice_images(self):
        """加载骰子图片"""
        dice_images = []
        for i in range(1, 7):
            try:
                img_path = os.path.join("static", "骰子", f"{i}.png")
                img = pygame.image.load(img_path)
                # 调整骰子大小
                img = pygame.transform.scale(img, (200, 200))
                dice_images.append(img)
            except Exception as e:
                print(f"加载骰子图片 {i}.png 失败: {e}")
                # 创建一个简单的占位图
                placeholder = pygame.Surface((200, 200))
                placeholder.fill(WHITE)
                pygame.draw.rect(placeholder, BLACK, (0, 0, 200, 200), 3)
                font = pygame.font.Font(None, 100)
                text = font.render(str(i), True, BLACK)
                placeholder.blit(text, (75, 50))
                dice_images.append(placeholder)
        return dice_images

    def load_ui_images(self):
        """加载UI素材"""
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
                print(f"加载UI图片 {filename} 失败: {e}")
                ui_images[key] = None
        return ui_images

    def load_event_gifs(self):
        """加载事件GIF动画（使用PIL加载所有帧）"""
        event_gifs = {}
        event_files = {
            '干旱': '干旱.gif',
            '丰收': '丰收.gif',
            '寒冬': '寒冬.gif',
            '洪水': '洪水.gif',
            '发现沃土': '发现沃土.gif'
        }
        for key, filename in event_files.items():
            try:
                img_path = os.path.join("static", "随机事件gif", filename)
                # 使用PIL加载GIF的所有帧
                pil_image = Image.open(img_path)
                frames = []

                # 提取所有帧
                for frame in ImageSequence.Iterator(pil_image):
                    # 转换为RGBA模式
                    frame = frame.convert('RGBA')
                    # 转换为pygame surface
                    frame_str = frame.tobytes()
                    frame_surface = pygame.image.fromstring(frame_str, frame.size, 'RGBA')
                    # 缩放到合适大小
                    frame_surface = pygame.transform.scale(frame_surface, (400, 300))
                    frames.append(frame_surface)

                event_gifs[key] = frames
                print(f"成功加载 {filename}，共 {len(frames)} 帧")
            except Exception as e:
                print(f"加载事件图片 {filename} 失败: {e}")
                # 创建占位图
                placeholder = pygame.Surface((400, 300))
                placeholder.fill(LIGHT_BLUE)
                pygame.draw.rect(placeholder, BLACK, (0, 0, 400, 300), 3)
                text = SMALL_FONT.render(key, True, BLACK)
                placeholder.blit(text, (200 - text.get_width()//2, 140))
                event_gifs[key] = [placeholder]  # 作为单帧列表
        return event_gifs

    def load_ending_images(self):
        """加载结局图片"""
        ending_images = {}
        ending_files = {
            '种族灭绝': '种族灭绝.png',
            '原始永恒': '原始永恒.png',
            '人口繁盛': '人口繁盛.png',
            '农耕时代': '农耕时代.png',
            '科学革命': '科学革命.png',
            '乌托邦': '乌托邦.png',
            '智能危机': '人口过载.png'
        }
        for key, filename in ending_files.items():
            try:
                img_path = os.path.join("static", "游戏结局png", filename)
                img = pygame.image.load(img_path)
                img = pygame.transform.scale(img, (800, 500))
                ending_images[key] = img
            except Exception as e:
                print(f"加载结局图片 {filename} 失败: {e}")
                # 创建占位图
                placeholder = pygame.Surface((800, 500))
                placeholder.fill(DARK_GRAY)
                pygame.draw.rect(placeholder, BLACK, (0, 0, 800, 500), 3)
                text = EVENT_FONT.render(key, True, WHITE)
                placeholder.blit(text, (400 - text.get_width()//2, 240))
                ending_images[key] = placeholder
        return ending_images

    def create_random_events(self):
        """创建5种随机事件"""
        events = [
            RandomEvent("干旱", self.event_gifs.get('干旱'), -1),
            RandomEvent("丰收", self.event_gifs.get('丰收'), 2),
            RandomEvent("寒冬", self.event_gifs.get('寒冬'), -1),
            RandomEvent("洪水", self.event_gifs.get('洪水'), -2),
            RandomEvent("发现沃土", self.event_gifs.get('发现沃土'), 2)
        ]
        return events

    def determine_ending(self):
        """判定游戏结局"""
        x = self.race.population
        food = self.race.food
        defense = self.race.defense
        tech = self.race.tech

        # 按优先级判定结局
        # 1. 种族灭绝
        if x == 0:
            return '种族灭绝'

        # 2. 原始永恒
        if 0 < x <= 7:
            return '原始永恒'

        # 3. 人口繁盛及其特殊结局
        if 7 < x <= 10:
            # 3.1 农耕时代
            if food >= 8 and tech >= 5:
                return '农耕时代'
            # 3.2 科学革命
            if food >= 10 and 3 <= defense < 5 and tech >= 8:
                return '科学革命'
            # 3.3 乌托邦
            if food >= 10 and tech >= 10:
                return '乌托邦'
            # 3.0 普通人口繁盛
            return '人口繁盛'

        # 4. 智能危机（人口过载）
        if x >= 10 and food >= 8 and defense >= 5 and tech >= 10:
            return '智能危机'

        # 默认返回人口繁盛（x>10但不满足智能危机条件）
        return '人口繁盛'

    def start_game(self):
        """开始游戏"""
        self.game_started = True
        self.state = "DICE"
        self.start_dice_animation()

    def start_dice_animation(self):
        """开始骰子动画"""
        self.dice_animating = True
        self.dice_animation_frame = 0
        self.dice_result = random.randint(1, 6)

    def update_dice_animation(self):
        """更新骰子动画"""
        if self.dice_animating:
            self.dice_animation_frame += 1
            if self.dice_animation_frame >= DICE_ANIMATION_FRAMES:
                # 动画结束
                self.dice_animating = False
                self.resource_points = self.dice_result
                self.state = "RESOURCE_CHOICE"

    def allocate_resource(self, resource_type):
        """分配资源点"""
        if resource_type == "food":
            self.race.food += self.resource_points
        elif resource_type == "defense":
            self.race.defense += self.resource_points
        elif resource_type == "tech":
            self.race.tech += self.resource_points

        # 触发随机事件
        self.trigger_random_event()

    def trigger_random_event(self):
        """触发随机事件"""
        # 随机选择一个事件
        self.current_event = random.choice(self.random_events)

        # 记录事件前的人口
        old_population = self.race.population

        # 应用人口变化
        self.race.population += self.current_event.population_change

        # 确保人口不为负数
        if self.race.population < 0:
            self.race.population = 0

        # 切换到事件显示状态
        self.state = "EVENT"

        # 记录事件日志
        self.event_log.append(f"第{self.race.round}回合: {self.current_event.name} (人口{self.current_event.population_change:+d})")

        # 打印调试信息
        print(f"触发事件: {self.current_event.name}, 人口变化: {old_population} -> {self.race.population}")

    def next_round(self):
        """进入下一回合"""
        # 检查是否存活
        if not self.race.is_alive():
            self.end_game()
            return

        self.race.round += 1

        # 检查是否游戏结束
        if self.race.round > MAX_ROUNDS:
            self.end_game()
        else:
            # 继续下一回合
            self.state = "DICE"
            self.start_dice_animation()

    def end_game(self):
        """结束游戏"""
        self.ending_type = self.determine_ending()
        self.state = "GAME_OVER"
        self.game_over = True

    def draw(self):
        """绘制游戏界面"""
        self.screen.fill(WHITE)

        if self.state == "START":
            self.draw_start_screen()
        elif self.state == "DICE":
            self.draw_game_screen()
            self.draw_dice()
        elif self.state == "RESOURCE_CHOICE":
            self.draw_game_screen()
            self.draw_dice()
            self.draw_resource_choice()
        elif self.state == "EVENT":
            self.draw_game_screen()
            self.draw_event()
        elif self.state == "GAME_OVER":
            self.draw_ending_screen()

        pygame.display.flip()

    def draw_start_screen(self):
        """绘制开始界面"""
        # 绘制标题图片
        if self.ui_images.get('title'):
            title_img = self.ui_images['title']
            title_img = pygame.transform.scale(title_img, (700, 180))
            self.screen.blit(title_img, (WINDOW_WIDTH // 2 - 350, 100))
        else:
            title = TITLE_FONT.render("短命种族模拟器", True, BLACK)
            self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 150))

        # 绘制开始按钮（使用UI素材）
        button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, 350, 300, 100)
        mouse_pos = pygame.mouse.get_pos()

        if self.ui_images.get('start_button'):
            start_btn_img = self.ui_images['start_button']
            start_btn_img = pygame.transform.scale(start_btn_img, (300, 100))
            self.screen.blit(start_btn_img, (WINDOW_WIDTH // 2 - 150, 350))
        else:
            if button_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, GREEN, button_rect, border_radius=10)
            else:
                pygame.draw.rect(self.screen, BLUE, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, BLACK, button_rect, 3, border_radius=10)
            start_text = EVENT_FONT.render("开始游戏", True, WHITE)
            self.screen.blit(start_text, (WINDOW_WIDTH // 2 - start_text.get_width() // 2, 380))

        # 存储按钮区域供点击检测
        self.start_button_rect = button_rect

        # 游戏说明（使用文字框背景）
        instructions = [
            "游戏规则：",
            "1. 每回合投掷骰子获得资源点（1-6点）",
            "2. 选择将资源点分配到粮食、防御或科技",
            "3. 每回合结束后触发随机事件影响人口",
            "4. 游戏共5回合，根据最终状态判定结局"
        ]

        # 绘制文字框背景
        text_box_y = 480
        text_box_width = 800
        text_box_height = 250
        if self.ui_images.get('text_box'):
            text_box_img = self.ui_images['text_box']
            text_box_img = pygame.transform.scale(text_box_img, (text_box_width, text_box_height))
            self.screen.blit(text_box_img, (WINDOW_WIDTH // 2 - text_box_width // 2, text_box_y))
        else:
            pygame.draw.rect(self.screen, LIGHT_BLUE, (WINDOW_WIDTH // 2 - text_box_width // 2, text_box_y, text_box_width, text_box_height), border_radius=10)
            pygame.draw.rect(self.screen, BLACK, (WINDOW_WIDTH // 2 - text_box_width // 2, text_box_y, text_box_width, text_box_height), 2, border_radius=10)

        # 文字在框内居中，留出边距
        y = text_box_y + 40
        for instruction in instructions:
            text = TINY_FONT.render(instruction, True, BLACK)
            # 确保文字在框内
            x = WINDOW_WIDTH // 2 - text.get_width() // 2
            # 限制在文字框范围内
            if x < WINDOW_WIDTH // 2 - text_box_width // 2 + 20:
                x = WINDOW_WIDTH // 2 - text_box_width // 2 + 20
            self.screen.blit(text, (x, y))
            y += 38

    def draw_game_screen(self):
        """绘制游戏主界面（状态栏）"""
        # 标题
        title = TEXT_FONT.render("短命种族模拟器", True, BLACK)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, int(WINDOW_HEIGHT * 0.02)))

        # 左上角状态栏（使用文字框背景）
        status_box_x = int(WINDOW_WIDTH * 0.02)
        status_box_y = int(WINDOW_HEIGHT * 0.08)
        status_box_width = int(WINDOW_WIDTH * 0.18)
        status_box_height = int(WINDOW_HEIGHT * 0.35)

        # 绘制状态框背景
        if self.ui_images.get('text_box'):
            status_bg = self.ui_images['text_box']
            status_bg = pygame.transform.scale(status_bg, (status_box_width, status_box_height))
            self.screen.blit(status_bg, (status_box_x, status_box_y))
        else:
            pygame.draw.rect(self.screen, LIGHT_BLUE, (status_box_x, status_box_y, status_box_width, status_box_height), border_radius=10)
            pygame.draw.rect(self.screen, BLACK, (status_box_x, status_box_y, status_box_width, status_box_height), 2, border_radius=10)

        # 回合信息和资源状态（确保在框内）
        text_x = status_box_x + 20  # 左边距20像素
        text_y = status_box_y + 20  # 上边距20像素

        # 回合信息
        round_text = SMALL_FONT.render(f"回合: {self.race.round}/{MAX_ROUNDS}", True, BLUE)
        self.screen.blit(round_text, (text_x, text_y))
        text_y += 45

        # 分隔线
        line_y = text_y
        pygame.draw.line(self.screen, BLACK, (text_x, line_y), (status_box_x + status_box_width - 20, line_y), 2)
        text_y += 15

        # 资源状态
        status_items = [
            (f"人口: {self.race.population}", RED),
            (f"粮食: {self.race.food}", GREEN),
            (f"防御: {self.race.defense}", BLUE),
            (f"科技: {self.race.tech}", ORANGE)
        ]

        for text, color in status_items:
            surf = TEXT_FONT.render(text, True, color)
            # 确保文字不超出框的右边界
            if surf.get_width() > status_box_width - 40:
                # 如果文字太长，使用小字体
                surf = SMALL_FONT.render(text, True, color)
            self.screen.blit(surf, (text_x, text_y))
            text_y += 50

        # 事件日志（右上角）
        if self.event_log:
            # 绘制日志背景
            log_box_x = int(WINDOW_WIDTH * 0.8)
            log_box_y = int(WINDOW_HEIGHT * 0.08)
            log_box_width = int(WINDOW_WIDTH * 0.18)
            log_box_height = int(WINDOW_HEIGHT * 0.35)

            if self.ui_images.get('text_box'):
                log_box = self.ui_images['text_box']
                log_box = pygame.transform.scale(log_box, (log_box_width, log_box_height))
                self.screen.blit(log_box, (log_box_x, log_box_y))
            else:
                pygame.draw.rect(self.screen, LIGHT_BLUE, (log_box_x, log_box_y, log_box_width, log_box_height), border_radius=10)
                pygame.draw.rect(self.screen, BLACK, (log_box_x, log_box_y, log_box_width, log_box_height), 2, border_radius=10)

            # 标题在框内
            log_title = SMALL_FONT.render("事件记录:", True, BLACK)
            self.screen.blit(log_title, (log_box_x + 20, log_box_y + 15))

            # 分隔线
            line_y = log_box_y + 50
            pygame.draw.line(self.screen, BLACK, (log_box_x + 20, line_y), (log_box_x + log_box_width - 20, line_y), 2)

            # 显示最近的事件（最多5条），确保文字在框内
            log_y = line_y + 15
            max_width = log_box_width - 40  # 左右各留20像素边距

            for log_entry in self.event_log[-5:]:
                # 如果文字太长，截断
                log_surf = TINY_FONT.render(log_entry, True, BLACK)

                # 如果文字超出宽度，逐步缩短
                if log_surf.get_width() > max_width:
                    parts = log_entry.split(': ')
                    if len(parts) >= 2:
                        # 尝试不同长度
                        for length in [10, 8, 6, 4]:
                            short_text = f"{parts[0][:6]}: {parts[1][:length]}..."
                            log_surf = TINY_FONT.render(short_text, True, BLACK)
                            if log_surf.get_width() <= max_width:
                                break

                self.screen.blit(log_surf, (log_box_x + 20, log_y))
                log_y += 45

                # 确保不超出框的底部
                if log_y > log_box_y + log_box_height - 30:
                    break

    def draw_dice(self):
        """绘制骰子"""
        if self.dice_animating:
            # 动画中，随机显示骰子
            dice_index = random.randint(0, 5)
            dice_img = self.dice_images[dice_index]
        else:
            # 显示最终结果
            dice_img = self.dice_images[self.dice_result - 1]

        dice_x = WINDOW_WIDTH // 2 - 100
        dice_y = 300
        self.screen.blit(dice_img, (dice_x, dice_y))

        if self.dice_animating:
            hint_text = TEXT_FONT.render("投掷骰子中...", True, RED)
            self.screen.blit(hint_text, (WINDOW_WIDTH // 2 - hint_text.get_width() // 2, 520))
        else:
            result_text = TEXT_FONT.render(f"获得 {self.dice_result} 点资源", True, BLUE)
            self.screen.blit(result_text, (WINDOW_WIDTH // 2 - result_text.get_width() // 2, 520))

    def draw_resource_choice(self):
        """绘制资源选择界面"""
        hint_text = SMALL_FONT.render("请选择分配资源：", True, BLACK)
        self.screen.blit(hint_text, (WINDOW_WIDTH // 2 - hint_text.get_width() // 2, 560))

        # 三个选项按钮（使用横板选项框）
        button_width = 250
        button_height = 80
        button_spacing = 40
        start_x = WINDOW_WIDTH // 2 - (button_width * 3 + button_spacing * 2) // 2
        button_y = 610

        choices = [
            ("粮食", "food", GREEN),
            ("防御", "defense", BLUE),
            ("科技", "tech", ORANGE)
        ]

        mouse_pos = pygame.mouse.get_pos()

        for i, (label, resource_type, color) in enumerate(choices):
            button_x = start_x + i * (button_width + button_spacing)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            # 存储按钮信息供点击检测
            if not hasattr(self, 'resource_buttons'):
                self.resource_buttons = {}
            self.resource_buttons[resource_type] = button_rect

            # 使用UI素材或绘制按钮
            is_hover = button_rect.collidepoint(mouse_pos)

            if self.ui_images.get('option_h'):
                option_img = self.ui_images['option_h']
                option_img = pygame.transform.scale(option_img, (button_width, button_height))
                self.screen.blit(option_img, (button_x, button_y))
                # 如果鼠标悬停，添加高亮效果
                if is_hover:
                    highlight = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
                    highlight.fill((255, 255, 255, 80))
                    self.screen.blit(highlight, (button_x, button_y))
                text_color = BLACK if not is_hover else color
            else:
                if is_hover:
                    pygame.draw.rect(self.screen, color, button_rect, border_radius=8)
                    text_color = WHITE
                else:
                    pygame.draw.rect(self.screen, WHITE, button_rect, border_radius=8)
                    pygame.draw.rect(self.screen, color, button_rect, 3, border_radius=8)
                    text_color = color

            text = TEXT_FONT.render(label, True, text_color)
            self.screen.blit(text, (button_x + button_width // 2 - text.get_width() // 2,
                                   button_y + button_height // 2 - text.get_height() // 2))

    def draw_event(self):
        """绘制事件界面"""
        if not self.current_event:
            return

        # 大标题：随机事件
        event_header = EVENT_FONT.render("随机事件发生！", True, RED)
        self.screen.blit(event_header, (WINDOW_WIDTH // 2 - event_header.get_width() // 2, int(WINDOW_HEIGHT * 0.15)))

        # 更新并绘制GIF动画
        if self.current_event.gif_frames and len(self.current_event.gif_frames) > 0:
            # 更新帧计数器
            self.current_event.frame_counter += 1
            if self.current_event.frame_counter >= self.current_event.frame_delay:
                self.current_event.frame_counter = 0
                self.current_event.current_frame = (self.current_event.current_frame + 1) % len(self.current_event.gif_frames)

            # 绘制当前帧
            current_frame = self.current_event.gif_frames[self.current_event.current_frame]
            event_x = WINDOW_WIDTH // 2 - 200
            event_y = int(WINDOW_HEIGHT * 0.3)
            self.screen.blit(current_frame, (event_x, event_y))
        else:
            # 如果没有图片，显示占位框
            event_y = int(WINDOW_HEIGHT * 0.3)
            pygame.draw.rect(self.screen, LIGHT_BLUE, (WINDOW_WIDTH // 2 - 200, event_y, 400, 300), border_radius=10)
            pygame.draw.rect(self.screen, BLACK, (WINDOW_WIDTH // 2 - 200, event_y, 400, 300), 2, border_radius=10)
            # 在占位框中显示事件名称
            placeholder_text = EVENT_FONT.render(self.current_event.name, True, BLACK)
            self.screen.blit(placeholder_text, (WINDOW_WIDTH // 2 - placeholder_text.get_width() // 2, event_y + 130))

        # 事件名称和人口变化（使用文字框背景）
        title_y = int(WINDOW_HEIGHT * 0.75)
        text_box_width = int(WINDOW_WIDTH * 0.5)
        text_box_height = 100
        if self.ui_images.get('text_box'):
            text_box_img = self.ui_images['text_box']
            text_box_img = pygame.transform.scale(text_box_img, (text_box_width, text_box_height))
            self.screen.blit(text_box_img, (WINDOW_WIDTH // 2 - text_box_width // 2, title_y))
        else:
            pygame.draw.rect(self.screen, LIGHT_BLUE, (WINDOW_WIDTH // 2 - text_box_width // 2, title_y, text_box_width, text_box_height), border_radius=10)
            pygame.draw.rect(self.screen, BLACK, (WINDOW_WIDTH // 2 - text_box_width // 2, title_y, text_box_width, text_box_height), 2, border_radius=10)

        # 事件名称和人口变化在同一行
        event_title = EVENT_FONT.render(self.current_event.name, True, RED)
        pop_change_text = f"  人口{self.current_event.population_change:+d}"
        pop_change_color = GREEN if self.current_event.population_change > 0 else RED
        pop_surf = EVENT_FONT.render(pop_change_text, True, pop_change_color)

        # 计算总宽度并居中
        total_width = event_title.get_width() + pop_surf.get_width()
        start_x = WINDOW_WIDTH // 2 - total_width // 2

        # 确保在框内
        if start_x < WINDOW_WIDTH // 2 - text_box_width // 2 + 20:
            start_x = WINDOW_WIDTH // 2 - text_box_width // 2 + 20

        self.screen.blit(event_title, (start_x, title_y + 30))
        self.screen.blit(pop_surf, (start_x + event_title.get_width(), title_y + 30))

        # 按空格继续提示（闪烁效果）
        hint_y = int(WINDOW_HEIGHT * 0.9)
        # 使用帧数实现闪烁效果
        if (pygame.time.get_ticks() // 500) % 2 == 0:  # 每500ms切换一次
            hint = TEXT_FONT.render("按空格键继续...", True, YELLOW)
            self.screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, hint_y))

    def draw_ending_screen(self):
        """绘制结局界面"""
        if not self.ending_type:
            return

        # 绘制结局图片
        ending_img = self.ending_images.get(self.ending_type)
        if ending_img:
            img_x = WINDOW_WIDTH // 2 - 400
            img_y = 80
            self.screen.blit(ending_img, (img_x, img_y))

        # 结局标题
        title_y = int(WINDOW_HEIGHT * 0.65)
        ending_title = TITLE_FONT.render(self.ending_type, True, BLUE)
        self.screen.blit(ending_title, (WINDOW_WIDTH // 2 - ending_title.get_width() // 2, title_y))

        # 最终数据（使用文字框背景）
        stats_y = int(WINDOW_HEIGHT * 0.72)
        stats_box_width = int(WINDOW_WIDTH * 0.5)
        stats_box_height = 120
        if self.ui_images.get('text_box'):
            stats_box = self.ui_images['text_box']
            stats_box = pygame.transform.scale(stats_box, (stats_box_width, stats_box_height))
            self.screen.blit(stats_box, (WINDOW_WIDTH // 2 - stats_box_width // 2, stats_y))
        else:
            pygame.draw.rect(self.screen, LIGHT_BLUE, (WINDOW_WIDTH // 2 - stats_box_width // 2, stats_y, stats_box_width, stats_box_height), border_radius=10)
            pygame.draw.rect(self.screen, BLACK, (WINDOW_WIDTH // 2 - stats_box_width // 2, stats_y, stats_box_width, stats_box_height), 2, border_radius=10)

        final_stats = [
            f"最终人口: {self.race.population}",
            f"粮食: {self.race.food}  |  防御: {self.race.defense}  |  科技: {self.race.tech}"
        ]

        # 文字在框内，留出边距
        y = stats_y + 25
        for stat in final_stats:
            surf = TEXT_FONT.render(stat, True, BLACK)
            x = WINDOW_WIDTH // 2 - surf.get_width() // 2
            # 确保在框内，左右各留20像素边距
            min_x = WINDOW_WIDTH // 2 - stats_box_width // 2 + 20
            max_x = WINDOW_WIDTH // 2 + stats_box_width // 2 - surf.get_width() - 20
            if x < min_x:
                x = min_x
            elif x > max_x:
                x = max_x
            self.screen.blit(surf, (x, y))
            y += 40

        # 重新开始按钮（下移）
        button_width = int(WINDOW_WIDTH * 0.12)
        button_height = int(WINDOW_HEIGHT * 0.06)
        button_y = int(WINDOW_HEIGHT * 0.88)
        restart_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - button_width - 20, button_y, button_width, button_height)
        exit_button_rect = pygame.Rect(WINDOW_WIDTH // 2 + 20, button_y, button_width, button_height)

        # 存储按钮供点击检测
        self.restart_button_rect = restart_button_rect
        self.exit_button_rect = exit_button_rect

        mouse_pos = pygame.mouse.get_pos()

        # 重新开始按钮
        if restart_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, GREEN, restart_button_rect, border_radius=8)
            text_color = WHITE
        else:
            pygame.draw.rect(self.screen, WHITE, restart_button_rect, border_radius=8)
            pygame.draw.rect(self.screen, GREEN, restart_button_rect, 3, border_radius=8)
            text_color = GREEN

        restart_text = TEXT_FONT.render("重新开始", True, text_color)
        self.screen.blit(restart_text, (restart_button_rect.x + button_width // 2 - restart_text.get_width() // 2,
                                       restart_button_rect.y + button_height // 2 - restart_text.get_height() // 2))

        # 退出按钮
        if exit_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, RED, exit_button_rect, border_radius=8)
            text_color = WHITE
        else:
            pygame.draw.rect(self.screen, WHITE, exit_button_rect, border_radius=8)
            pygame.draw.rect(self.screen, RED, exit_button_rect, 3, border_radius=8)
            text_color = RED

        exit_text = TEXT_FONT.render("退出游戏", True, text_color)
        self.screen.blit(exit_text, (exit_button_rect.x + button_width // 2 - exit_text.get_width() // 2,
                                    exit_button_rect.y + button_height // 2 - exit_text.get_height() // 2))

    def reset_game(self):
        """重置游戏"""
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

    def run(self):
        """游戏主循环"""
        running = True
        while running:
            self.clock.tick(FPS)

            # 更新骰子动画
            if self.state == "DICE":
                self.update_dice_animation()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    # ESC键退出游戏（任何界面都可以）
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif self.state == "EVENT":
                        # 空格键继续下一回合
                        if event.key == pygame.K_SPACE:
                            self.next_round()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if self.state == "START":
                        # 检查开始按钮
                        if hasattr(self, 'start_button_rect') and self.start_button_rect.collidepoint(mouse_pos):
                            self.start_game()

                    elif self.state == "RESOURCE_CHOICE":
                        # 检查资源选择按钮
                        if hasattr(self, 'resource_buttons'):
                            for resource_type, button_rect in self.resource_buttons.items():
                                if button_rect.collidepoint(mouse_pos):
                                    self.allocate_resource(resource_type)
                                    break

                    elif self.state == "GAME_OVER":
                        # 检查结局界面按钮
                        if hasattr(self, 'restart_button_rect') and self.restart_button_rect.collidepoint(mouse_pos):
                            self.reset_game()
                        elif hasattr(self, 'exit_button_rect') and self.exit_button_rect.collidepoint(mouse_pos):
                            running = False

            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()

