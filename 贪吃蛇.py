"""
贪吃蛇小游戏
依赖包安装：pip install pygame
音效文件要求：将 eat.wav 和 game_over.wav 放在与本文件同目录下
"""

import tkinter as tk
import random
import os
import sys

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("提示：未安装pygame，音效功能不可用。安装命令：pip install pygame")


class SnakeGame:
    """
    贪吃蛇游戏主类
    包含游戏初始化、绘制、控制、碰撞检测等所有功能模块
    """

    def __init__(self, master):
        """
        初始化游戏参数和界面元素
        :param master: Tkinter根窗口
        """
        self.master = master
        self.master.title("贪吃蛇小游戏")
        self.master.resizable(False, False)

        self.WINDOW_WIDTH = 600
        self.WINDOW_HEIGHT = 650
        self.GAME_AREA_HEIGHT = 600
        self.CELL_SIZE = 20
        self.COLUMNS = self.WINDOW_WIDTH // self.CELL_SIZE
        self.ROWS = self.GAME_AREA_HEIGHT // self.CELL_SIZE

        self.master.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")

        self.setup_audio()

        self.speed = 200
        self.score = 0
        self.high_score = 0
        self.is_paused = False
        self.game_over_flag = False

        self.load_high_score()

        self.create_control_panel()

        self.canvas = tk.Canvas(
            self.master,
            width=self.WINDOW_WIDTH,
            height=self.GAME_AREA_HEIGHT,
            bg="#222222"
        )
        self.canvas.pack()

        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.food = self.spawn_food()

        self.bind_keys()
        self.update_game()

    def setup_audio(self):
        """
        初始化音频系统，处理音效文件缺失情况
        """
        self.eat_sound = None
        self.game_over_sound = None

        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                if os.path.exists("eat.wav"):
                    self.eat_sound = pygame.mixer.Sound("eat.wav")
                if os.path.exists("game_over.wav"):
                    self.game_over_sound = pygame.mixer.Sound("game_over.wav")
            except Exception as e:
                print(f"音频初始化失败: {e}")

    def create_control_panel(self):
        """
        创建顶部控制面板：难度按钮、分数显示、最高分显示
        """
        control_frame = tk.Frame(self.master, bg="#333333", height=50)
        control_frame.pack(fill=tk.X, side=tk.TOP)
        control_frame.pack_propagate(False)

        btn_style = {
            "font": ("Arial", 12, "bold"),
            "width": 8,
            "relief": tk.FLAT,
            "activebackground": "#555555"
        }

        tk.Button(control_frame, text="简单", bg="#4CAF50", fg="white",
                  command=lambda: self.set_speed(300), **btn_style).pack(side=tk.LEFT, padx=5, pady=8)
        tk.Button(control_frame, text="中等", bg="#FF9800", fg="white",
                  command=lambda: self.set_speed(200), **btn_style).pack(side=tk.LEFT, padx=5, pady=8)
        tk.Button(control_frame, text="困难", bg="#F44336", fg="white",
                  command=lambda: self.set_speed(100), **btn_style).pack(side=tk.LEFT, padx=5, pady=8)

        self.score_label = tk.Label(control_frame, text="分数: 0",
                                    font=("Arial", 14, "bold"), bg="#333333", fg="white")
        self.score_label.pack(side=tk.LEFT, padx=30, pady=8)

        self.high_score_label = tk.Label(control_frame, text=f"最高分: {self.high_score}",
                                         font=("Arial", 14, "bold"), bg="#333333", fg="yellow")
        self.high_score_label.pack(side=tk.RIGHT, padx=30, pady=8)

    def load_high_score(self):
        """
        读取本地最高分记录，文件不存在时自动创建并初始化
        """
        try:
            if os.path.exists("snake_high_score.txt"):
                with open("snake_high_score.txt", "r") as f:
                    self.high_score = int(f.read().strip())
            else:
                self.high_score = 0
                with open("snake_high_score.txt", "w") as f:
                    f.write("0")
        except Exception as e:
            print(f"读取最高分失败: {e}")
            self.high_score = 0

    def save_high_score(self):
        """
        保存最高分到本地文件
        """
        try:
            with open("snake_high_score.txt", "w") as f:
                f.write(str(self.high_score))
        except Exception as e:
            print(f"保存最高分失败: {e}")

    def bind_keys(self):
        """
        绑定键盘控制事件
        """
        self.master.bind("<Up>", lambda e: self.change_direction("Up"))
        self.master.bind("<Down>", lambda e: self.change_direction("Down"))
        self.master.bind("<Left>", lambda e: self.change_direction("Left"))
        self.master.bind("<Right>", lambda e: self.change_direction("Right"))
        self.master.bind("<space>", lambda e: self.toggle_pause())

    def set_speed(self, speed):
        """
        设置游戏速度（难度）
        :param speed: 移动间隔时间(ms)
        """
        self.speed = speed

    def change_direction(self, new_direction):
        """
        改变蛇的移动方向，防止反向移动
        :param new_direction: 新方向
        """
        opposites = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if new_direction != opposites.get(self.direction, ""):
            self.next_direction = new_direction

    def toggle_pause(self):
        """
        切换游戏暂停/继续状态
        """
        if not self.game_over_flag:
            self.is_paused = not self.is_paused
            if not self.is_paused:
                self.update_game()

    def spawn_food(self):
        """
        随机生成食物位置，确保不在蛇身上
        :return: 食物坐标
        """
        while True:
            x = random.randint(0, self.COLUMNS - 1)
            y = random.randint(0, self.ROWS - 1)
            if (x, y) not in self.snake:
                return (x, y)

    def check_collision(self, head):
        """
        碰撞检测系统
        :param head: 蛇头坐标
        :return: 是否发生碰撞
        """
        x, y = head
        if x < 0 or x >= self.COLUMNS or y < 0 or y >= self.ROWS:
            return True
        if head in self.snake[1:]:
            return True
        return False

    def draw_snake(self):
        """
        绘制蛇身
        """
        for i, (x, y) in enumerate(self.snake):
            color = "#4CAF50" if i == 0 else "#81C784"
            x1 = x * self.CELL_SIZE
            y1 = y * self.CELL_SIZE
            x2 = x1 + self.CELL_SIZE
            y2 = y1 + self.CELL_SIZE
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#222222", width=2)

    def draw_food(self):
        """
        绘制食物
        """
        x, y = self.food
        x1 = x * self.CELL_SIZE
        y1 = y * self.CELL_SIZE
        x2 = x1 + self.CELL_SIZE
        y2 = y1 + self.CELL_SIZE
        self.canvas.create_oval(x1, y1, x2, y2, fill="#FF5722", outline="#FF5722")

    def draw_score(self):
        """
        绘制分数显示
        """
        self.score_label.config(text=f"分数: {self.score}")
        self.high_score_label.config(text=f"最高分: {self.high_score}")

    def draw_pause(self):
        """
        绘制暂停提示
        """
        if self.is_paused:
            self.canvas.create_rectangle(0, 0, self.WINDOW_WIDTH, self.GAME_AREA_HEIGHT,
                                         fill="#000000", stipple="gray50")
            self.canvas.create_text(self.WINDOW_WIDTH // 2, self.GAME_AREA_HEIGHT // 2,
                                    text="游戏暂停", font=("Arial", 36, "bold"), fill="white")

    def draw_game_over(self):
        """
        绘制游戏结束画面
        """
        self.canvas.create_rectangle(0, 0, self.WINDOW_WIDTH, self.GAME_AREA_HEIGHT,
                                     fill="#000000", stipple="gray50")
        self.canvas.create_text(self.WINDOW_WIDTH // 2, self.GAME_AREA_HEIGHT // 2 - 50,
                                text="游戏结束", font=("Arial", 36, "bold"), fill="white")
        self.canvas.create_text(self.WINDOW_WIDTH // 2, self.GAME_AREA_HEIGHT // 2,
                                text=f"得分: {self.score}", font=("Arial", 24), fill="yellow")
        self.canvas.create_text(self.WINDOW_WIDTH // 2, self.GAME_AREA_HEIGHT // 2 + 60,
                                text="按任意键重新开始", font=("Arial", 18), fill="white")
        self.master.bind("<Key>", self.restart_game)

    def restart_game(self, event):
        """
        重新开始游戏
        :param event: 键盘事件
        """
        self.master.unbind("<Key>")
        self.game_over_flag = False
        self.score = 0
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.food = self.spawn_food()
        self.is_paused = False
        self.bind_keys()
        self.update_game()

    def play_eat_sound(self):
        """
        播放吃食物音效
        """
        if self.eat_sound:
            try:
                self.eat_sound.play()
            except:
                pass

    def play_game_over_sound(self):
        """
        播放游戏结束音效
        """
        if self.game_over_sound:
            try:
                self.game_over_sound.play()
            except:
                pass

    def update_game(self):
        """
        游戏主循环更新函数
        """
        if self.is_paused or self.game_over_flag:
            if self.is_paused:
                self.draw_pause()
            return

        self.direction = self.next_direction

        head_x, head_y = self.snake[0]
        if self.direction == "Up":
            new_head = (head_x, head_y - 1)
        elif self.direction == "Down":
            new_head = (head_x, head_y + 1)
        elif self.direction == "Left":
            new_head = (head_x - 1, head_y)
        else:
            new_head = (head_x + 1, head_y)

        if self.check_collision(new_head):
            self.game_over()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 10
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            self.food = self.spawn_food()
            self.play_eat_sound()
        else:
            self.snake.pop()

        self.canvas.delete(tk.ALL)
        self.draw_snake()
        self.draw_food()
        self.draw_score()

        self.master.after(self.speed, self.update_game)

    def game_over(self):
        """
        游戏结束处理
        """
        self.game_over_flag = True
        self.play_game_over_sound()
        self.draw_game_over()


if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
