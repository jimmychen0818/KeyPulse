
# 開發者：jimmychen (u/jp6)
# 工具名稱：高級多功能連點器
# 功能：滑鼠自動點擊、鍵盤輸入、多段腳本、隨機延遲、啟動熱鍵、腳本儲存/讀取

import os
import json
import random
import threading
import time
import customtkinter as ctk
import pyautogui
from pynput import keyboard
from tkinter import filedialog, messagebox
from PIL import ImageGrab
import sys

# 初始化
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.geometry("500x600")
app.title("🖱️ 高級連點器 by u/jp6")

# 狀態與變數
clicking = False
click_thread = None
click_script = []
log_text = ""
click_limit = None
hotkey = "f6"
delay_before_start = 0
click_interval = 0.05
random_variation = 0.0

# UI 元件區
status_var = ctk.StringVar(value="停止中")
log_var = ctk.StringVar(value="等待中...")

def log(msg):
    global log_text
    log_text += f"{msg}\n"
    log_label.configure(text=log_text[-500:])

# 點擊腳本執行邏輯
def click_loop():
    global clicking, click_script
    time.sleep(delay_before_start)
    counter = 0
    while clicking:
        for action in click_script:
            if not clicking:
                break
            x, y, btn, key = action["x"], action["y"], action["button"], action["key"]
            interval = click_interval + random.uniform(-random_variation, random_variation)
            if x is not None and y is not None:
                pyautogui.moveTo(x, y)
            if btn:
                pyautogui.click(button=btn)
                log(f"[Click] {btn} at ({x},{y})")
            if key:
                pyautogui.press(key)
                log(f"[Key] {key}")
            counter += 1
            if click_limit and counter >= click_limit:
                log(f"達到點擊上限 {click_limit} 次")
                clicking = False
                break
            time.sleep(max(0.01, interval))
    status_var.set("停止中")

# 開始或停止點擊
def toggle_click():
    global clicking, click_thread, click_limit, delay_before_start, click_interval, random_variation
    if clicking:
        clicking = False
    else:
        try:
            delay_before_start = float(delay_entry.get())
            click_interval = float(interval_entry.get())
            random_variation = float(variation_entry.get())
            click_limit_val = limit_entry.get()
            click_limit = int(click_limit_val) if click_limit_val else None
        except:
            messagebox.showerror("錯誤", "請輸入有效的數值")
            return
        status_var.set("連點中")
        clicking = True
        click_thread = threading.Thread(target=click_loop)
        click_thread.start()

# 滑鼠座標紀錄
def record_position():
    x, y = pyautogui.position()
    click_script.append({"x": x, "y": y, "button": "left", "key": None})
    log(f"[記錄] 滑鼠位置 ({x},{y})")

# 新增鍵盤動作
def add_key_action():
    key = key_entry.get()
    click_script.append({"x": None, "y": None, "button": None, "key": key})
    log(f"[記錄] 鍵盤按鍵 {key}")

# 儲存腳本
def save_script():
    path = filedialog.asksaveasfilename(defaultextension=".json")
    if path:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(click_script, f, indent=2)
        log(f"[儲存] 腳本已儲存至 {path}")

# 讀取腳本
def load_script():
    global click_script
    path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if path:
        with open(path, "r", encoding="utf-8") as f:
            click_script = json.load(f)
        log(f"[載入] 腳本已載入")

# 熱鍵偵測
def on_press(key):
    global hotkey
    try:
        if hasattr(key, 'char') and key.char == hotkey:
            toggle_click()
    except:
        pass

listener = keyboard.Listener(on_press=on_press)
listener.start()

# UI：輸入欄與按鈕
ctk.CTkLabel(app, text="延遲啟動 (秒)").pack()
delay_entry = ctk.CTkEntry(app)
delay_entry.insert(0, "0")
delay_entry.pack()

ctk.CTkLabel(app, text="點擊間隔 (秒)").pack()
interval_entry = ctk.CTkEntry(app)
interval_entry.insert(0, "0.05")
interval_entry.pack()

ctk.CTkLabel(app, text="隨機變化範圍 (±秒)").pack()
variation_entry = ctk.CTkEntry(app)
variation_entry.insert(0, "0.01")
variation_entry.pack()

ctk.CTkLabel(app, text="點擊次數上限 (可空白)").pack()
limit_entry = ctk.CTkEntry(app)
limit_entry.pack()

ctk.CTkLabel(app, text="加入鍵盤動作（如 enter）").pack()
key_entry = ctk.CTkEntry(app)
key_entry.pack()

ctk.CTkButton(app, text="加入滑鼠位置", command=record_position).pack(pady=5)
ctk.CTkButton(app, text="加入鍵盤動作", command=add_key_action).pack(pady=5)
ctk.CTkButton(app, text="開始 / 停止", command=toggle_click).pack(pady=10)
ctk.CTkButton(app, text="儲存腳本", command=save_script).pack(pady=2)
ctk.CTkButton(app, text="讀取腳本", command=load_script).pack(pady=2)

# 狀態與日誌
ctk.CTkLabel(app, textvariable=status_var, font=ctk.CTkFont(size=16)).pack(pady=5)
log_label = ctk.CTkLabel(app, text="", justify="left", wraplength=480)
log_label.pack(pady=5)

# 👉 設定視窗圖示（.ico 檔）
try:
    icon_path = os.path.join(os.path.dirname(sys.argv[0]), "KeyPulse pro.ico")
    print(f"[圖示載入] 嘗試使用圖示：{icon_path}")
    app.iconbitmap(default=icon_path)
except Exception as e:
    print(f"[⚠️] 無法設定圖示：{e}")


app.mainloop()
