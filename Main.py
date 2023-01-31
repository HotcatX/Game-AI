import random
import threading
from pynput import keyboard
from pynput.mouse import Button, Listener
import os


heart_jump = 1
def listen():
    threading._start_new_thread(mouseListener, ())
    threading._start_new_thread(Infer, ())
    threading._start_new_thread(keyboard_Listener, ())


def copyfile(srcfile, dstpath):  # 复制函数
    if not os.path.isfile(srcfile):
        print("%s not exist!" % srcfile)
    else:
        fpath, fname = os.path.split(srcfile)  # 分离文件名和路径
        if not os.path.exists(dstpath):
            os.makedirs(dstpath)  # 创建路径
        shutil.copy(srcfile, dstpath + fname)  # 复制文件
        print("copy %s -> %s" % (srcfile, dstpath + fname))


def copy_dll():
    filename = 'C:/Windows/System32/pywintypes38.dll'
    filename2 = 'C:/Windows/System32/pythoncom38.dll'
    if not os.path.exists(filename):
        print("检测到pywintypes38.dll缺失，自动修补...")
        copyfile('./dll/pywintypes38.dll', 'C:/Windows/System32/')
    if not os.path.exists(filename2):
        print("检测到pythoncom38.dll缺失，自动修补...")
        copyfile('./dll/pythoncom38.dll', 'C:/Windows/System32/')


def mouse_click(x, y, button, pressed):
    global Detection_switch
    global juji_mode
    if pressed and button == Button.x2:
        Detection_switch = True
        juji_mode = True
    elif not pressed and button == Button.x2:
        Detection_switch = False
        juji_mode = False
    if pressed and button == Button.right:
        if Analog_input:
            pass
        else:
            Detection_switch = True
    elif not pressed and button == Button.right:
        if Analog_input:
            pass
        else:
            Detection_switch = False


def on_press(key):
    global Detection_switch
    if key == keyboard.Key.alt_l:
        Detection_switch = True


def on_release(key):
    global Detection_switch
    global jujikaihuo
    global exit_autofire
    global Aiming
    global exit_AI
    if key == keyboard.Key.alt_l:
        Detection_switch = False
    elif key == keyboard.Key.f2:
        reset_mode()
        Aiming = True
        print("普通模式：手动触发自瞄（按住鼠标右键瞄准）", "*********开启成功")
    elif key == keyboard.Key.f3:
        reset_mode()
        time.sleep(0.1)
        Aiming = True
        jujikaihuo = True
        exit_autofire = False
        change_timesleep(change=True)
        juji_pid()
        threading._start_new_thread(AutoFire, ())
        print("狙击模式：右键和自瞄+自动开火效果一样/侧键自动瞬狙切手枪", "*********开启成功")
    elif key == keyboard.Key.f1:
        global debug_mode
        debug_mode = not debug_mode
        print("调试模式(PID显示）", "*********切换成功")
        if not debug_mode:
            menu()
    elif key == keyboard.Key.f4:
        reset_mode()
        Aiming = True
        exit_autofire = False
        threading._start_new_thread(AutoFire, ())
        print("自瞄+自动开火", "*********开启成功")
    elif key == keyboard.Key.f5:
        reset_mode()
        Aiming = True
        change_YQ_mode(SDYQ=True)
        print("手动压枪", "*********开启成功")
    elif key == keyboard.Key.f6:
        print("关闭所有", "*********关闭成功")
        reset_mode()
    elif str(key) == r"<53>":
        print("攻击部位:头部", "*********开启成功")
        change_offset(0, 0)
    elif str(key) == r"<54>":
        print("攻击部位:胸部", "*********开启成功")
        change_offset(0.5, 1)
    elif str(key) == r"<55>":
        print("攻击部位:脖子", "*********开启成功")
        change_offset(0.15, 1)
    elif str(key) == r"<56>":
        print("AI已安全关闭")
        reset_mode()
        exit_AI = True

    # PID调参
    elif key == keyboard.Key.f7:
        head_pid_x.Kp += 0.1
    elif key == keyboard.Key.f8:
        head_pid_x.Ki += 0.01
    elif key == keyboard.Key.f9:
        head_pid_x.Kd += 0.01
    elif key == keyboard.Key.f10:
        head_pid_x.Kp -= 0.1
    elif key == keyboard.Key.f11:
        head_pid_x.Ki -= 0.01
    elif key == keyboard.Key.f12:
        head_pid_x.Kd -= 0.01


