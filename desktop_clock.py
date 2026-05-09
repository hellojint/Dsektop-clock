import tkinter as tk
from tkinter import ttk
from datetime import datetime
import zoneinfo
import threading
import requests
from lunar_python import Lunar
import os
import math

# 修复 tkinter 找不到 tcl/tk 库的问题
os.environ['TCL_LIBRARY'] = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"
os.environ['TK_LIBRARY'] = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python313\tcl\tk8.6"

class DesktopClock:
    def __init__(self, root):
        self.root = root
        
        # 无边框模式
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)  # 置顶显示

        self.is_compact = False
        self.expanded_geometry = "1000x410"
        self.compact_geometry = "280x130"
        self.root.geometry(self.expanded_geometry)

        # 变量设置
        self.tz1_var = tk.StringVar(value="Asia/Shanghai")
        self.tz2_var = tk.StringVar(value="UTC")
        self.alpha_var = tk.DoubleVar(value=1.0)
        
        # 界面初始化
        self.setup_ui()
        
        # 监听时区变化以更新天气
        self.tz1_var.trace_add("write", lambda *args: self.update_weather(1))
        self.tz2_var.trace_add("write", lambda *args: self.update_weather(2))
        
        # 首次获取天气
        self.update_weather(1)
        self.update_weather(2)
        
        # 启动时间更新
        self.update_time()

    def setup_ui(self):
        # 自定义标题栏 (用于拖动)
        self.title_bar = tk.Frame(self.root, bg="#87CEEB", relief="flat", bd=0)
        self.title_bar.pack(fill=tk.X, side=tk.TOP)
        
        self.title_label = tk.Label(self.title_bar, text=" 桌面时钟", bg="#87CEEB", fg="white", font=("Microsoft YaHei", 10, "bold"))
        self.title_label.pack(side=tk.LEFT, pady=5)
        
        # 关闭按钮
        self.close_btn = tk.Button(self.title_bar, text="✕", bg="#E74C3C", fg="white", bd=0, width=4, command=self.root.quit)
        self.close_btn.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 切换模式按钮
        self.toggle_btn = tk.Button(self.title_bar, text="精简模式", bg="#5BB5E0", fg="white", bd=0, padx=10, command=self.toggle_mode)
        self.toggle_btn.pack(side=tk.RIGHT, fill=tk.Y, padx=2)
        
        # 绑定拖动事件
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        self.title_label.bind("<Button-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.do_move)

        # ================== 完整模式容器 ==================
        self.expanded_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.expanded_frame.pack(fill=tk.BOTH, expand=True)

        # 获取所有可用时区并排序
        try:
            timezones = sorted(list(zoneinfo.available_timezones()))
        except Exception:
            timezones = [
                "Asia/Shanghai", "UTC", "America/New_York", 
                "Europe/London", "Asia/Tokyo", "Australia/Sydney",
                "Europe/Paris", "Asia/Dubai", "America/Los_Angeles"
            ]
        
        # 设置样式
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Microsoft YaHei", 10))

        # 底部：透明度控制
        alpha_frame = ttk.Frame(self.expanded_frame, padding=10)
        alpha_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Label(alpha_frame, text="不透明度:").pack(side=tk.LEFT)
        alpha_scale = ttk.Scale(alpha_frame, from_=0.1, to=1.0, variable=self.alpha_var, command=self.change_alpha)
        alpha_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        # 主容器：用于左中右布局
        main_container = ttk.Frame(self.expanded_frame, padding=15)
        main_container.pack(fill=tk.BOTH, expand=True)

        # ================= 左侧：时区 1 框 =================
        left_frame = tk.Frame(main_container, bg="#ffffff", relief=tk.RIDGE, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="主时间 (国家/地区 1):", font=("Microsoft YaHei", 10, "bold"), background="#ffffff").pack(pady=(10, 5))
        cb1 = ttk.Combobox(left_frame, textvariable=self.tz1_var, values=timezones, width=25, state="readonly")
        cb1.pack(pady=5)
        
        self.date1_label = tk.Label(left_frame, font=("Microsoft YaHei", 14), bg="#ffffff", fg="#7F8C8D")
        self.date1_label.pack(pady=(5, 0))
        self.lunar1_label = tk.Label(left_frame, font=("Microsoft YaHei", 11), bg="#ffffff", fg="#D35400")
        self.lunar1_label.pack(pady=(2, 0))
        self.time1_label = tk.Label(left_frame, font=("Microsoft YaHei", 32, "bold"), bg="#ffffff", fg="#2C3E50")
        self.time1_label.pack(pady=(5, 5), expand=True)
        self.weather1_label = tk.Label(left_frame, font=("Microsoft YaHei", 11), bg="#ffffff", fg="#34495E")
        self.weather1_label.pack(pady=(0, 10))
        
        # ================= 中间：模拟钟表 =================
        center_frame = tk.Frame(main_container, bg="#f0f0f0")
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10)
        
        ttk.Label(center_frame, text="当前主时间", font=("Microsoft YaHei", 10, "bold")).pack(pady=(10, 5))
        
        self.canvas = tk.Canvas(center_frame, width=180, height=180, bg="#f0f0f0", highlightthickness=0)
        self.canvas.pack(pady=15)
        
        self.canvas.create_oval(10, 10, 170, 170, width=2, outline="#BDC3C7")
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x1 = 90 + 70 * math.cos(angle)
            y1 = 90 + 70 * math.sin(angle)
            x2 = 90 + 80 * math.cos(angle)
            y2 = 90 + 80 * math.sin(angle)
            self.canvas.create_line(x1, y1, x2, y2, width=2 if i % 3 == 0 else 1, fill="#7F8C8D")
            
        self.hour_hand = self.canvas.create_line(90, 90, 90, 90, width=4, fill="#2C3E50", capstyle=tk.ROUND)
        self.min_hand = self.canvas.create_line(90, 90, 90, 90, width=3, fill="#34495E", capstyle=tk.ROUND)
        self.sec_hand = self.canvas.create_line(90, 90, 90, 90, width=1.5, fill="#E74C3C", capstyle=tk.ROUND)
        self.canvas.create_oval(85, 85, 95, 95, fill="#E74C3C", outline="")
        
        # ================= 右侧：时区 2 框 =================
        right_frame = tk.Frame(main_container, bg="#ffffff", relief=tk.RIDGE, bd=2)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        ttk.Label(right_frame, text="次时间 (国家/地区 2):", font=("Microsoft YaHei", 10, "bold"), background="#ffffff").pack(pady=(10, 5))
        cb2 = ttk.Combobox(right_frame, textvariable=self.tz2_var, values=timezones, width=25, state="readonly")
        cb2.pack(pady=5)
        
        self.date2_label = tk.Label(right_frame, font=("Microsoft YaHei", 14), bg="#ffffff", fg="#7F8C8D")
        self.date2_label.pack(pady=(5, 0))
        self.lunar2_label = tk.Label(right_frame, font=("Microsoft YaHei", 11), bg="#ffffff", fg="#D35400")
        self.lunar2_label.pack(pady=(2, 0))
        self.time2_label = tk.Label(right_frame, font=("Microsoft YaHei", 32, "bold"), bg="#ffffff", fg="#2C3E50")
        self.time2_label.pack(pady=(5, 5), expand=True)
        self.weather2_label = tk.Label(right_frame, font=("Microsoft YaHei", 11), bg="#ffffff", fg="#34495E")
        self.weather2_label.pack(pady=(0, 10))

        # ================== 精简模式容器 ==================
        self.compact_frame = tk.Frame(self.root, bg="#ffffff", relief=tk.RIDGE, bd=2)
        self.compact_time_label = tk.Label(self.compact_frame, font=("Microsoft YaHei", 40, "bold"), bg="#ffffff", fg="#2C3E50")
        self.compact_time_label.pack(pady=(15, 0), expand=True)
        self.compact_date_label = tk.Label(self.compact_frame, font=("Microsoft YaHei", 12), bg="#ffffff", fg="#7F8C8D")
        self.compact_date_label.pack(pady=(0, 15))

    def toggle_mode(self):
        if self.is_compact:
            self.compact_frame.pack_forget()
            self.expanded_frame.pack(fill=tk.BOTH, expand=True)
            self.root.geometry(self.expanded_geometry)
            self.toggle_btn.config(text="精简模式")
            self.is_compact = False
        else:
            self.expanded_frame.pack_forget()
            self.compact_frame.pack(fill=tk.BOTH, expand=True)
            self.root.geometry(self.compact_geometry)
            self.toggle_btn.config(text="完整模式")
            self.is_compact = True

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
        
    def change_alpha(self, event=None):
        alpha = self.alpha_var.get()
        self.root.attributes("-alpha", alpha)
        
    def get_city_from_tz(self, tz_str):
        if "/" in tz_str:
            return tz_str.split("/")[-1].replace("_", " ")
        return tz_str

    def update_weather(self, tz_index):
        tz_str = self.tz1_var.get() if tz_index == 1 else self.tz2_var.get()
        city = self.get_city_from_tz(tz_str)
        label = self.weather1_label if tz_index == 1 else self.weather2_label
        
        if city.upper() in ["UTC", "GMT", "UCT", "ETC/GMT"]:
            label.config(text="天气: --")
            return

        label.config(text="获取天气中...")
        
        def fetch():
            try:
                headers = {'Accept-Language': 'zh-CN'}
                url = f"http://wttr.in/{city}?format=%c+%C+%t"
                res = requests.get(url, headers=headers, timeout=5)
                if res.status_code == 200:
                    weather_text = res.text.strip()
                    self.root.after(0, lambda: label.config(text=f"天气: {weather_text}"))
                else:
                    self.root.after(0, lambda: label.config(text="天气获取失败"))
            except Exception:
                self.root.after(0, lambda: label.config(text="天气: 网络异常"))
        
        threading.Thread(target=fetch, daemon=True).start()

    def update_time(self):
        tz1_str = self.tz1_var.get()
        tz2_str = self.tz2_var.get()
        
        # ================= 更新时区1 (主时间) =================
        try:
            tz1 = zoneinfo.ZoneInfo(tz1_str)
            now1 = datetime.now(tz1)
            date_str = now1.strftime("%Y-%m-%d")
            time_str = now1.strftime("%H:%M:%S")
            
            self.date1_label.config(text=date_str)
            self.time1_label.config(text=time_str)
            self.compact_date_label.config(text=date_str)
            self.compact_time_label.config(text=time_str)
            
            # 农历与节气
            lunar1 = Lunar.fromDate(now1)
            lunar_str1 = f"农历 {lunar1.getMonthInChinese()}月{lunar1.getDayInChinese()}"
            jieqi1 = lunar1.getJieQi()
            if jieqi1:
                lunar_str1 += f" · {jieqi1}"
            festivals1 = lunar1.getFestivals()
            if festivals1:
                lunar_str1 += f" · {festivals1[0]}"
            self.lunar1_label.config(text=lunar_str1)
            
            # ---------------- 更新中间的模拟钟表 ----------------
            sec = now1.second
            min_ = now1.minute
            hr = now1.hour
            
            sec_angle = math.radians(sec * 6 - 90)
            min_angle = math.radians(min_ * 6 + sec * 0.1 - 90)
            hr_angle = math.radians((hr % 12) * 30 + min_ * 0.5 - 90)
            
            self.canvas.coords(self.sec_hand, 90, 90, 90 + 70 * math.cos(sec_angle), 90 + 70 * math.sin(sec_angle))
            self.canvas.coords(self.min_hand, 90, 90, 90 + 60 * math.cos(min_angle), 90 + 60 * math.sin(min_angle))
            self.canvas.coords(self.hour_hand, 90, 90, 90 + 45 * math.cos(hr_angle), 90 + 45 * math.sin(hr_angle))
            
        except Exception:
            self.date1_label.config(text="--")
            self.time1_label.config(text="无效时区")
            self.lunar1_label.config(text="--")
            self.compact_date_label.config(text="--")
            self.compact_time_label.config(text="无效时区")
            
        # ================= 更新时区2 (次时间) =================
        try:
            tz2 = zoneinfo.ZoneInfo(tz2_str)
            now2 = datetime.now(tz2)
            self.date2_label.config(text=now2.strftime("%Y-%m-%d"))
            self.time2_label.config(text=now2.strftime("%H:%M:%S"))
            
            # 农历与节气
            lunar2 = Lunar.fromDate(now2)
            lunar_str2 = f"农历 {lunar2.getMonthInChinese()}月{lunar2.getDayInChinese()}"
            jieqi2 = lunar2.getJieQi()
            if jieqi2:
                lunar_str2 += f" · {jieqi2}"
            festivals2 = lunar2.getFestivals()
            if festivals2:
                lunar_str2 += f" · {festivals2[0]}"
            self.lunar2_label.config(text=lunar_str2)
            
        except Exception:
            self.date2_label.config(text="--")
            self.time2_label.config(text="无效时区")
            self.lunar2_label.config(text="--")
            
        # 每 1000 毫秒（1 秒）更新一次
        self.root.after(1000, self.update_time)

if __name__ == "__main__":
    root = tk.Tk()
    app = DesktopClock(root)
    root.mainloop()
