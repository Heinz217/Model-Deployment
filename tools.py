import time
import pyautogui
import pyperclip


# 要明确：我们只负责传送文本至服务器；还是服务器调取我们自己的ui界面
# send和get函数：需要对接服务器来实现
# 关于多人访问：需要服务器传给我们用户的id(按时间排列)，需要一个逻辑来调度。储存用户的信息
# 我来写一个switch函数，负责调度访问，并进行内存清理

# 移动并完成右键按压
def right_click(x, y):
    pyautogui.moveTo(x, y)
    pyautogui.mouseDown(button='right')
    pyautogui.mouseUp(button='right')


# 移动鼠标到指定位置
def move_mouse(x, y):
    pyautogui.moveTo(x, y)


# 使用Ctrl+C复制选中的内容
def copy():
    pyautogui.hotkey('ctrl', 'c')


# 使用Ctrl+V粘贴
def paste():
    pyautogui.hotkey('ctrl', 'v')


def click(x, y):
    pyautogui.click(x, y)


# def get():

# def send():

# (x1,y1):右下位，(x2,y2):左上位，(x3,y3):对话框,(x4,y4):发送,(x5,y5):清除
def cli_send(x3, y3, x4, y4, text_list):
    # mes=get()
    text_list = ["你好"]
    mes = " ".join(text_list)
    pyperclip.copy(mes)
    pyautogui.click(x3, y3)
    paste()
    pyautogui.click(x4, y4)


def cs_repeat(x1, y1, x2, y2, x3, y3, x4, y4, x5, y5):
    time.sleep(3)  # 等待3秒后进行复制
    pyautogui.mouseDown(x=x1, y=y1, button='left')
    move_mouse(x2, y2)
    pyautogui.mouseUp()
    copy()
    get_mes = pyperclip.paste()
    get_arr = get_mes.split()
    pyautogui.click(x5, y5)
    # send()This is a sample text
    return get_arr


# 80%缩放
def message():
    x1, y1, x2, y2, x3, y3, x4, y4, x5, y5 = 2414, 1239, 616, 381, 611, 1341, 1042, 1507, 1985, 1518
    time.sleep(3)  # 开始时缓冲3秒
    pyautogui.FAILSAFE = True
    cli_send(x3, y3, x4, y4,text_list="你好")
    message = cs_repeat(x1, y1, x2, y2, x3, y3, x4, y4, x5, y5)
    message_p = " ".join(message)
    return message_p
