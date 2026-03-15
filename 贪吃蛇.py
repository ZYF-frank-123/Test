#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贪吃蛇游戏 - Snake Game

文件结构说明：
- 本文件使用Python3 + Tkinter实现图形界面贪吃蛇游戏
- 可选集成pygame用于音效播放
- 采用面向对象编程范式，主要类为SnakeGame

依赖包安装命令：
    pip install pygame  # 可选，用于音效功能

音效文件放置说明：
- eat.wav: 吃食物音效，放置在与本文件同目录下
- game_over.wav: 游戏结束音效，放置在与本文件同目录下
- 若音效文件缺失，游戏将以静音模式运行，不影响其他功能

游戏操作说明：
- 方向键(↑↓←→): 控制蛇的移动方向
- 空格键: 暂停/继续游戏
- 游戏结束后点击窗口可重新开始

作者: AI Assistant
日期: 2026-03-15
"""

import tkinter as tk
from tkinter import messagebox
import random
import os

# 尝试导入pygame用于音效，若失败则以静音模式运行
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("提示: 未安装pygame，游戏将以静音模式运行")
    print("安装命令: pip install pygame")


class SnakeGame:
    """
    贪吃蛇游戏主类
    
    功能模块：
    - 游戏初始化与窗口设置
    - 蛇的移动与控制
    - 食物生成与管理
    - 碰撞检测系统
    - 计分与最高分记录
    - 难度调节系统
    - 暂停/继续功能
    - 音效播放系统
    """
    
    # 游戏常量定义
    GAME_WIDTH = 600          # 游戏区域宽度(像素)
    GAME_HEIGHT = 400         # 游戏区域高度(像素)
    GRID_SIZE = 20            # 网格大小(像素)
    GRID_WIDTH = GAME_WIDTH // GRID_SIZE   # 横向网格数
    GRID_HEIGHT = GAME_HEIGHT // GRID_SIZE # 纵向网格数
    
    # 难度设置 (移动间隔毫秒数，越小越快)
    DIFFICULTY_EASY = 300
    DIFFICULTY_MEDIUM = 200
    DIFFICULTY_HARD = 100
    
    # 颜色定义
    COLOR_BACKGROUND = "#2C3E50"      # 背景色
    COLOR_SNAKE_HEAD = "#27AE60"      # 蛇头颜色
    COLOR_SNAKE_BODY = "#2ECC71"      # 蛇身颜色
    COLOR_FOOD = "#E74C3C"            # 食物颜色
    COLOR_TEXT = "#ECF0F1"            # 文字颜色
    COLOR_BUTTON_BG = "#34495E"       # 按钮背景色
    COLOR_BUTTON_ACTIVE = "#1ABC9C"   # 按钮激活色
    
    def __init__(self):
        """
        初始化游戏
        
        功能：
        - 创建主窗口
        - 初始化游戏状态
        - 设置UI组件
        - 加载音效资源
        - 读取最高分记录
        """
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("贪吃蛇游戏 - Snake Game")
        self.root.resizable(False, False)
        
        # 初始化游戏状态
        self.score = 0                    # 当前得分
        self.high_score = 0               # 最高分
        self.game_speed = self.DIFFICULTY_MEDIUM  # 默认中等难度
        self.direction = "Right"          # 当前移动方向
        self.next_direction = "Right"     # 下一个移动方向(防止快速按键冲突)
        self.is_game_over = False         # 游戏是否结束
        self.is_paused = False            # 游戏是否暂停
        self.game_running = False         # 游戏是否进行中
        
        # 蛇和食物数据
        self.snake = []                   # 蛇身坐标列表 [(x,y), ...]
        self.food = None                  # 食物坐标 (x,y)
        
        # 初始化音效系统
        self._init_audio()
        
        # 读取最高分
        self._load_high_score()
        
        # 创建UI组件
        self._create_ui()
        
        # 绑定键盘事件
        self._bind_events()
        
        # 初始化游戏
        self.reset_game()
    
    def _init_audio(self):
        """
        初始化音效系统
        
        功能：
        - 初始化pygame混音器
        - 加载音效文件
        - 若文件缺失则设置静音模式
        """
        self.audio_enabled = False
        self.eat_sound = None
        self.game_over_sound = None
        
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                
                # 获取当前文件所在目录
                current_dir = os.path.dirname(os.path.abspath(__file__))
                
                # 尝试加载吃食物音效
                eat_path = os.path.join(current_dir, "eat.wav")
                if os.path.exists(eat_path):
                    self.eat_sound = pygame.mixer.Sound(eat_path)
                else:
                    print(f"提示: 未找到音效文件 {eat_path}")
                
                # 尝试加载游戏结束音效
                over_path = os.path.join(current_dir, "game_over.wav")
                if os.path.exists(over_path):
                    self.game_over_sound = pygame.mixer.Sound(over_path)
                else:
                    print(f"提示: 未找到音效文件 {over_path}")
                
                # 至少有一个音效文件存在才启用音效
                if self.eat_sound or self.game_over_sound:
                    self.audio_enabled = True
                    print("音效系统已启用")
                else:
                    print("音效系统: 静音模式(无音效文件)")
                    
            except Exception as e:
                print(f"音效初始化失败: {e}")
                print("游戏将以静音模式运行")
    
    def _play_sound(self, sound_type):
        """
        播放指定类型的音效
        
        参数：
            sound_type: str - 音效类型，"eat"或"game_over"
        """
        if not self.audio_enabled:
            return
        
        try:
            if sound_type == "eat" and self.eat_sound:
                self.eat_sound.play()
            elif sound_type == "game_over" and self.game_over_sound:
                self.game_over_sound.play()
        except Exception as e:
            print(f"音效播放失败: {e}")
    
    def _load_high_score(self):
        """
        从文件加载最高分记录
        
        功能：
        - 读取snake_high_score.txt文件
        - 若文件不存在则创建并初始化为0
        - 异常处理确保程序稳定运行
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.high_score_file = os.path.join(current_dir, "snake_high_score.txt")
        
        try:
            if os.path.exists(self.high_score_file):
                with open(self.high_score_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    self.high_score = int(content) if content.isdigit() else 0
            else:
                # 文件不存在，创建并初始化为0
                with open(self.high_score_file, "w", encoding="utf-8") as f:
                    f.write("0")
                self.high_score = 0
                print(f"已创建最高分记录文件: {self.high_score_file}")
        except Exception as e:
            print(f"读取最高分记录失败: {e}")
            self.high_score = 0
    
    def _save_high_score(self):
        """
        保存最高分到文件
        
        功能：
        - 比较当前得分与最高分
        - 若当前得分更高则更新记录
        - 写入snake_high_score.txt文件
        """
        if self.score > self.high_score:
            self.high_score = self.score
            try:
                with open(self.high_score_file, "w", encoding="utf-8") as f:
                    f.write(str(self.high_score))
            except Exception as e:
                print(f"保存最高分记录失败: {e}")
        
        # 更新显示
        self.high_score_label.config(text=f"最高分: {self.high_score}")
    
    def _create_ui(self):
        """
        创建用户界面
        
        功能：
        - 创建顶部控制栏(难度按钮、分数显示)
        - 创建游戏画布
        - 设置布局
        """
        # 顶部控制栏框架
        self.control_frame = tk.Frame(
            self.root,
            bg=self.COLOR_BACKGROUND,
            height=60
        )
        self.control_frame.pack(fill=tk.X, padx=10, pady=10)
        self.control_frame.pack_propagate(False)
        
        # 难度选择按钮框架
        difficulty_frame = tk.Frame(self.control_frame, bg=self.COLOR_BACKGROUND)
        difficulty_frame.pack(side=tk.LEFT, padx=10)
        
        # 难度标签
        tk.Label(
            difficulty_frame,
            text="难度选择:",
            bg=self.COLOR_BACKGROUND,
            fg=self.COLOR_TEXT,
            font=("微软雅黑", 11)
        ).pack(side=tk.LEFT, padx=5)
        
        # 难度按钮
        self.difficulty_buttons = {}
        difficulties = [
            ("简单", self.DIFFICULTY_EASY),
            ("中等", self.DIFFICULTY_MEDIUM),
            ("困难", self.DIFFICULTY_HARD)
        ]
        
        for name, speed in difficulties:
            btn = tk.Button(
                difficulty_frame,
                text=name,
                bg=self.COLOR_BUTTON_BG,
                fg=self.COLOR_TEXT,
                activebackground=self.COLOR_BUTTON_ACTIVE,
                activeforeground=self.COLOR_TEXT,
                font=("微软雅黑", 10),
                width=8,
                relief=tk.FLAT,
                cursor="hand2",
                command=lambda s=speed, n=name: self._set_difficulty(s, n)
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.difficulty_buttons[name] = btn
        
        # 默认选中中等难度
        self._update_difficulty_button_style("中等")
        
        # 分数显示框架
        score_frame = tk.Frame(self.control_frame, bg=self.COLOR_BACKGROUND)
        score_frame.pack(side=tk.RIGHT, padx=10)
        
        # 当前分数标签
        self.score_label = tk.Label(
            score_frame,
            text="得分: 0",
            bg=self.COLOR_BACKGROUND,
            fg=self.COLOR_TEXT,
            font=("微软雅黑", 12, "bold")
        )
        self.score_label.pack(side=tk.LEFT, padx=10)
        
        # 最高分标签
        self.high_score_label = tk.Label(
            score_frame,
            text=f"最高分: {self.high_score}",
            bg=self.COLOR_BACKGROUND,
            fg="#F39C12",
            font=("微软雅黑", 12, "bold")
        )
        self.high_score_label.pack(side=tk.LEFT, padx=10)
        
        # 游戏画布
        self.canvas = tk.Canvas(
            self.root,
            width=self.GAME_WIDTH,
            height=self.GAME_HEIGHT,
            bg=self.COLOR_BACKGROUND,
            highlightthickness=2,
            highlightbackground="#34495E"
        )
        self.canvas.pack(padx=10, pady=(0, 10))
        
        # 底部提示信息
        self.info_label = tk.Label(
            self.root,
            text="操作: 方向键移动 | 空格键暂停/继续",
            bg=self.COLOR_BACKGROUND,
            fg="#7F8C8D",
            font=("微软雅黑", 10)
        )
        self.info_label.pack(pady=(0, 10))
    
    def _set_difficulty(self, speed, name):
        """
        设置游戏难度
        
        参数：
            speed: int - 移动间隔毫秒数
            name: str - 难度名称
        
        功能：
        - 更新游戏速度
        - 更新按钮样式
        - 若游戏进行中则立即生效
        """
        self.game_speed = speed
        self._update_difficulty_button_style(name)
        
        # 若游戏进行中，重新调度游戏循环以应用新速度
        if self.game_running and not self.is_game_over and not self.is_paused:
            self.root.after_cancel(self.game_loop_id)
            self._game_loop()
    
    def _update_difficulty_button_style(self, active_name):
        """
        更新难度按钮样式
        
        参数：
            active_name: str - 当前激活的难度按钮名称
        """
        for name, btn in self.difficulty_buttons.items():
            if name == active_name:
                btn.config(
                    bg=self.COLOR_BUTTON_ACTIVE,
                    relief=tk.SUNKEN
                )
            else:
                btn.config(
                    bg=self.COLOR_BUTTON_BG,
                    relief=tk.FLAT
                )
    
    def _bind_events(self):
        """
        绑定键盘事件
        
        功能：
        - 绑定方向键控制蛇移动
        - 绑定空格键暂停/继续
        - 绑定R键重新开始(游戏结束时)
        """
        self.root.focus_set()
        self.root.bind("<Key>", self._on_key_press)
        self.root.bind("<Up>", lambda e: self._change_direction("Up"))
        self.root.bind("<Down>", lambda e: self._change_direction("Down"))
        self.root.bind("<Left>", lambda e: self._change_direction("Left"))
        self.root.bind("<Right>", lambda e: self._change_direction("Right"))
        self.root.bind("<space>", lambda e: self._toggle_pause())
        self.root.bind("<r>", lambda e: self.reset_game() if self.is_game_over else None)
        self.root.bind("<R>", lambda e: self.reset_game() if self.is_game_over else None)
    
    def _on_key_press(self, event):
        """
        处理键盘按键事件
        
        参数：
            event: Tkinter事件对象
        """
        # 防止其他按键影响游戏
        pass
    
    def _change_direction(self, new_direction):
        """
        改变蛇的移动方向
        
        参数：
            new_direction: str - 新方向 ("Up"/"Down"/"Left"/"Right")
        
        功能：
        - 防止180度直接转向(蛇不能立即反向移动)
        - 记录下一个方向，在下次移动时应用
        """
        if self.is_game_over or self.is_paused:
            return
        
        # 防止直接反向移动
        opposite_directions = {
            "Up": "Down",
            "Down": "Up",
            "Left": "Right",
            "Right": "Left"
        }
        
        if opposite_directions.get(new_direction) != self.direction:
            self.next_direction = new_direction
    
    def _toggle_pause(self):
        """
        切换游戏暂停状态
        
        功能：
        - 暂停游戏时显示半透明提示
        - 继续游戏时隐藏提示并恢复游戏循环
        """
        if self.is_game_over or not self.game_running:
            return
        
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            # 显示暂停提示
            self._show_pause_overlay()
        else:
            # 隐藏暂停提示并恢复游戏
            self._hide_pause_overlay()
            self._game_loop()
    
    def _show_pause_overlay(self):
        """
        显示暂停提示覆盖层
        """
        # 创建半透明覆盖层
        self.pause_overlay = self.canvas.create_rectangle(
            0, 0, self.GAME_WIDTH, self.GAME_HEIGHT,
            fill="black",
            stipple="gray50",
            tags="pause"
        )
        
        # 显示暂停文字
        self.pause_text = self.canvas.create_text(
            self.GAME_WIDTH // 2,
            self.GAME_HEIGHT // 2,
            text="游戏暂停",
            fill=self.COLOR_TEXT,
            font=("微软雅黑", 32, "bold"),
            tags="pause"
        )
        
        self.pause_subtext = self.canvas.create_text(
            self.GAME_WIDTH // 2,
            self.GAME_HEIGHT // 2 + 50,
            text="按空格键继续",
            fill="#BDC3C7",
            font=("微软雅黑", 14),
            tags="pause"
        )
    
    def _hide_pause_overlay(self):
        """
        隐藏暂停提示覆盖层
        """
        self.canvas.delete("pause")
    
    def reset_game(self):
        """
        重置游戏状态
        
        功能：
        - 初始化蛇的位置和长度
        - 生成新的食物
        - 重置分数和状态
        - 清除画布并重新开始游戏循环
        """
        # 重置游戏状态
        self.is_game_over = False
        self.is_paused = False
        self.game_running = True
        self.score = 0
        self.direction = "Right"
        self.next_direction = "Right"
        
        # 初始化蛇的位置 (从左侧中间开始，长度3)
        start_x = self.GRID_WIDTH // 4
        start_y = self.GRID_HEIGHT // 2
        self.snake = [
            (start_x, start_y),
            (start_x - 1, start_y),
            (start_x - 2, start_y)
        ]
        
        # 生成食物
        self._generate_food()
        
        # 更新分数显示
        self.score_label.config(text=f"得分: {self.score}")
        
        # 清除画布
        self.canvas.delete("all")
        
        # 开始游戏循环
        self._game_loop()
    
    def _generate_food(self):
        """
        随机生成食物位置
        
        功能：
        - 在游戏区域内随机生成坐标
        - 确保食物不会出现在蛇身体上
        """
        while True:
            x = random.randint(0, self.GRID_WIDTH - 1)
            y = random.randint(0, self.GRID_HEIGHT - 1)
            
            # 确保食物不在蛇身上
            if (x, y) not in self.snake:
                self.food = (x, y)
                break
    
    def _game_loop(self):
        """
        游戏主循环
        
        功能：
        - 更新蛇的位置
        - 检测碰撞
        - 检测吃食物
        - 重绘画布
        - 调度下一次循环
        """
        if self.is_game_over or self.is_paused:
            return
        
        # 应用下一个方向
        self.direction = self.next_direction
        
        # 移动蛇
        self._move_snake()
        
        # 检测碰撞
        if self._check_collision():
            self._game_over()
            return
        
        # 检测是否吃到食物
        if self.snake[0] == self.food:
            self._eat_food()
        
        # 绘制游戏画面
        self._draw()
        
        # 调度下一次循环
        self.game_loop_id = self.root.after(self.game_speed, self._game_loop)
    
    def _move_snake(self):
        """
        移动蛇的位置
        
        功能：
        - 根据当前方向计算新头部位置
        - 将新头部添加到蛇身列表
        - 移除尾部(若未吃到食物)
        """
        # 获取当前头部位置
        head_x, head_y = self.snake[0]
        
        # 根据方向计算新头部位置
        direction_offsets = {
            "Up": (0, -1),
            "Down": (0, 1),
            "Left": (-1, 0),
            "Right": (1, 0)
        }
        
        dx, dy = direction_offsets[self.direction]
        new_head = (head_x + dx, head_y + dy)
        
        # 将新头部插入到列表开头
        self.snake.insert(0, new_head)
        
        # 若未吃到食物，移除尾部(保持长度不变)
        # 若吃到食物，不移除尾部(长度+1)，并在_eat_food中处理
        if new_head != self.food:
            self.snake.pop()
    
    def _check_collision(self):
        """
        检测碰撞
        
        返回：
            bool - 是否发生碰撞
        
        检测类型：
        - 边界碰撞：蛇头超出游戏区域
        - 自咬碰撞：蛇头与身体任何部分重叠
        """
        head_x, head_y = self.snake[0]
        
        # 边界碰撞检测
        if head_x < 0 or head_x >= self.GRID_WIDTH:
            return True
        if head_y < 0 or head_y >= self.GRID_HEIGHT:
            return True
        
        # 自咬碰撞检测 (头部与身体其他部分)
        if self.snake[0] in self.snake[1:]:
            return True
        
        return False
    
    def _eat_food(self):
        """
        处理吃食物逻辑
        
        功能：
        - 增加分数
        - 播放吃食物音效
        - 生成新食物
        - 更新分数显示
        """
        # 增加分数
        self.score += 10
        self.score_label.config(text=f"得分: {self.score}")
        
        # 播放音效
        self._play_sound("eat")
        
        # 生成新食物
        self._generate_food()
    
    def _game_over(self):
        """
        处理游戏结束逻辑
        
        功能：
        - 设置游戏结束状态
        - 保存最高分
        - 播放游戏结束音效
        - 显示游戏结束画面
        """
        self.is_game_over = True
        self.game_running = False
        
        # 保存最高分
        self._save_high_score()
        
        # 播放音效
        self._play_sound("game_over")
        
        # 显示游戏结束画面
        self._show_game_over_screen()
    
    def _show_game_over_screen(self):
        """
        显示游戏结束画面
        
        功能：
        - 显示半透明覆盖层
        - 显示游戏结束文字
        - 显示最终得分
        - 显示重新开始提示
        """
        # 创建半透明覆盖层
        self.canvas.create_rectangle(
            0, 0, self.GAME_WIDTH, self.GAME_HEIGHT,
            fill="black",
            stipple="gray50",
            tags="gameover"
        )
        
        # 游戏结束标题
        self.canvas.create_text(
            self.GAME_WIDTH // 2,
            self.GAME_HEIGHT // 2 - 60,
            text="游戏结束",
            fill="#E74C3C",
            font=("微软雅黑", 36, "bold"),
            tags="gameover"
        )
        
        # 显示最终得分
        self.canvas.create_text(
            self.GAME_WIDTH // 2,
            self.GAME_HEIGHT // 2,
            text=f"最终得分: {self.score}",
            fill=self.COLOR_TEXT,
            font=("微软雅黑", 20),
            tags="gameover"
        )
        
        # 显示最高分
        self.canvas.create_text(
            self.GAME_WIDTH // 2,
            self.GAME_HEIGHT // 2 + 40,
            text=f"最高分: {self.high_score}",
            fill="#F39C12",
            font=("微软雅黑", 16),
            tags="gameover"
        )
        
        # 重新开始提示
        self.canvas.create_text(
            self.GAME_WIDTH // 2,
            self.GAME_HEIGHT // 2 + 100,
            text="按 R 键重新开始",
            fill="#1ABC9C",
            font=("微软雅黑", 14),
            tags="gameover"
        )
        
        # 绑定点击事件重新开始
        self.canvas.bind("<Button-1>", lambda e: self.reset_game())
    
    def _draw(self):
        """
        绘制游戏画面
        
        功能：
        - 清除画布
        - 绘制蛇身
        - 绘制食物
        """
        # 清除画布(保留游戏结束画面)
        if not self.is_game_over:
            self.canvas.delete("all")
        
        # 绘制蛇
        for i, (x, y) in enumerate(self.snake):
            x1 = x * self.GRID_SIZE
            y1 = y * self.GRID_SIZE
            x2 = x1 + self.GRID_SIZE
            y2 = y1 + self.GRID_SIZE
            
            # 蛇头使用不同颜色
            color = self.COLOR_SNAKE_HEAD if i == 0 else self.COLOR_SNAKE_BODY
            
            # 绘制方块
            self.canvas.create_rectangle(
                x1 + 1, y1 + 1, x2 - 1, y2 - 1,
                fill=color,
                outline="",
                tags="snake"
            )
        
        # 绘制食物
        if self.food:
            fx, fy = self.food
            x1 = fx * self.GRID_SIZE
            y1 = fy * self.GRID_SIZE
            x2 = x1 + self.GRID_SIZE
            y2 = y1 + self.GRID_SIZE
            
            # 绘制圆形食物
            padding = 3
            self.canvas.create_oval(
                x1 + padding, y1 + padding,
                x2 - padding, y2 - padding,
                fill=self.COLOR_FOOD,
                outline="",
                tags="food"
            )
    
    def run(self):
        """
        启动游戏主循环
        """
        self.root.mainloop()


def main():
    """
    程序入口函数
    """
    print("=" * 50)
    print("贪吃蛇游戏 - Snake Game")
    print("=" * 50)
    print("操作说明:")
    print("  - 方向键(↑↓←→): 控制蛇移动")
    print("  - 空格键: 暂停/继续游戏")
    print("  - R键: 重新开始(游戏结束时)")
    print("=" * 50)
    
    # 创建并运行游戏
    game = SnakeGame()
    game.run()


if __name__ == "__main__":
    main()