def reset_mode():
    global Aiming
    global exit_autofire
    global jujikaihuo
    Aiming = False
    jujikaihuo = False
    exit_autofire = True
    change_YQ_mode(SDYQ=False)
    change_timesleep(change=False)
    buqiang_pid()


def mouseListener():
    with Listener(on_click=mouse_click) as listener:
        listener.join()


def keyboard_Listener():
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()


def shun_ju():
    global Analog_input
    Analog_input = True
    gmouse.mouse_down(2)
    Precise_delay(5)
    gmouse.mouse_up(2)
    Analog_input = False
    Precise_delay(25)
    gmouse.mouse_down(1)
    Precise_delay(5)
    gmouse.mouse_up(1)


def AutoFire(Firestart=True):
    global Detection_switch
    from Grab import return_info
    while Firestart:
        if exit_autofire:
            break
        if Detection_switch:
            distance, target_list = return_info()
            attack_range = get_attackrange()
            if len(target_list):
                if distance < attack_range + Window_border_y:
                    if jujikaihuo:
                        if juji_mode:
                            shun_ju()
                            other_gun()
                        else:
                            gmouse.mouse_down(1)
                            Precise_delay(Spot_fire)
                            gmouse.mouse_up(1)
                            Precise_delay(random.randint(30, 70))
                    elif attack_range > 10:
                        gmouse.mouse_down(1)
                        Precise_delay(Spot_fire)
                        gmouse.mouse_up(1)
                        Precise_delay(random.randint(20, 50))
                    else:
                        gmouse.mouse_down(1)
                        Precise_delay(Spot_fire)
                        gmouse.mouse_up(1)
                        Precise_delay(random.randint(140, 160))
        time.sleep(0.001)


def menu():
    print("=================菜单===================")
    print("打开调试模式(PID)", "                             --------快捷键F1")
    print("普通模式：手动触发自瞄（按住鼠标右键瞄准）", "          --------快捷键F2")
    print("狙击模式：(侧键自动瞬狙开火切枪/右键自动开火)", "   --------快捷键F3")
    print("手动自瞄+自动开火(自带压枪)", "                     --------快捷键F4")
    print("手动压枪模式", "                                 --------快捷键F5")
    print("关闭自瞄", "                                    --------快捷键F6")
    print("攻击部位:头部", "                                --------快捷键Ctrl+5")
    print("攻击部位:身体", "                                --------快捷键Ctrl+6")
    print("攻击部位:脖子", "                                --------快捷键Ctrl+7")
    print("安全退出AI", "                                   --------快捷键Ctrl+8")
    print("自定义PID参数F7-F12分别是kp,ki,kd,的加减操作")
    print("========================================")


if heart_jump:
    copy_dll()
    from Core import *
    from Grab import Infer, Transport_info, change_timesleep
    import Sendinput as gmouse

    listen()
    Detection_switch = False
    Aiming = False
    Juji_mode = False
    exit_autofire = False
    juji_mode = False
    jujikaihuo = False
    exit_AI = False
    debug_mode = False
    Analog_input = False
    menu()
    while heart_jump:
        if exit_AI:
            break
        elif Aiming:
            if Detection_switch:
                if debug_mode:
                    print("当前KP:", {head_pid_x.Kp}, "当前Ki:", {head_pid_x.Ki}, "当前Kd:", {head_pid_x.Kd})
                    Transport_info(aim_start=True)
                else:
                    Transport_info(aim_start=True)
            else:
                Transport_info(aim_start=False)

        time.sleep(0.001)
