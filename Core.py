import math
import time
from ctypes import windll

import Sendinput as gmouse
import PID as PID
import cv2
import keyboard as kb
import numpy as np
import win32api

ai_data1 = open('./配置文件.ini', "r", encoding="UTF-8")
AI_config1 = ai_data1.readlines()
x_One_week_pixel = int(AI_config1[34][9:])
y_Half_week_pixel = int(AI_config1[35][9:])
vfov = float(AI_config1[31][7:])
hfov = float(AI_config1[32][7:])


# FOV
def HFOV(sub_s):
    hfov_ = math.radians(hfov)
    Unit_angle_pixels = x_One_week_pixel / math.radians(360)
    xpixels_sum = 1920
    filming_distance = xpixels_sum / 2 / math.tan(hfov_ / 2)
    Rotation_angle = math.atan(sub_s / filming_distance)
    Convert_mobile_pixels = Rotation_angle * Unit_angle_pixels
    return Convert_mobile_pixels


def VFOV(sub_s):
    vfov_ = math.radians(vfov)
    Unit_angle_pixels = y_Half_week_pixel / math.radians(180)
    ypixels_sum = 1080
    filming_distance = ypixels_sum / 2 / math.tan(vfov_ / 2)
    Rotation_angle = math.atan(sub_s / filming_distance)
    Convert_mobile_pixels = Rotation_angle * Unit_angle_pixels
    return Convert_mobile_pixels


TimeBeginPeriod = windll.winmm.timeBeginPeriod
HPSleep = windll.kernel32.Sleep
TimeEndPeriod = windll.winmm.timeEndPeriod


# 精准延迟
def Precise_delay(num):
    TimeBeginPeriod(1)
    HPSleep(int(num))  # 减少报错
    TimeEndPeriod(1)


# 截图
def Screenshot_Mode(ps_mode, pos_x, pos_y, mcx, mcy):
    window_size = (pos_x - mcx, pos_y - mcy, pos_x + mcx, pos_y + mcy)
    # 目标检测中心点
    core_x = int((window_size[2] - window_size[0]) / 2)
    core_y = int((window_size[3] - window_size[1]) / 2)
    if ps_mode == 0:
        from mss import mss
        Screenshot_value = mss()
        windows_size = {
            "left": window_size[0],
            "top": window_size[1],
            "width": window_size[2] - window_size[0],
            "height": window_size[3] - window_size[1],
        }
    elif ps_mode == 1:
        from d3dshot import create
        Screenshot_value = create("numpy", frame_buffer_size=100)

    return window_size, core_x, core_y, Screenshot_value


# 检测模式
def Detection_mode(Detect_mode, Screenshot_value, window_size):
    # MSS
    if Detect_mode == 0:
        img = Screenshot_value.grab(window_size)
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    # d3shot
    elif Detect_mode == 1:
        img = Screenshot_value.screenshot(region=window_size)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    return img


# PID初始化
kp = float(AI_config1[27][5:])
ki = float(AI_config1[28][5:])
kd = float(AI_config1[29][5:])
head_pid_x = PID.pid(0, kp, ki, kd)
body_pid_x = PID.pid(0, kp, ki, kd)

ps_mode = int(AI_config1[25][7:])
Detect_mode = int(AI_config1[25][7:])
pos_x = int(int(AI_config1[12][9:]) / 2)
pos_y = int(int(AI_config1[13][9:]) / 2)
mcx = int(AI_config1[14][8:])
mcy = int(AI_config1[15][8:])
window_size, core_x, core_y, Screenshot_value = Screenshot_Mode(ps_mode, pos_x, pos_y, mcx, mcy)
head_offset_value_x = float(AI_config1[7][13:])
head_offset_value_y = float(AI_config1[8][13:])
Window_border_x = int(AI_config1[17][9:])
Window_border_y = int(AI_config1[18][9:])
Body_offset_value_x = float(AI_config1[9][13:])
Body_offset_value_y = float(AI_config1[10][13:])

