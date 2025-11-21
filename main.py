import pygame
import random
import sys
import os

# 初始化 Pygame
pygame.init()

# 常量定义
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
FPS = 60
MAX_ROUNDS = 5
DICE_ANIMATION_FRAMES = 20  # 骰子动画帧数
DICE_ANIMATION_SPEED = 3    # 骰子动画速度

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
BLUE = (50, 100, 200)
YELLOW = (220, 200, 50)

# 字体设置
pygame.font.init()
# 使用系统中文字体
try:
    # Windows 系统字体
    TITLE_FONT = pygame.font.SysFont('microsoftyahei', 48)
    EVENT_FONT = pygame.font.SysFont('microsoftyahei', 36)
    TEXT_FONT = pygame.font.SysFont('microsoftyahei', 28)
    SMALL_FONT = pygame.font.SysFont('microsoftyahei', 24)
except:
    # 备用字体
    try:
        TITLE_FONT = pygame.font.SysFont('simsun', 48)
        EVENT_FONT = pygame.font.SysFont('simsun', 36)
        TEXT_FONT = pygame.font.SysFont('simsun', 28)
        SMALL_FONT = pygame.font.SysFont('simsun', 24)
    except:
        # 最后备用
        TITLE_FONT = pygame.font.Font(None, 48)
        EVENT_FONT = pygame.font.Font(None, 36)
        TEXT_FONT = pygame.font.Font(None, 28)
        SMALL_FONT = pygame.font.Font(None, 24)


class Race:
    """短命种族类"""
    def __init__(self):
        self.population = 100
        self.generation = 1
        self.round = 1
        self.traits = []  # 进化特性
        self.food = 50
        self.shelter = False
        
    def add_trait(self, trait):
        if trait not in self.traits:
            self.traits.append(trait)
    
    def is_alive(self):
        return self.population > 0


class Event:
    """事件类"""
    def __init__(self, title, description, choices):
        self.title = title
        self.description = description
        self.choices = choices  # [(选项文本, 效果函数), ...]


