import threading
import time

import torch
import ctypes
import win32con
import win32gui

from Core import *
from models.common import DetectMultiBackend
from utils.augmentations import letterbox
from utils.general import (check_img_size, non_max_suppression, scale_coords, xyxy2xywh)
from utils.plots import Annotator, colors
from utils.torch_utils import select_device

# 初始化
ai_data1 = open('./配置文件.ini', "r", encoding="UTF-8")
AI_config1 = ai_data1.readlines()
# 截图模式
ps_mode = int(AI_config1[25][7:])
Detect_mode = int(AI_config1[25][7:])
# 屏幕中心
pos_x = int(int(AI_config1[12][9:]) / 2)
pos_y = int(int(AI_config1[13][9:]) / 2)
print("你配置文件的分辨率为:", pos_x * 2, "*", pos_y * 2, "请确保其与你游戏内分辨率一致。")
# 检测范围
mcx = int(AI_config1[14][8:])
mcy = int(AI_config1[15][8:])
window_size, core_x, core_y, Screenshot_value = Screenshot_Mode(ps_mode, pos_x, pos_y, mcx, mcy)
# 推理
device = 'cuda:0'
weights = 'weights/cf6200.engine'
data = 'data/coco128.yaml'
imgsz = int(640)
half = True
max_det = 1000
agnostic_nms = False
conf_thres = float(AI_config1[2][6:])
iou_thres = float(AI_config1[3][5:])
open_windows = int(AI_config1[37][7:])
classes = 0
Aim_where = 0
start_aim = False
self_timesleep = False
distance = 0
det = []

device = select_device(device)
model = DetectMultiBackend(weights, device=device)
stride, names, pt, engine = model.stride, model.names, model.pt, model.engine
imgsz = check_img_size(imgsz, s=stride)
u32 = ctypes.windll.user32

# Half
half &= (pt or engine) and device.type != 'cpu'
if pt:
    model.model.half() if half else model.model.float()


def Infer():
    global distance
    global det
    while True:
        t0 = time.time()
        im = Detection_mode(Detect_mode, Screenshot_value, window_size)

        img0 = im
        im = letterbox(im, imgsz, stride=stride)[0]
        im = im.transpose((2, 0, 1))[::-1]
        im = np.ascontiguousarray(im)

        im = torch.from_numpy(im).to(device)
        im = im.half() if half else im.float()  # uint8 to fp16/32
        im /= 255  # 0 - 255 to 0.0 - 1.0
        if len(im.shape) == 3:
            im = im[None]  # expand for batch dim

        # Inference

        pred = model(im, augment=False, visualize=False)

        # NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
        annotator = Annotator(img0, line_width=3, example=str(names))
        t00 = time.time()

        # Second-stage classifier (optional)
        # pred = utils.general.apply_classifier(pred, classifier_model, im, im0s)
        # Process predictions
        _, det = next(enumerate(pred))
        s = ''
        s += '%gx%g ' % im.shape[2:]
        aims = []
        if len(det):
            det[:, :4] = scale_coords(im.shape[2:], det[:, :4], img0.shape).round()
            for *xyxy, conf, cls in reversed(det):
                xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4))).view(-1).tolist()
                # print(xywh)
                line = (cls, *xywh, conf)  # label format
                aim = ('%g ' * len(line)).rstrip() % line
                aim = aim.split(' ')
                aims.append(aim)
                cls = int(cls)
                try:
                    label = f'{names[cls]} {conf:.2f}'
                except IndexError:
                    pass
                annotator.box_label(xyxy, label, color=colors(cls, True))
                dis_list = []
            for i in aims:
                dis = Target_Distance(targetx=float(i[1]), targety=float(i[2]), target_h=float(i[4]))
                dis_list.append(dis)

            distance = min(dis_list)
            det = aims[dis_list.index(min(dis_list))]
            target_x = float(det[1])
            target_y = float(det[2])
            target_w = float(det[3])
            target_h = float(det[4])
            if start_aim:
                threading._start_new_thread(body_attack_range, (target_w,))
                threading._start_new_thread(Aim_Target, (target_x, target_y, target_w, target_h))
        if self_timesleep:
            time.sleep(0.003)
        if open_windows:
            img0 = annotator.result()
            if t00 - t0:
                fps = 1 / (t00 - t0)
            cv2.putText(img0, ':{0}'.format(float('%.1f' % fps)), (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("winname", img0)
            hwnd = win32gui.FindWindow(None, 'winname')
            CVRECT = cv2.getWindowImageRect('winname')
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()  # 1 millisecond


def Transport_info(aim_start=False):
    global start_aim
    start_aim = aim_start


def return_info():
    return distance, det


def change_timesleep(change=False):
    global self_timesleep
    self_timesleep = change
