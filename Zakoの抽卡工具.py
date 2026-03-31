# -*- coding: utf-8 -*-
import customtkinter as ctk
import json
import random
import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog
import shutil
import webbrowser

# 使用浅色模式
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# 级别配置
LEVELS = {
    "G": "普通",
    "S": "敏感",
    "Q": "可疑",
    "E": "露骨",
}


class ScrollableDropdown(ctk.CTkFrame):
    """可滚动的自定义下拉框"""
    def __init__(self, master, values=None, command=None, height=40, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.values = values or []
        self.command = command
        self._dropdown_open = False
        self._dropdown_window = None
        self._selected_value = self.values[0] if self.values else ""
        
        # 主按钮框架
        self.button_frame = ctk.CTkFrame(
            self,
            fg_color="#f8f9fc",
            border_color="#e2e4e9",
            border_width=1,
            corner_radius=10,
            height=height
        )
        self.button_frame.pack(fill="x")
        self.button_frame.pack_propagate(False)
        
        # 文本标签
        self.label = ctk.CTkLabel(
            self.button_frame,
            text=self._selected_value,
            font=ctk.CTkFont(size=14),
            text_color="#2d3748",
            anchor="w"
        )
        self.label.pack(side="left", fill="x", expand=True, padx=15)
        
        # 下拉箭头
        self.arrow = ctk.CTkLabel(
            self.button_frame,
            text="›",
            font=ctk.CTkFont(size=16),
            text_color="#718096",
            width=30
        )
        self.arrow.pack(side="right", padx=(0, 10))
        
        # 绑定点击事件
        for widget in [self.button_frame, self.label, self.arrow]:
            widget.bind("<Button-1>", self._toggle)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        self.button_frame.configure(fg_color="#eef0f5")
    
    def _on_leave(self, event):
        self.button_frame.configure(fg_color="#f8f9fc")
    
    def _toggle(self, event=None):
        if self._dropdown_open:
            self._close_dropdown()
        else:
            self._open_dropdown()
    
    def _open_dropdown(self):
        if self._dropdown_open:
            return
            
        self._dropdown_open = True
        self.arrow.configure(text="⌄")
        
        # 创建下拉窗口
        self._dropdown_window = tk.Toplevel(self)
        self._dropdown_window.withdraw()
        self._dropdown_window.overrideredirect(True)
        
        # 获取位置
        x = self.button_frame.winfo_rootx()
        y = self.button_frame.winfo_rooty() + self.button_frame.winfo_height() + 4
        width = self.button_frame.winfo_width()
        
        # 下拉框容器
        dropdown_frame = ctk.CTkFrame(
            self._dropdown_window,
            fg_color="#ffffff",
            border_color="#e2e4e9",
            border_width=1,
            corner_radius=10
        )
        dropdown_frame.pack(fill="both", expand=True)
        
        # 可滚动区域
        max_visible = 8
        item_height = 38
        visible_count = min(len(self.values), max_visible)
        list_height = visible_count * item_height
        
        scroll_frame = ctk.CTkScrollableFrame(
            dropdown_frame,
            fg_color="transparent",
            height=list_height,
            corner_radius=8
        )
        scroll_frame.pack(fill="both", expand=True, padx=6, pady=6)
        
        # 添加选项
        for value in self.values:
            btn = ctk.CTkButton(
                scroll_frame,
                text=value,
                font=ctk.CTkFont(size=13),
                height=item_height - 6,
                anchor="w",
                fg_color="transparent",
                hover_color="#f0f2f5",
                text_color="#2d3748",
                corner_radius=6,
                command=lambda v=value: self._select(v)
            )
            btn.pack(fill="x", pady=1)
        
        # 设置窗口位置和大小
        self._dropdown_window.geometry(f"{width}x{list_height + 14}+{x}+{y}")
        self._dropdown_window.deiconify()
        
        # 点击其他地方关闭
        self.winfo_toplevel().bind("<Button-1>", self._on_click_outside, add="+")
    
    def _on_click_outside(self, event):
        if self._dropdown_window and self._dropdown_open:
            try:
                widget = event.widget
                if widget in [self.button_frame, self.label, self.arrow]:
                    return
                x, y = event.x_root, event.y_root
                dx = self._dropdown_window.winfo_rootx()
                dy = self._dropdown_window.winfo_rooty()
                dw = self._dropdown_window.winfo_width()
                dh = self._dropdown_window.winfo_height()
                if not (dx <= x <= dx + dw and dy <= y <= dy + dh):
                    self._close_dropdown()
            except:
                pass
    
    def _select(self, value):
        self._selected_value = value
        self.label.configure(text=value)
        self._close_dropdown()
        if self.command:
            self.command(value)
    
    def _close_dropdown(self):
        if self._dropdown_window:
            self._dropdown_window.destroy()
            self._dropdown_window = None
        self._dropdown_open = False
        self.arrow.configure(text="›")
        try:
            self.winfo_toplevel().unbind("<Button-1>")
        except:
            pass
    
    def get(self):
        return self._selected_value
    
    def set(self, value):
        if value in self.values:
            self._selected_value = value
            self.label.configure(text=value)


class SmallDropdown(ctk.CTkFrame):
    """小型可点击展开的下拉框"""
    def __init__(self, master, values=None, width=100, height=24, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.values = values or []
        self._dropdown_open = False
        self._dropdown_window = None
        self._selected_value = self.values[0] if self.values else ""
        self._width = width
        self._height = height
        
        # 主按钮框架（去掉边框，使用纯色背景）
        self.button_frame = ctk.CTkFrame(
            self,
            fg_color="#e8eaed",
            border_width=0,
            corner_radius=6,
            height=height,
            width=width
        )
        self.button_frame.pack()
        self.button_frame.pack_propagate(False)
        
        # 文本标签
        self.label = ctk.CTkLabel(
            self.button_frame,
            text=self._selected_value,
            font=ctk.CTkFont(size=11),
            text_color="#2d3748",
            anchor="w"
        )
        self.label.pack(side="left", fill="x", expand=True, padx=8)
        
        # 下拉箭头
        self.arrow = ctk.CTkLabel(
            self.button_frame,
            text="▾",
            font=ctk.CTkFont(size=10),
            text_color="#718096",
            width=16
        )
        self.arrow.pack(side="right", padx=(0, 6))
        
        # 绑定点击事件
        for widget in [self.button_frame, self.label, self.arrow]:
            widget.bind("<Button-1>", self._toggle)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        self.button_frame.configure(fg_color="#dcdfe3")
    
    def _on_leave(self, event):
        self.button_frame.configure(fg_color="#e8eaed")
    
    def _toggle(self, event=None):
        if self._dropdown_open:
            self._close_dropdown()
        else:
            self._open_dropdown()
    
    def _open_dropdown(self):
        if self._dropdown_open:
            return
            
        self._dropdown_open = True
        self.arrow.configure(text="⌄")
        
        # 创建下拉窗口
        self._dropdown_window = tk.Toplevel(self)
        self._dropdown_window.withdraw()
        self._dropdown_window.overrideredirect(True)
        
        # 获取位置
        x = self.button_frame.winfo_rootx()
        y = self.button_frame.winfo_rooty() + self.button_frame.winfo_height() + 2
        
        # 下拉框容器（无边框，使用阴影效果的背景色）
        dropdown_frame = ctk.CTkFrame(
            self._dropdown_window,
            fg_color="#ffffff",
            border_width=0,
            corner_radius=8
        )
        dropdown_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # 选项
        max_visible = 6
        item_height = 28
        visible_count = min(len(self.values), max_visible)
        list_height = visible_count * item_height + 12
        
        # 始终使用滚动框架以支持滚动
        scroll_frame = ctk.CTkScrollableFrame(
            dropdown_frame,
            fg_color="transparent",
            height=list_height - 12,
            corner_radius=4,
            scrollbar_button_color="#d1d5db",
            scrollbar_button_hover_color="#b0b5bc"
        )
        scroll_frame.pack(fill="both", expand=True, padx=4, pady=6)
        
        # 绑定鼠标滚轮事件到下拉窗口
        def on_mousewheel(event):
            scroll_frame._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self._dropdown_window.bind("<MouseWheel>", on_mousewheel)
        
        # 添加选项
        for value in self.values:
            btn = ctk.CTkButton(
                scroll_frame,
                text=value,
                font=ctk.CTkFont(size=11),
                height=item_height - 4,
                anchor="w",
                fg_color="transparent",
                hover_color="#e8eaed",
                text_color="#2d3748",
                corner_radius=4,
                command=lambda v=value: self._select(v)
            )
            btn.pack(fill="x", pady=1)
        
        # 设置窗口位置和大小
        self._dropdown_window.geometry(f"{self._width}x{list_height}+{x}+{y}")
        self._dropdown_window.deiconify()
        
        # 点击其他地方关闭
        self.winfo_toplevel().bind("<Button-1>", self._on_click_outside, add="+")
    
    def _on_click_outside(self, event):
        if self._dropdown_window and self._dropdown_open:
            try:
                widget = event.widget
                if widget in [self.button_frame, self.label, self.arrow]:
                    return
                x, y = event.x_root, event.y_root
                dx = self._dropdown_window.winfo_rootx()
                dy = self._dropdown_window.winfo_rooty()
                dw = self._dropdown_window.winfo_width()
                dh = self._dropdown_window.winfo_height()
                if not (dx <= x <= dx + dw and dy <= y <= dy + dh):
                    self._close_dropdown()
            except:
                pass
    
    def _select(self, value):
        self._selected_value = value
        self.label.configure(text=value)
        self._close_dropdown()
    
    def _close_dropdown(self):
        if self._dropdown_window:
            self._dropdown_window.destroy()
            self._dropdown_window = None
        self._dropdown_open = False
        self.arrow.configure(text="›")
        try:
            self.winfo_toplevel().unbind("<Button-1>")
        except:
            pass
    
    def get(self):
        return self._selected_value
    
    def set(self, value):
        if value in self.values:
            self._selected_value = value
            self.label.configure(text=value)
    
    def configure(self, **kwargs):
        if "values" in kwargs:
            self.values = kwargs.pop("values")
            if self.values and self._selected_value not in self.values:
                self._selected_value = self.values[0]
                self.label.configure(text=self._selected_value)
        super().configure(**kwargs)


class GachaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("杂鱼的宇宙超级霹雳无敌至尊黄瓜🥒抽卡机")
        self.geometry("580x750")
        self.minsize(500, 650)
        
        # 设置窗口背景
        self.configure(fg_color="#ffffff")
        
        # 获取数据目录
        if getattr(sys, 'frozen', False):
            # 打包后：内置数据在临时目录，用户数据在exe所在目录
            self.base_dir = os.path.join(sys._MEIPASS, "D站词条")
            self.exe_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境：都在脚本所在目录的D站词条下
            self.base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D站词条")
            self.exe_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 用户导入数据目录（exe所在目录下，确保持久化）
        self.input_dir = os.path.join(self.exe_dir, "input")
        self.input_tag_dir = os.path.join(self.input_dir, "tag")
        self.input_artist_dir = os.path.join(self.input_dir, "artist")
        for d in [self.input_dir, self.input_tag_dir, self.input_artist_dir]:
            if not os.path.exists(d):
                os.makedirs(d)
        
        # 设置窗口图标
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, "icon.ico")
        else:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        self.icon_path = icon_path  # 保存图标路径供弹窗使用
        
        # 获取类别数据
        self.category_data = self.get_categories_with_count()
        self.selected_level = ctk.StringVar(value="G")
        self.artist_mode = ctk.StringVar(value="none")  # none, artist_string, artist_random, custom_artist
        self.fixed_mode = ctk.BooleanVar(value=False)  # 固定模式
        self.last_tag = ""  # 保存上次抽取的tag
        
        self.create_widgets()
    
    def _count_tags_in_folder(self, folder_path):
        """统计文件夹中所有级别JSON的tag总数"""
        total = 0
        has_json = False
        for level in LEVELS.keys():
            data = self._load_json_safe(os.path.join(folder_path, f"{level}.json"))
            if data:
                has_json = True
                total += len(data)
        return (total, has_json)
    
    def get_categories_with_count(self):
        """获取所有类别及其总tag数，导入的在前（按时间倒序），内置的按数量降序"""
        exclude_folders = {"画师串", "__pycache__", "input", "build", "dist", "venv"}
        
        # 内置类别
        builtin = {}
        for item in os.listdir(self.base_dir):
            if item in exclude_folders or not os.path.isdir(os.path.join(self.base_dir, item)):
                continue
            count, has_json = self._count_tags_in_folder(os.path.join(self.base_dir, item))
            if has_json:
                builtin[item] = count
        
        # 用户导入的类别（按创建时间倒序）
        imported = []
        if os.path.exists(self.input_tag_dir):
            for item in os.listdir(self.input_tag_dir):
                item_path = os.path.join(self.input_tag_dir, item)
                if os.path.isdir(item_path):
                    count, has_json = self._count_tags_in_folder(item_path)
                    if has_json:
                        imported.append((f"[导入] {item}", count, os.path.getctime(item_path)))
            imported.sort(key=lambda x: x[2], reverse=True)
        
        # 合并结果：导入的在前，内置的按数量降序在后
        result = {name: count for name, count, _ in imported}
        result.update(dict(sorted(builtin.items(), key=lambda x: x[1], reverse=True)))
        return result
    
    def get_imported_artist_list(self):
        """获取导入的画师串列表"""
        artists = []
        if os.path.exists(self.input_artist_dir):
            for folder in os.listdir(self.input_artist_dir):
                folder_path = os.path.join(self.input_artist_dir, folder)
                if os.path.isdir(folder_path):
                    # 检查是否有json文件
                    for file in os.listdir(folder_path):
                        if file.endswith('.json'):
                            artists.append(folder)
                            break
        return artists if artists else ["无"]
    
    def create_widgets(self):
        # 主容器
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=50, pady=40)
        
        # GitHub 图标（左上角）
        github_btn = ctk.CTkButton(
            self,
            text="🐙",
            width=28,
            height=28,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color="#e2e8f0",
            text_color="#718096",
            corner_radius=6,
            command=lambda: webbrowser.open("https://github.com/xiaoshengyvlin/ZaKo-Random-Roll")
        )
        github_btn.place(x=12, y=12)
        
        # 标题（混合字体）
        title_frame = ctk.CTkFrame(main, fg_color="transparent")
        title_frame.pack(anchor="center", pady=(0, 32))
        
        ctk.CTkLabel(
            title_frame,
            text="✦ ",
            font=ctk.CTkFont(family="KaiTi", size=28),
            text_color="#1a202c"
        ).pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="ZaKo",
            font=ctk.CTkFont(family="STSong", size=28, weight="bold"),
            text_color="#1a202c"
        ).pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="の神奇抽卡工具 ✦",
            font=ctk.CTkFont(family="KaiTi", size=28),
            text_color="#1a202c"
        ).pack(side="left")
        
        # 类别选择区
        cat_frame = ctk.CTkFrame(main, fg_color="transparent")
        cat_frame.pack(fill="x", pady=10)
        
        cat_header = ctk.CTkFrame(cat_frame, fg_color="transparent")
        cat_header.pack(fill="x", pady=(0, 8))
        
        ctk.CTkLabel(
            cat_header,
            text="选择类别",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4a5568"
        ).pack(side="left")
        
        ctk.CTkButton(
            cat_header,
            text="+ 导入",
            width=70,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="#10b981",
            hover_color="#059669",
            text_color="#ffffff",
            corner_radius=6,
            command=self.open_import_tag_dialog
        ).pack(side="right")
        
        display_values = [f"{name} ({count})" for name, count in self.category_data.items()]
        
        self.category_combo = ScrollableDropdown(
            cat_frame,
            values=display_values,
            height=46
        )
        self.category_combo.pack(fill="x")
        
        # 级别选择区
        level_frame = ctk.CTkFrame(main, fg_color="transparent")
        level_frame.pack(fill="x", pady=(20, 10))
        
        ctk.CTkLabel(
            level_frame,
            text="选择级别",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4a5568"
        ).pack(anchor="w", pady=(0, 12))
        
        # 级别按钮容器
        btn_frame = ctk.CTkFrame(level_frame, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        for level, name in LEVELS.items():
            rb = ctk.CTkRadioButton(
                btn_frame,
                text=f"{level} · {name}",
                variable=self.selected_level,
                value=level,
                font=ctk.CTkFont(size=14),
                fg_color="#6366f1",
                hover_color="#4f46e5",
                border_color="#cbd5e0",
                text_color="#2d3748",
                radiobutton_width=20,
                radiobutton_height=20
            )
            rb.pack(side="left", padx=(0, 20))
        
        # 画师选项区
        artist_frame = ctk.CTkFrame(main, fg_color="transparent")
        artist_frame.pack(fill="x", pady=(20, 10))
        
        artist_header = ctk.CTkFrame(artist_frame, fg_color="transparent")
        artist_header.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(
            artist_header,
            text="画师选项",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4a5568"
        ).pack(side="left")
        
        ctk.CTkButton(
            artist_header,
            text="+ 导入画师串",
            width=100,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="#10b981",
            hover_color="#059669",
            text_color="#ffffff",
            corner_radius=6,
            command=self.open_import_artist_dialog
        ).pack(side="right")
        
        artist_btn_frame = ctk.CTkFrame(artist_frame, fg_color="transparent")
        artist_btn_frame.pack(fill="x")
        
        artist_options = [
            ("none", "不添加"),
            ("artist_string", "预设画师串"),
            ("artist_random", "随机画师"),
            ("custom_artist", "自定义画师串"),
        ]
        
        for value, text in artist_options:
            rb = ctk.CTkRadioButton(
                artist_btn_frame,
                text=text,
                variable=self.artist_mode,
                value=value,
                font=ctk.CTkFont(size=14),
                fg_color="#10b981",
                hover_color="#059669",
                border_color="#cbd5e0",
                text_color="#2d3748",
                radiobutton_width=20,
                radiobutton_height=20
            )
            rb.pack(side="left", padx=(0, 15))
        
        # 固定模式区（独立一行）
        fixed_frame = ctk.CTkFrame(main, fg_color="transparent")
        fixed_frame.pack(fill="x", pady=(15, 10))
        
        ctk.CTkLabel(
            fixed_frame,
            text="其他选项",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4a5568"
        ).pack(side="left", padx=(0, 15))
        
        self.fixed_checkbox = ctk.CTkCheckBox(
            fixed_frame,
            text="固定内容（仅更换画师）",
            variable=self.fixed_mode,
            font=ctk.CTkFont(size=14),
            fg_color="#f59e0b",
            hover_color="#d97706",
            border_color="#cbd5e0",
            text_color="#2d3748",
            checkbox_width=20,
            checkbox_height=20
        )
        self.fixed_checkbox.pack(side="left")
        
        # 自定义画师串下拉框（放在右侧）
        self.custom_artist_dropdown = SmallDropdown(
            fixed_frame,
            values=self.get_imported_artist_list(),
            width=110,
            height=24
        )
        self.custom_artist_dropdown.pack(side="right")
        
        ctk.CTkLabel(
            fixed_frame,
            text="选择画师串：",
            font=ctk.CTkFont(size=12),
            text_color="#718096"
        ).pack(side="right", padx=(0, 6))
        
        # 抽卡按钮
        self.gacha_btn = ctk.CTkButton(
            main,
            text="✧ 开始抽卡",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=52,
            fg_color="#6366f1",
            hover_color="#4f46e5",
            text_color="#ffffff",
            corner_radius=14,
            command=self.do_gacha
        )
        self.gacha_btn.pack(fill="x", pady=(28, 24))
        
        # 结果区域
        result_frame = ctk.CTkFrame(main, fg_color="transparent")
        result_frame.pack(fill="both", expand=True)
        
        # 结果头部
        header = ctk.CTkFrame(result_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            header,
            text="抽卡结果",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4a5568"
        ).pack(side="left")
        
        self.copy_btn = ctk.CTkButton(
            header,
            text="复制",
            width=60,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color="#eef2ff",
            hover_color="#e0e7ff",
            text_color="#4f46e5",
            corner_radius=8,
            command=self.copy_result
        )
        self.copy_btn.pack(side="right")
        
        # 结果文本框
        self.output_text = ctk.CTkTextbox(
            result_frame,
            font=ctk.CTkFont(family="Consolas", size=14),
            wrap="word",
            fg_color="#f8fafc",
            border_width=1,
            border_color="#e2e8f0",
            corner_radius=12,
            text_color="#1e293b"
        )
        self.output_text.pack(fill="both", expand=True)
    
    def do_gacha(self):
        """执行抽卡"""
        artist_mode = self.artist_mode.get()
        is_fixed = self.fixed_mode.get()
        
        # 固定模式 + 不添加画师 = 不进行任何变化
        if is_fixed and artist_mode == "none":
            messagebox.showinfo("提示", "已勾选固定内容，tag将不进行变化")
            return
        
        # 固定模式：只更换画师，保持tag不变
        if is_fixed and artist_mode != "none" and self.last_tag:
            tag = self.last_tag
        else:
            # 正常抽取tag
            combo_value = self.category_combo.get()
            category = combo_value.rsplit(" (", 1)[0]
            level = self.selected_level.get()
            
            # 判断是否是导入类别
            if category.startswith("[导入] "):
                real_name = category.replace("[导入] ", "")
                json_path = os.path.join(self.input_tag_dir, real_name, f"{level}.json")
            else:
                json_path = os.path.join(self.base_dir, category, f"{level}.json")
            
            if not os.path.exists(json_path):
                messagebox.showwarning("提示", f"请先导入 {level} 级别的tag")
                return
            
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if not data:
                    self.show_result("该类别下没有可用的词条")
                    return
                
                tag = random.choice(list(data.keys()))
                self.last_tag = tag  # 保存当前tag
                
            except Exception as e:
                self.show_result(f"读取出错：{str(e)}")
                return
        
        # 根据画师模式添加内容
        result = tag
        if artist_mode == "artist_string":
            artist_str = self.get_random_artist_string()
            if artist_str:
                result = artist_str + ",\n" + tag
        elif artist_mode == "artist_random":
            artist_str = self.get_random_artist_combo()
            if artist_str:
                result = artist_str + ",\n" + tag
        elif artist_mode == "custom_artist":
            artist_str = self.get_custom_artist_string()
            if artist_str:
                result = artist_str + ",\n" + tag
            else:
                messagebox.showwarning("提示", "请先导入自定义画师串")
                return
        
        self.show_result(result)
    
    def _load_json_safe(self, path):
        """安全加载JSON文件，失败返回空字典"""
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _load_random_from_folder(self, folder_path):
        """从文件夹中的第一个JSON文件随机抽取一条"""
        if not os.path.exists(folder_path):
            return None
        for file in os.listdir(folder_path):
            if file.endswith('.json'):
                data = self._load_json_safe(os.path.join(folder_path, file))
                if data:
                    return random.choice(list(data.keys()))
        return None
    
    def get_random_artist_string(self):
        """从画师串.json中随机抽取一条"""
        data = self._load_json_safe(os.path.join(self.base_dir, "画师串", "画师串.json"))
        return random.choice(list(data.keys())) if data else ""
    
    def get_random_artist_combo(self):
        """从热门画师+画师池中随机组合，按权重降序排列"""
        base_path = os.path.join(self.base_dir, "画师串")
        hot_data = self._load_json_safe(os.path.join(base_path, "热门画师.json"))
        pool_data = self._load_json_safe(os.path.join(base_path, "画师池.json"))
        
        result = []
        # 热门画师权重：0.80~1.20，画师池权重：0.50~0.80
        hot_weights = [0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20]
        pool_weights = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]
        
        def strip_parens(s):
            return s[1:-1] if s.startswith('(') and s.endswith(')') else s
        
        # 从热门画师抽1个
        if hot_data:
            artist = strip_parens(random.choice(list(hot_data.keys())))
            result.append((artist, random.choice(hot_weights)))
        
        # 从画师池抽2~4个
        if pool_data:
            pool_list = list(pool_data.keys())
            for artist in random.sample(pool_list, min(random.randint(2, 4), len(pool_list))):
                result.append((strip_parens(artist), random.choice(pool_weights)))
        
        # 按权重降序排列并格式化
        result.sort(key=lambda x: x[1], reverse=True)
        return ", ".join(f"({name}:{weight:.2f})" for name, weight in result)
    
    def show_result(self, text):
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text)
    
    def copy_result(self):
        text = self.output_text.get("1.0", "end").strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.copy_btn.configure(text="已复制 ✓")
            self.after(1500, lambda: self.copy_btn.configure(text="复制"))
    
    def _center_dialog(self, dialog, width, height):
        """将弹窗居中到主窗口"""
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - width) // 2
        y = self.winfo_y() + (self.winfo_height() - height) // 2
        dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def open_import_tag_dialog(self):
        """打开导入Tag类别对话框"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("导入Tag类别")
        self._center_dialog(dialog, 450, 400)
        dialog.transient(self)
        dialog.grab_set()
        
        # 设置对话框图标
        if os.path.exists(self.icon_path):
            dialog.after(200, lambda: dialog.iconbitmap(self.icon_path))
        
        # 类别名输入
        ctk.CTkLabel(
            dialog,
            text="类别名称：",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        name_entry = ctk.CTkEntry(dialog, width=400, height=35)
        name_entry.pack(padx=20)
        
        # 级别导入区
        ctk.CTkLabel(
            dialog,
            text="导入JSON文件：",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        level_files = {}
        level_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        level_frame.pack(fill="x", padx=20)
        
        for level, name in LEVELS.items():
            row = ctk.CTkFrame(level_frame, fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                row,
                text=f"{level} ({name})：",
                width=100,
                anchor="w"
            ).pack(side="left")
            
            file_label = ctk.CTkLabel(row, text="未选择", text_color="#718096", width=200, anchor="w")
            file_label.pack(side="left", padx=10)
            
            def select_file(lv=level, lbl=file_label):
                path = filedialog.askopenfilename(
                    title=f"选择 {lv}.json",
                    filetypes=[("JSON文件", "*.json")]
                )
                if path:
                    level_files[lv] = path
                    lbl.configure(text=os.path.basename(path), text_color="#10b981")
            
            ctk.CTkButton(
                row,
                text="选择",
                width=60,
                height=28,
                command=select_file
            ).pack(side="right")
        
        def save_import():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("提示", "请输入类别名称")
                return
            if not level_files:
                messagebox.showwarning("提示", "请至少导入一个JSON文件")
                return
            
            # 创建目录并复制文件 (input/tag/预设名/E.json等)
            tag_dir = os.path.join(self.input_tag_dir, name)
            os.makedirs(tag_dir, exist_ok=True)
            
            for level, path in level_files.items():
                shutil.copy(path, os.path.join(tag_dir, f"{level}.json"))
            
            messagebox.showinfo("成功", f"已导入类别：{name}")
            dialog.destroy()
            
            # 刷新类别列表
            self.category_data = self.get_categories_with_count()
            display_values = [f"{n} ({c})" for n, c in self.category_data.items()]
            self.category_combo.values = display_values
            if display_values:
                self.category_combo.set(display_values[0])
        
        ctk.CTkButton(
            dialog,
            text="保存",
            width=120,
            height=40,
            fg_color="#6366f1",
            hover_color="#4f46e5",
            command=save_import
        ).pack(pady=30)
    
    def open_import_artist_dialog(self):
        """打开导入画师串对话框"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("导入画师串")
        self._center_dialog(dialog, 450, 250)
        dialog.transient(self)
        dialog.grab_set()
        
        # 设置对话框图标
        if os.path.exists(self.icon_path):
            dialog.after(200, lambda: dialog.iconbitmap(self.icon_path))
        
        # 画师串名称
        ctk.CTkLabel(
            dialog,
            text="画师串名称：",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        name_entry = ctk.CTkEntry(dialog, width=400, height=35)
        name_entry.pack(padx=20)
        
        ctk.CTkLabel(
            dialog,
            text="选择JSON文件：",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 5))
        
        file_path = {"path": None}
        
        row = ctk.CTkFrame(dialog, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=5)
        
        file_label = ctk.CTkLabel(row, text="未选择", text_color="#718096", width=300, anchor="w")
        file_label.pack(side="left")
        
        def select_file():
            path = filedialog.askopenfilename(
                title="选择画师串JSON",
                filetypes=[("JSON文件", "*.json")]
            )
            if path:
                file_path["path"] = path
                file_label.configure(text=os.path.basename(path), text_color="#10b981")
        
        ctk.CTkButton(
            row,
            text="选择文件",
            width=80,
            height=30,
            command=select_file
        ).pack(side="right")
        
        def save_import():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("提示", "请输入画师串名称")
                return
            if not file_path["path"]:
                messagebox.showwarning("提示", "请选择JSON文件")
                return
            
            # 创建目录并复制文件 (input/artist/画师串名/xxx.json)
            artist_dir = os.path.join(self.input_artist_dir, name)
            os.makedirs(artist_dir, exist_ok=True)
            
            # 复制JSON文件（保留原文件名）
            src_filename = os.path.basename(file_path["path"])
            shutil.copy(file_path["path"], os.path.join(artist_dir, src_filename))
            
            messagebox.showinfo("成功", f"已导入画师串：{name}")
            dialog.destroy()
            
            # 刷新下拉框
            new_list = self.get_imported_artist_list()
            self.custom_artist_dropdown.configure(values=new_list)
            self.custom_artist_dropdown.set(name)  # 设置为刚导入的
        
        ctk.CTkButton(
            dialog,
            text="保存",
            width=120,
            height=40,
            fg_color="#6366f1",
            hover_color="#4f46e5",
            command=save_import
        ).pack(pady=20)
    
    def get_custom_artist_string(self):
        """从选中的导入画师串中随机抽取"""
        selected = self.custom_artist_dropdown.get()
        if not selected or selected == "无":
            return None
        
        folder_path = os.path.join(self.input_artist_dir, selected)
        return self._load_random_from_folder(folder_path)


if __name__ == "__main__":
    app = GachaApp()
    app.mainloop()