SD_yaqiang = False
Aim_where = 0


def body_attack_range(target_w):
    global Physical_attack_range
    if Aim_where == 0:
        Physical_attack_range = target_w * 0.7
        # print(Physical_attack_range)
    elif Aim_where == 1:
        Physical_attack_range = target_w * 1.1
        # print(Physical_attack_range)


def get_attackrange():
    return Physical_attack_range


# 计算瞄准坐标
def Aim_Target(target_x, target_y, target_w, target_h):
    x1 = head_pid_x.cmd_pid(HFOV(target_x - core_x - Window_border_x) + (target_w * head_offset_value_x))
    y1 = VFOV(target_y - core_y - Window_border_y) + (target_h * head_offset_value_y)
    # 头目标
    if SD_yaqiang:
        if win32api.GetAsyncKeyState(1) != 0:
            gmouse.mouse_xy(int(x1), int(0))
        else:
            gmouse.mouse_xy(int(x1), int(y1))
    else:
        gmouse.mouse_xy(int(x1), int(y1))
    time.sleep(0.004)


# 计算目标距离
def Target_Distance(targetx, targety, target_h):
    if Aim_where == 0:
        a = float(targetx - core_x)  # -412
        b = float(targety - core_y)  # -284
        dis = math.sqrt((float(a) ** 2) + (float(b) ** 2))
    elif Aim_where == 1:
        a = float(targetx - core_x)  # -412
        b = float((targety + target_h) - core_y)
        dis = math.sqrt((float(a) ** 2) + (float(b) ** 2))
    return dis


Physical_attack_range = int(AI_config1[21][9:])
Spot_fire = int(AI_config1[5][9:])


def change_offset(Offset, Aimwhere):
    global head_offset_value_y
    global Aim_where
    head_offset_value_y = Offset
    Aim_where = Aimwhere


def change_YQ_mode(SDYQ=False):
    global SD_yaqiang
    SD_yaqiang = SDYQ


def close_input():
    kb.block_key('A')
    kb.block_key('D')
    kb.block_key('W')
    kb.block_key('S')
    kb.release('A')
    kb.release('D')
    kb.release('W')
    kb.release('S')


def open_input():
    kb.unblock_key('A')
    kb.unblock_key('W')
    kb.unblock_key('D')
    kb.unblock_key('S')


def other_gun():
    kb.press('2')
    Precise_delay(50)
    kb.release('2')


def knife_gun():
    kb.press('3')
    kb.release('3')
    Precise_delay(200)
    kb.press('1')
    kb.release('1')


def juji_pid():
    head_pid_x.Kp = float(AI_config1[41][5:])
    head_pid_x.Ki = float(AI_config1[42][5:])
    head_pid_x.Kd = float(AI_config1[43][5:])


def buqiang_pid():
    head_pid_x.Kp = float(AI_config1[27][5:])
    head_pid_x.Ki = float(AI_config1[28][5:])
    head_pid_x.Kd = float(AI_config1[29][5:])


def menu():
    print("=================菜单===================")
    print("打开调试模式(PID)", "                             --------快捷键F1")
    print("普通模式：手动触发自瞄（按住鼠标右键瞄准）", "          --------快捷键F2")
    print("狙击模式：(侧键自动急停瞬狙开火切枪/右键自动开火)", "   --------快捷键F3")
    print("手动自瞄+自动开火(自带压枪)", "                     --------快捷键F4")
    print("手动压枪模式", "                                 --------快捷键F5")
    print("关闭自瞄", "                                    --------快捷键F6")
    print("攻击部位:头部", "                                --------快捷键Ctrl+5")
    print("攻击部位:身体", "                                --------快捷键Ctrl+6")
    print("攻击部位:脖子", "                                --------快捷键Ctrl+7")
    print("安全退出AI", "                                   --------快捷键Ctrl+8")
    print("自定义PID参数F7-F12分别是kp,ki,kd,的加减操作")
    print("========================================")