class Game:
    """游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("短命种族模拟器")
        self.clock = pygame.time.Clock()
        self.race = Race()
        self.current_event = None
        self.event_log = []
        self.game_over = False
        self.victory = False

        # 骰子相关
        self.dice_images = self.load_dice_images()
        self.dice_animating = False
        self.dice_animation_frame = 0
        self.dice_result = 1
        self.show_choices = False  # 是否显示选项
        self.auto_result_text = ""  # 自动执行结果文本
        self.waiting_for_next = False  # 等待进入下一回合

    def load_dice_images(self):
        """加载骰子图片"""
        dice_images = []
        for i in range(1, 7):
            try:
                img_path = os.path.join("static", "骰子", f"{i}.png")
                img = pygame.image.load(img_path)
                # 调整骰子大小
                img = pygame.transform.scale(img, (150, 150))
                dice_images.append(img)
            except Exception as e:
                print(f"加载骰子图片 {i}.png 失败: {e}")
                # 创建一个简单的占位图
                placeholder = pygame.Surface((150, 150))
                placeholder.fill(WHITE)
                pygame.draw.rect(placeholder, BLACK, (0, 0, 150, 150), 3)
                font = pygame.font.Font(None, 72)
                text = font.render(str(i), True, BLACK)
                placeholder.blit(text, (60, 40))
                dice_images.append(placeholder)
        return dice_images
        
    def create_events(self):
        """创建所有可能的事件"""
        events = []
        
        # 环境事件
        events.append(Event(
            "寒冬来袭",
            "刺骨的寒风席卷而来，种群面临严峻考验...",
            [
                ("聚集取暖", lambda: self.effect_winter_huddle()),
                ("寻找洞穴", lambda: self.effect_find_cave()),
                ("继续觅食", lambda: self.effect_keep_foraging())
            ]
        ))
        
        events.append(Event(
            "干旱",
            "水源枯竭，食物变得稀缺...",
            [
                ("迁徙寻找水源", lambda: self.effect_migrate()),
                ("节约资源", lambda: self.effect_conserve()),
                ("挖掘地下水", lambda: self.effect_dig_water())
            ]
        ))
        
        events.append(Event(
            "洪水",
            "暴雨引发洪水，栖息地被淹没...",
            [
                ("爬上高地", lambda: self.effect_high_ground()),
                ("建造木筏", lambda: self.effect_build_raft()),
                ("原地等待", lambda: self.effect_wait_flood())
            ]
        ))
        
        events.append(Event(
            "食物丰收",
            "发现了大片果树林，食物充足！",
            [
                ("大量储存", lambda: self.effect_store_food()),
                ("立即繁殖", lambda: self.effect_breed_now()),
                ("继续探索", lambda: self.effect_explore_more())
            ]
        ))
        
        # 捕食者事件
        events.append(Event(
            "猛兽袭击",
            "一群饥饿的猛兽盯上了你的种群！",
            [
                ("正面对抗", lambda: self.effect_fight_beast()),
                ("快速逃跑", lambda: self.effect_flee()),
                ("分散隐藏", lambda: self.effect_hide())
            ]
        ))
        
        events.append(Event(
            "天敌出现",
            "天空中盘旋着巨大的猛禽...",
            [
                ("躲入地下", lambda: self.effect_underground()),
                ("伪装自己", lambda: self.effect_camouflage()),
                ("群体防御", lambda: self.effect_group_defense())
            ]
        ))
        
        # 繁殖事件
        events.append(Event(
            "繁殖季节",
            "种群进入繁殖期，这是增加数量的好机会！",
            [
                ("大量繁殖", lambda: self.effect_mass_breed()),
                ("精英繁殖", lambda: self.effect_elite_breed()),
                ("延迟繁殖", lambda: self.effect_delay_breed())
            ]
        ))
        
        # 进化/突变事件
        events.append(Event(
            "基因突变",
            "部分个体出现了奇特的变化...",
            [
                ("培育厚毛皮", lambda: self.effect_thick_fur()),
                ("发展利爪", lambda: self.effect_claws()),
                ("增强速度", lambda: self.effect_speed())
            ]
        ))
        
        events.append(Event(
            "进化机遇",
            "环境压力促使种群快速进化...",
            [
                ("体型变大", lambda: self.effect_larger_size()),
                ("智力提升", lambda: self.effect_intelligence()),
                ("适应环境", lambda: self.effect_adaptation())
            ]
        ))
        
        # 生存挑战
        events.append(Event(
            "饥饿危机",
            "食物储备告急，种群陷入饥荒...",
            [
                ("狩猎冒险", lambda: self.effect_risky_hunt()),
                ("减少进食", lambda: self.effect_ration()),
                ("寻找新食物", lambda: self.effect_new_food())
            ]
        ))
        
        events.append(Event(
            "疾病爆发",
            "一种未知疾病在种群中蔓延...",
            [
                ("隔离病患", lambda: self.effect_quarantine()),
                ("寻找草药", lambda: self.effect_medicine()),
                ("自然淘汰", lambda: self.effect_natural_selection())
            ]
        ))
        
        return events
    
    # 效果函数
    def effect_winter_huddle(self):
        loss = max(10, int(self.race.population * 0.1))
        if "厚毛皮" in self.race.traits:
            loss = loss // 2
        self.race.population -= loss
        return f"聚集取暖，损失了 {loss} 个体"
    
    def effect_find_cave(self):
        if random.random() < 0.6:
            self.race.shelter = True
            loss = max(5, int(self.race.population * 0.05))
            self.race.population -= loss
            return f"找到了庇护所！损失 {loss} 个体"
        else:
            loss = max(15, int(self.race.population * 0.15))
            self.race.population -= loss
            return f"没找到合适的洞穴，损失 {loss} 个体"
    
    def effect_keep_foraging(self):
        self.race.food += 10
        loss = max(20, int(self.race.population * 0.2))
        self.race.population -= loss
        return f"获得食物 +10，但损失了 {loss} 个体"
    
    def effect_migrate(self):
        if random.random() < 0.5:
            self.race.food += 20
            loss = max(10, int(self.race.population * 0.1))
            self.race.population -= loss
            return f"成功找到水源！食物 +20，损失 {loss} 个体"
        else:
            loss = max(25, int(self.race.population * 0.25))
            self.race.population -= loss
            return f"迁徙失败，损失惨重 -{loss} 个体"
    
    def effect_conserve(self):
        self.race.food = max(0, self.race.food - 5)
        loss = max(8, int(self.race.population * 0.08))
        self.race.population -= loss
        return f"节约资源，食物 -5，损失 {loss} 个体"
    
    def effect_dig_water(self):
        if random.random() < 0.4:
            self.race.food += 15
            return f"挖到地下水！食物 +15"
        else:
            loss = max(12, int(self.race.population * 0.12))
            self.race.population -= loss
            return f"挖掘失败，浪费体力，损失 {loss} 个体"
    
    def effect_high_ground(self):
        loss = max(5, int(self.race.population * 0.05))
        self.race.population -= loss
        return f"成功避开洪水，损失 {loss} 个体"
    
    def effect_build_raft(self):
        if "智力提升" in self.race.traits:
            self.race.food += 10
            return f"成功建造木筏！食物 +10"
        else:
            loss = max(15, int(self.race.population * 0.15))
            self.race.population -= loss
            return f"建造失败，损失 {loss} 个体"
    
    def effect_wait_flood(self):
        loss = max(30, int(self.race.population * 0.3))
        self.race.population -= loss
        return f"洪水造成重大损失 -{loss} 个体"
    
    def effect_store_food(self):
        self.race.food += 30
        return f"储存大量食物 +30"
    
    def effect_breed_now(self):
        gain = max(20, int(self.race.population * 0.3))
        self.race.population += gain
        self.race.food -= 10
        return f"种群增长 +{gain}，食物 -10"
    
    def effect_explore_more(self):
        if random.random() < 0.5:
            self.race.food += 40
            return f"发现更多资源！食物 +40"
        else:
            self.race.food += 15
            return f"探索收获一般，食物 +15"
    
    def effect_fight_beast(self):
        if "利爪" in self.race.traits or "体型变大" in self.race.traits:
            loss = max(10, int(self.race.population * 0.1))
            self.race.population -= loss
            self.race.food += 20
            return f"击退猛兽！损失 {loss} 个体，获得食物 +20"
        else:
            loss = max(35, int(self.race.population * 0.35))
            self.race.population -= loss
            return f"战斗失败，损失惨重 -{loss} 个体"
    
    def effect_flee(self):
        if "速度提升" in self.race.traits:
            loss = max(5, int(self.race.population * 0.05))
            self.race.population -= loss
            return f"快速逃脱！仅损失 {loss} 个体"
        else:
            loss = max(20, int(self.race.population * 0.2))
            self.race.population -= loss
            return f"逃跑中损失 {loss} 个体"
    
    def effect_hide(self):
        loss = max(12, int(self.race.population * 0.12))
        self.race.population -= loss
        return f"成功隐藏，损失 {loss} 个体"
    
    def effect_underground(self):
        if self.race.shelter:
            loss = max(3, int(self.race.population * 0.03))
            self.race.population -= loss
            return f"利用庇护所躲避，仅损失 {loss} 个体"
        else:
            loss = max(15, int(self.race.population * 0.15))
            self.race.population -= loss
            return f"匆忙躲藏，损失 {loss} 个体"
    
    def effect_camouflage(self):
        if random.random() < 0.6:
            loss = max(5, int(self.race.population * 0.05))
            self.race.population -= loss
            return f"伪装成功！损失 {loss} 个体"
        else:
            loss = max(18, int(self.race.population * 0.18))
            self.race.population -= loss
            return f"伪装失败，损失 {loss} 个体"
    
    def effect_group_defense(self):
        loss = max(10, int(self.race.population * 0.1))
        self.race.population -= loss
        return f"群体防御，损失 {loss} 个体"
    
    def effect_mass_breed(self):
        if self.race.food >= 20:
            gain = max(40, int(self.race.population * 0.5))
            self.race.population += gain
            self.race.food -= 20
            return f"大量繁殖成功！种群 +{gain}，食物 -20"
        else:
            return f"食物不足，繁殖失败"
    
    def effect_elite_breed(self):
        gain = max(15, int(self.race.population * 0.2))
        self.race.population += gain
        self.race.food -= 10
        return f"精英繁殖，种群 +{gain}，食物 -10"
    
    def effect_delay_breed(self):
        self.race.food += 10
        return f"延迟繁殖，节省食物 +10"
    
    def effect_thick_fur(self):
        self.race.add_trait("厚毛皮")
        return f"进化出厚毛皮！抗寒能力提升"
    
    def effect_claws(self):
        self.race.add_trait("利爪")
        return f"进化出利爪！战斗力提升"
    
    def effect_speed(self):
        self.race.add_trait("速度提升")
        return f"速度大幅提升！逃生能力增强"
    
    def effect_larger_size(self):
        self.race.add_trait("体型变大")
        self.race.food -= 15
        return f"体型变大！战斗力提升，食物 -15"
    
    def effect_intelligence(self):
        self.race.add_trait("智力提升")
        return f"智力提升！解决问题能力增强"
    
    def effect_adaptation(self):
        self.race.add_trait("环境适应")
        return f"获得环境适应能力！"
    
    def effect_risky_hunt(self):
        if random.random() < 0.5:
            self.race.food += 25
            loss = max(8, int(self.race.population * 0.08))
            self.race.population -= loss
            return f"狩猎成功！食物 +25，损失 {loss} 个体"
        else:
            loss = max(20, int(self.race.population * 0.2))
            self.race.population -= loss
            return f"狩猎失败，损失 {loss} 个体"
    
    def effect_ration(self):
        loss = max(15, int(self.race.population * 0.15))
        self.race.population -= loss
        return f"减少进食，损失 {loss} 个体"
    
    def effect_new_food(self):
        if random.random() < 0.6:
            self.race.food += 20
            return f"发现新食物来源！食物 +20"
        else:
            loss = max(10, int(self.race.population * 0.1))
            self.race.population -= loss
            return f"寻找失败，损失 {loss} 个体"
    
    def effect_quarantine(self):
        loss = max(12, int(self.race.population * 0.12))
        self.race.population -= loss
        return f"隔离病患，控制疫情，损失 {loss} 个体"
    
    def effect_medicine(self):
        if "智力提升" in self.race.traits:
            loss = max(5, int(self.race.population * 0.05))
            self.race.population -= loss
            return f"找到草药治疗！仅损失 {loss} 个体"
        else:
            loss = max(15, int(self.race.population * 0.15))
            self.race.population -= loss
            return f"草药效果有限，损失 {loss} 个体"
    
    def effect_natural_selection(self):
        loss = max(25, int(self.race.population * 0.25))
        self.race.population -= loss
        if random.random() < 0.3:
            self.race.add_trait("抗病能力")
            return f"自然淘汰，损失 {loss} 个体，但获得抗病能力"
        else:
            return f"自然淘汰，损失 {loss} 个体"
    
    def start_dice_animation(self):
        """开始骰子动画"""
        self.dice_animating = True
        self.dice_animation_frame = 0
        self.dice_result = random.randint(1, 6)
        self.show_choices = False
        self.auto_result_text = ""
        self.waiting_for_next = False

    def update_dice_animation(self):
        """更新骰子动画"""
        if self.dice_animating:
            self.dice_animation_frame += 1
            if self.dice_animation_frame >= DICE_ANIMATION_FRAMES:
                # 动画结束
                self.dice_animating = False
                # 40%概率显示选项
                if random.random() < 0.4:
                    self.show_choices = True
                else:
                    # 自动执行随机选项
                    self.auto_execute_choice()

    def auto_execute_choice(self):
        """自动执行随机选项"""
        if self.current_event:
            choice_index = random.randint(0, len(self.current_event.choices) - 1)
            choice_text, effect_func = self.current_event.choices[choice_index]
            result = effect_func()
            self.auto_result_text = f"骰子决定: {choice_text}\n结果: {result}"
            self.event_log.append(f"{self.current_event.title}: {result}")

            # 检查种族是否存活
            if not self.race.is_alive():
                self.game_over = True
                self.event_log.append("种族灭绝...")
            else:
                self.waiting_for_next = True

    def next_round(self):
        """进入下一回合"""
        self.race.round += 1
        if self.race.round > MAX_ROUNDS:
            # 新一代
            self.race.generation += 1
            self.race.round = 1
            # 繁殖新一代
            if self.race.food >= 10:
                new_pop = max(50, int(self.race.population * 0.8))
                self.race.population = new_pop
                self.race.food -= 10
                self.event_log.append(f"第 {self.race.generation} 代诞生！种群: {new_pop}")
            else:
                self.game_over = True
                self.event_log.append("食物不足，种族灭绝...")
                return

        # 检查胜利条件
        if self.race.generation >= 10:
            self.victory = True
            self.game_over = True
            return

        # 随机事件
        self.current_event = random.choice(self.create_events())
        # 开始骰子动画
        self.start_dice_animation()
    
    def draw(self):
        """绘制游戏界面"""
        self.screen.fill(WHITE)

        # 标题
        title = TITLE_FONT.render("短命种族模拟器", True, BLACK)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 20))

        # 状态栏
        y_offset = 80
        status_texts = [
            f"第 {self.race.generation} 代  |  回合: {self.race.round}/{MAX_ROUNDS}",
            f"种群数量: {self.race.population}",
            f"食物储备: {self.race.food}",
            f"进化特性: {', '.join(self.race.traits) if self.race.traits else '无'}"
        ]

        for text in status_texts:
            surf = TEXT_FONT.render(text, True, BLUE)
            self.screen.blit(surf, (50, y_offset))
            y_offset += 35

        # 绘制骰子
        if self.dice_animating:
            # 动画中，随机显示骰子
            dice_index = random.randint(0, 5)
            dice_img = self.dice_images[dice_index]
        else:
            # 显示最终结果
            dice_img = self.dice_images[self.dice_result - 1]

        dice_x = WINDOW_WIDTH // 2 - 75
        dice_y = 220
        self.screen.blit(dice_img, (dice_x, dice_y))
        
        # 游戏结束界面
        if self.game_over:
            pygame.draw.rect(self.screen, DARK_GRAY, (150, 250, 700, 300))
            pygame.draw.rect(self.screen, BLACK, (150, 250, 700, 300), 3)

            if self.victory:
                end_text = EVENT_FONT.render("胜利！种族存活了10代！", True, GREEN)
            else:
                end_text = EVENT_FONT.render("游戏结束 - 种族灭绝", True, RED)

            self.screen.blit(end_text, (WINDOW_WIDTH // 2 - end_text.get_width() // 2, 300))

            final_stats = [
                f"最终代数: {self.race.generation}",
                f"最终种群: {self.race.population}",
                f"进化特性: {len(self.race.traits)} 个"
            ]

            y = 360
            for stat in final_stats:
                surf = TEXT_FONT.render(stat, True, WHITE)
                self.screen.blit(surf, (WINDOW_WIDTH // 2 - surf.get_width() // 2, y))
                y += 40

            restart_text = SMALL_FONT.render("按 R 重新开始 | 按 ESC 退出", True, YELLOW)
            self.screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, 500))

            pygame.display.flip()
            return

        # 骰子动画提示
        if self.dice_animating:
            hint_text = TEXT_FONT.render("投掷骰子中...", True, RED)
            self.screen.blit(hint_text, (WINDOW_WIDTH // 2 - hint_text.get_width() // 2, 390))
            pygame.display.flip()
            return
        
        # 当前事件
        if self.current_event:
            # 事件标题
            event_title = EVENT_FONT.render(self.current_event.title, True, RED)
            self.screen.blit(event_title, (WINDOW_WIDTH // 2 - event_title.get_width() // 2, 400))

            # 事件描述
            desc = TEXT_FONT.render(self.current_event.description, True, BLACK)
            self.screen.blit(desc, (WINDOW_WIDTH // 2 - desc.get_width() // 2, 450))

            # 显示选项或自动结果
            if self.show_choices:
                # 显示选项按钮
                y_pos = 500
                for i, (choice_text, _) in enumerate(self.current_event.choices):
                    button_rect = pygame.Rect(150, y_pos, 700, 50)
                    mouse_pos = pygame.mouse.get_pos()

                    if button_rect.collidepoint(mouse_pos):
                        pygame.draw.rect(self.screen, GREEN, button_rect)
                    else:
                        pygame.draw.rect(self.screen, DARK_GRAY, button_rect)

                    pygame.draw.rect(self.screen, BLACK, button_rect, 2)

                    choice_surf = TEXT_FONT.render(f"{i+1}. {choice_text}", True, WHITE)
                    self.screen.blit(choice_surf, (button_rect.x + 20, button_rect.y + 12))

                    y_pos += 70
            elif self.waiting_for_next:
                # 显示自动执行结果
                lines = self.auto_result_text.split('\n')
                y_pos = 500
                for line in lines:
                    result_surf = TEXT_FONT.render(line, True, BLUE)
                    self.screen.blit(result_surf, (WINDOW_WIDTH // 2 - result_surf.get_width() // 2, y_pos))
                    y_pos += 40

                # 提示按空格继续
                hint = SMALL_FONT.render("按空格键继续...", True, YELLOW)
                self.screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 620))

        pygame.display.flip()
    
    def handle_choice(self, choice_index):
        """处理玩家选择"""
        if self.current_event and 0 <= choice_index < len(self.current_event.choices):
            _, effect_func = self.current_event.choices[choice_index]
            result = effect_func()
            self.event_log.append(f"{self.current_event.title}: {result}")
            
            # 检查种族是否存活
            if not self.race.is_alive():
                self.game_over = True
                self.event_log.append("种族灭绝...")
            else:
                self.next_round()
    
    def run(self):
        """游戏主循环"""
        self.next_round()  # 开始第一个事件

        running = True
        while running:
            self.clock.tick(FPS)

            # 更新骰子动画
            self.update_dice_animation()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:
                            # 重新开始
                            self.race = Race()
                            self.event_log = []
                            self.game_over = False
                            self.victory = False
                            self.next_round()
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                    else:
                        # 空格键继续下一回合
                        if event.key == pygame.K_SPACE and self.waiting_for_next:
                            self.next_round()
                        # 数字键选择（仅在显示选项时）
                        elif self.show_choices:
                            if event.key == pygame.K_1:
                                self.handle_choice(0)
                            elif event.key == pygame.K_2:
                                self.handle_choice(1)
                            elif event.key == pygame.K_3:
                                self.handle_choice(2)

                if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and self.show_choices:
                    mouse_pos = pygame.mouse.get_pos()
                    # 检查按钮点击
                    y_pos = 500
                    for i in range(len(self.current_event.choices) if self.current_event else 0):
                        button_rect = pygame.Rect(150, y_pos, 700, 50)
                        if button_rect.collidepoint(mouse_pos):
                            self.handle_choice(i)
                            break
                        y_pos += 70

            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()

