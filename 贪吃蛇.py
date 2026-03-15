# -*- coding: utf-8 -*-
"""
贪吃蛇小游戏 - 使用Python Tkinter图形界面库开发

文件结构说明：
- SnakeGame类：主游戏类，包含所有游戏逻辑
- 依赖包：tkinter（Python内置）、pygame（需安装）
- 音效文件：eat.wav、game_over.wav（与Python文件同目录）
- 最高分文件：snake_high_score.txt（自动创建）

安装依赖命令：pip install pygame

作者：AI Assistant
日期：2026-03-15
"""

import tkinter as tk
from tkinter import messagebox
import random
import os

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("提示：pygame未安装，音效功能将被禁用。安装命令：pip install pygame")


class SnakeGame:
    """
    贪吃蛇游戏主类
    
    该类封装了贪吃蛇游戏的所有功能，包括：
    - 游戏初始化与窗口创建
    - 蛇的移动与控制
    - 食物生成
    - 碰撞检测
    - 计分系统
    - 难度调节
    - 暂停/继续功能
    - 最高分记录
    - 音效播放
    """
    
    def __init__(self, root):
        """
        初始化游戏
        
        参数：
            root: Tkinter根窗口对象
        """
        self.root = root
        self.root.title("贪吃蛇小游戏")
        self.root.resizable(False, False)
        
        # 游戏区域尺寸配置
        self.canvas_width = 600
        self.canvas_height = 500
        self.cell_size = 20
        
        # 难度设置（毫秒）
        self.difficulties = {
            "简单": 300,
            "中等": 200,
            "困难": 100
        }
        self.current_speed = 200
        
        # 游戏状态变量
        self.snake = []
        self.direction = "Right"
        self.next_direction = "Right"
        self.food = None
        self.score = 0
        self.high_score = 0
        self.is_running = False
        self.is_paused = False
        self.game_over = False
        
        # 颜色配置
        self.bg_color = "#2c3e50"
        self.snake_color = "#27ae60"
        self.snake_head_color = "#2ecc71"
        self.food_color = "#e74c3c"
        self.text_color = "#ecf0f1"
        
        # 初始化音效系统
        self._init_sound()
        
        # 加载最高分记录
        self._load_high_score()
        
        # 创建游戏界面
        self._create_ui()
        
        # 绑定键盘事件
        self._bind_events()
        
        # 初始化游戏
        self._init_game()
    
    def _init_sound(self):
        """
        初始化音效系统
        
        尝试初始化pygame音频模块，加载音效文件
        如果音效文件不存在，则禁用对应音效
        """
        self.sound_enabled = False
        self.eat_sound = None
        self.game_over_sound = None
        
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                self.sound_enabled = True
                
                # 获取音效文件路径（与Python文件同目录）
                script_dir = os.path.dirname(os.path.abspath(__file__))
                
                # 加载吃食物音效
                eat_sound_path = os.path.join(script_dir, "eat.wav")
                if os.path.exists(eat_sound_path):
                    self.eat_sound = pygame.mixer.Sound(eat_sound_path)
                else:
                    print(f"提示：音效文件 {eat_sound_path} 不存在，吃食物音效被禁用")
                
                # 加载游戏结束音效
                game_over_sound_path = os.path.join(script_dir, "game_over.wav")
                if os.path.exists(game_over_sound_path):
                    self.game_over_sound = pygame.mixer.Sound(game_over_sound_path)
                else:
                    print(f"提示：音效文件 {game_over_sound_path} 不存在，游戏结束音效被禁用")
                    
            except Exception as e:
                print(f"音效系统初始化失败：{e}")
                self.sound_enabled = False
    
    def _play_sound(self, sound_type):
        """
        播放音效
        
        参数：
            sound_type: 音效类型，"eat"或"game_over"
        """
        if not self.sound_enabled:
            return
        
        try:
            if sound_type == "eat" and self.eat_sound:
                self.eat_sound.play()
            elif sound_type == "game_over" and self.game_over_sound:
                self.game_over_sound.play()
        except Exception as e:
            print(f"播放音效失败：{e}")
    
    def _load_high_score(self):
        """
        加载最高分记录
        
        从snake_high_score.txt文件读取最高分
        如果文件不存在，则创建并初始化为0
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.high_score_file = os.path.join(script_dir, "snake_high_score.txt")
        
        try:
            if os.path.exists(self.high_score_file):
                with open(self.high_score_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    self.high_score = int(content) if content.isdigit() else 0
            else:
                # 文件不存在，创建并初始化为0
                self._save_high_score(0)
        except Exception as e:
            print(f"加载最高分失败：{e}")
            self.high_score = 0
    
    def _save_high_score(self, score):
        """
        保存最高分记录
        
        参数：
            score: 要保存的最高分
        """
        try:
            with open(self.high_score_file, "w", encoding="utf-8") as f:
                f.write(str(score))
            self.high_score = score
        except Exception as e:
            print(f"保存最高分失败：{e}")
    
    def _create_ui(self):
        """
        创建游戏界面
        
        包括：顶部控制面板、游戏画布、底部信息显示
        """
        # 顶部控制面板
        control_frame = tk.Frame(self.root, bg="#34495e", pady=10)
        control_frame.pack(fill=tk.X)
        
        # 难度按钮标题
        tk.Label(
            control_frame,
            text="难度选择：",
            bg="#34495e",
            fg=self.text_color,
            font=("微软雅黑", 12)
        ).pack(side=tk.LEFT, padx=10)
        
        # 难度按钮（简单/中等/困难）
        self.difficulty_buttons = {}
        for difficulty in ["简单", "中等", "困难"]:
            btn = tk.Button(
                control_frame,
                text=difficulty,
                width=8,
                font=("微软雅黑", 10),
                command=lambda d=difficulty: self._change_difficulty(d),
                bg="#3498db" if difficulty == "中等" else "#95a5a6",
                fg="white",
                relief=tk.RAISED,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.difficulty_buttons[difficulty] = btn
        
        # 最高分显示
        self.high_score_label = tk.Label(
            control_frame,
            text=f"最高分：{self.high_score}",
            bg="#34495e",
            fg="#f1c40f",
            font=("微软雅黑", 12, "bold")
        )
        self.high_score_label.pack(side=tk.RIGHT, padx=20)
        
        # 游戏画布
        self.canvas = tk.Canvas(
            self.root,
            width=self.canvas_width,
            height=self.canvas_height,
            bg=self.bg_color,
            highlightthickness=2,
            highlightbackground="#34495e"
        )
        self.canvas.pack(padx=10, pady=5)
        
        # 底部信息面板
        info_frame = tk.Frame(self.root, bg="#34495e", pady=8)
        info_frame.pack(fill=tk.X)
        
        # 当前分数显示
        self.score_label = tk.Label(
            info_frame,
            text=f"当前分数：{self.score}",
            bg="#34495e",
            fg=self.text_color,
            font=("微软雅黑", 14, "bold")
        )
        self.score_label.pack(side=tk.LEFT, padx=20)
        
        # 操作提示
        tk.Label(
            info_frame,
            text="操作：方向键移动 | 空格键暂停 | R键重新开始",
            bg="#34495e",
            fg="#bdc3c7",
            font=("微软雅黑", 10)
        ).pack(side=tk.RIGHT, padx=20)
    
    def _change_difficulty(self, difficulty):
        """
        切换游戏难度
        
        参数：
            difficulty: 难度名称（"简单"/"中等"/"困难"）
        """
        self.current_speed = self.difficulties[difficulty]
        
        # 更新按钮样式
        for d, btn in self.difficulty_buttons.items():
            if d == difficulty:
                btn.config(bg="#3498db", relief=tk.SUNKEN)
            else:
                btn.config(bg="#95a5a6", relief=tk.RAISED)
        
        # 如果游戏正在运行，重新设置移动速度
        if self.is_running and not self.is_paused:
            self.root.after_cancel(self.move_job)
            self.move_job = self.root.after(self.current_speed, self._move_snake)
    
    def _bind_events(self):
        """
        绑定键盘事件
        
        方向键控制蛇的移动方向
        空格键控制暂停/继续
        R键重新开始游戏
        """
        self.root.bind("<Up>", lambda e: self._set_direction("Up"))
        self.root.bind("<Down>", lambda e: self._set_direction("Down"))
        self.root.bind("<Left>", lambda e: self._set_direction("Left"))
        self.root.bind("<Right>", lambda e: self._set_direction("Right"))
        self.root.bind("<space>", lambda e: self._toggle_pause())
        self.root.bind("<r>", lambda e: self._restart_game())
        self.root.bind("<R>", lambda e: self._restart_game())
    
    def _set_direction(self, new_direction):
        """
        设置蛇的移动方向
        
        参数：
            new_direction: 新方向（"Up"/"Down"/"Left"/"Right"）
        
        防止蛇反向移动（如向右时不能直接向左）
        """
        # 方向相反映射
        opposites = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        
        # 只有在不与当前方向相反时才更新方向
        if opposites.get(new_direction) != self.direction:
            self.next_direction = new_direction
    
    def _toggle_pause(self):
        """
        切换暂停/继续状态
        
        按空格键暂停或继续游戏
        暂停时显示"游戏暂停"提示
        """
        if not self.is_running or self.game_over:
            return
        
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            # 暂停游戏
            self.root.after_cancel(self.move_job)
            self._draw_pause_overlay()
        else:
            # 继续游戏
            self._move_snake()
    
    def _draw_pause_overlay(self):
        """
        绘制暂停覆盖层
        
        在游戏画布中央显示半透明"游戏暂停"提示
        """
        # 绘制半透明背景
        self.canvas.create_rectangle(
            0, 0, self.canvas_width, self.canvas_height,
            fill="#000000",
            stipple="gray50",
            tags="pause_overlay"
        )
        
        # 绘制暂停文字
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2,
            text="游戏暂停",
            font=("微软雅黑", 36, "bold"),
            fill="#ffffff",
            tags="pause_overlay"
        )
        
        # 绘制继续提示
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2 + 50,
            text="按空格键继续",
            font=("微软雅黑", 14),
            fill="#bdc3c7",
            tags="pause_overlay"
        )
    
    def _init_game(self):
        """
        初始化游戏状态
        
        重置蛇的位置、方向、分数等
        生成第一个食物
        """
        # 初始化蛇（从中间位置开始，长度为3）
        start_x = self.canvas_width // 2 // self.cell_size * self.cell_size
        start_y = self.canvas_height // 2 // self.cell_size * self.cell_size
        
        self.snake = [
            (start_x, start_y),
            (start_x - self.cell_size, start_y),
            (start_x - self.cell_size * 2, start_y)
        ]
        
        # 重置方向
        self.direction = "Right"
        self.next_direction = "Right"
        
        # 重置分数
        self.score = 0
        self.score_label.config(text=f"当前分数：{self.score}")
        
        # 重置游戏状态
        self.game_over = False
        self.is_paused = False
        
        # 生成食物
        self._generate_food()
        
        # 绘制初始画面
        self._draw()
        
        # 开始游戏
        self.is_running = True
        self.move_job = self.root.after(self.current_speed, self._move_snake)
    
    def _generate_food(self):
        """
        生成食物
        
        随机生成食物位置，确保不会出现在蛇身体上
        """
        while True:
            # 计算网格数量
            cols = self.canvas_width // self.cell_size
            rows = self.canvas_height // self.cell_size
            
            # 随机生成食物位置
            x = random.randint(0, cols - 1) * self.cell_size
            y = random.randint(0, rows - 1) * self.cell_size
            
            # 确保食物不在蛇身上
            if (x, y) not in self.snake:
                self.food = (x, y)
                break
    
    def _move_snake(self):
        """
        移动蛇
        
        根据当前方向移动蛇头，检查碰撞
        如果吃到食物，增加蛇身长度和分数
        """
        if self.game_over or self.is_paused:
            return
        
        # 更新方向
        self.direction = self.next_direction
        
        # 获取蛇头位置
        head_x, head_y = self.snake[0]
        
        # 根据方向计算新蛇头位置
        if self.direction == "Up":
            new_head = (head_x, head_y - self.cell_size)
        elif self.direction == "Down":
            new_head = (head_x, head_y + self.cell_size)
        elif self.direction == "Left":
            new_head = (head_x - self.cell_size, head_y)
        else:  # Right
            new_head = (head_x + self.cell_size, head_y)
        
        # 检查碰撞
        if self._check_collision(new_head):
            self._game_over()
            return
        
        # 移动蛇
        self.snake.insert(0, new_head)
        
        # 检查是否吃到食物
        if new_head == self.food:
            # 增加分数
            self.score += 10
            self.score_label.config(text=f"当前分数：{self.score}")
            
            # 播放吃食物音效
            self._play_sound("eat")
            
            # 生成新食物
            self._generate_food()
        else:
            # 没吃到食物，移除蛇尾
            self.snake.pop()
        
        # 重绘画面
        self._draw()
        
        # 继续移动
        self.move_job = self.root.after(self.current_speed, self._move_snake)
    
    def _check_collision(self, head):
        """
        检查碰撞
        
        参数：
            head: 蛇头位置元组
        
        返回：
            True表示发生碰撞，False表示安全
        
        检查边界碰撞和自咬碰撞
        """
        x, y = head
        
        # 检查边界碰撞
        if x < 0 or x >= self.canvas_width or y < 0 or y >= self.canvas_height:
            return True
        
        # 检查自咬碰撞
        if head in self.snake:
            return True
        
        return False
    
    def _draw(self):
        """
        绘制游戏画面
        
        包括蛇、食物、游戏结束画面等
        """
        # 清除画布
        self.canvas.delete("game")
        
        # 绘制网格背景（可选，增加视觉效果）
        for i in range(0, self.canvas_width, self.cell_size):
            self.canvas.create_line(
                i, 0, i, self.canvas_height,
                fill="#34495e",
                tags="game"
            )
        for i in range(0, self.canvas_height, self.cell_size):
            self.canvas.create_line(
                0, i, self.canvas_width, i,
                fill="#34495e",
                tags="game"
            )
        
        # 绘制食物
        if self.food:
            fx, fy = self.food
            self.canvas.create_oval(
                fx + 2, fy + 2,
                fx + self.cell_size - 2, fy + self.cell_size - 2,
                fill=self.food_color,
                outline="#c0392b",
                width=2,
                tags="game"
            )
        
        # 绘制蛇
        for i, (x, y) in enumerate(self.snake):
            if i == 0:
                # 蛇头（不同颜色）
                color = self.snake_head_color
                outline_color = "#1e8449"
            else:
                # 蛇身
                color = self.snake_color
                outline_color = "#1e8449"
            
            self.canvas.create_rectangle(
                x + 1, y + 1,
                x + self.cell_size - 1, y + self.cell_size - 1,
                fill=color,
                outline=outline_color,
                width=1,
                tags="game"
            )
    
    def _game_over(self):
        """
        游戏结束处理
        
        显示游戏结束画面，更新最高分，播放音效
        """
        self.game_over = True
        self.is_running = False
        
        # 播放游戏结束音效
        self._play_sound("game_over")
        
        # 检查并更新最高分
        if self.score > self.high_score:
            self._save_high_score(self.score)
            self.high_score_label.config(text=f"最高分：{self.high_score}")
            new_record = True
        else:
            new_record = False
        
        # 绘制游戏结束覆盖层
        self.canvas.create_rectangle(
            0, 0, self.canvas_width, self.canvas_height,
            fill="#000000",
            stipple="gray50",
            tags="game_over"
        )
        
        # 游戏结束文字
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2 - 60,
            text="游戏结束",
            font=("微软雅黑", 42, "bold"),
            fill="#e74c3c",
            tags="game_over"
        )
        
        # 显示分数
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2,
            text=f"最终得分：{self.score}",
            font=("微软雅黑", 20),
            fill="#ecf0f1",
            tags="game_over"
        )
        
        # 新纪录提示
        if new_record:
            self.canvas.create_text(
                self.canvas_width // 2,
                self.canvas_height // 2 + 40,
                text="🎉 恭喜！打破最高分记录！",
                font=("微软雅黑", 16, "bold"),
                fill="#f1c40f",
                tags="game_over"
            )
        
        # 重新开始提示
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2 + 80,
            text="按 R 键重新开始",
            font=("微软雅黑", 14),
            fill="#bdc3c7",
            tags="game_over"
        )
    
    def _restart_game(self):
        """
        重新开始游戏
        
        清除游戏结束画面，重新初始化游戏
        """
        if not self.game_over:
            return
        
        # 清除游戏结束覆盖层
        self.canvas.delete("game_over")
        
        # 重新初始化游戏
        self._init_game()


def main():
    """
    主函数
    
    创建Tkinter根窗口，初始化游戏
    """
    root = tk.Tk()
    
    # 先创建游戏实例（这会创建所有UI组件）
    game = SnakeGame(root)
    
    # 设置窗口居中
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # 获取窗口实际大小
    window_width = root.winfo_reqwidth()
    window_height = root.winfo_reqheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"+{x}+{y}")
    
    # 运行主循环
    root.mainloop()


if __name__ == "__main__":
    main()