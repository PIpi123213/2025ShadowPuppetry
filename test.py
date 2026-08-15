import time
import threading
import Adafruit_PCA9685

# ====== 参数设置 ======
CHANNEL = 7
CENTER_PULSE_US = 1850
MAX_DELTA = 800 #控制速度
VELOCITY_UNITS_PER_SEC = 1.0  # 每秒1单位 
MOVEMENT_THRESHOLD = 0.03     # 忽略微小变动
DEFAULT_SPEED = 100           # 运动速度百分比
MOVE_STEP = 0.1               # 按键调整的单位    0.1 单位 就等价于 0.1 秒时间的移动量

# ====== 修正因子 ======
LEFT_CORRECTION = 1.00
RIGHT_CORRECTION = 1.06
ARRIVAL_MARGIN = 0.02

# ====== 状态变量 ======
target_X = 0.0
current_position = 0.0

# 舵机初始化
servo_pwm = Adafruit_PCA9685.PCA9685(busnum=1)
servo_pwm.set_pwm_freq(60)

def pulse_us_to_pwm(pulse_us): # 将“微秒脉宽”转换为 PCA9685 的 12位 PWM值
    return int(pulse_us / 20000 * 4096)

def set_servo_pulse_us(channel, pulse_us):
    pwm_val = pulse_us_to_pwm(pulse_us)
    servo_pwm.set_pwm(channel, 0, pwm_val)

def set_motor_speed(channel, speed_percent):
    speed_percent = max(-100, min(100, speed_percent))
    pulse_us = CENTER_PULSE_US + MAX_DELTA * (speed_percent / 100.0) # 计算目标脉宽（单位：微秒）
    set_servo_pulse_us(channel, pulse_us)

def stop_servo(channel):
    set_motor_speed(channel, 0)

# 控制线程变量
stop_event = threading.Event()
move_thread = None

def control_loop():
    global current_position, target_X

    prev_time = time.time()

    while not stop_event.is_set():
        now = time.time()
        dt = now - prev_time
        prev_time = now
        # target_X = max(-1.0, min(1.0, target_X))
        dx = target_X - current_position

        # 移动判断
        if abs(dx) < max(MOVEMENT_THRESHOLD, ARRIVAL_MARGIN):
        #if abs(dx) < MOVEMENT_THRESHOLD:
            current_position = target_X
            stop_servo(CHANNEL)
            continue

        direction = 1 if dx > 0 else -1


        set_motor_speed(CHANNEL, direction * DEFAULT_SPEED)

        # ✅ 引入方向修正系数
        correction = RIGHT_CORRECTION if direction > 0 else LEFT_CORRECTION
        delta_pos = VELOCITY_UNITS_PER_SEC * dt * direction * correction
        current_position += delta_pos

        '''# 估算新位置（模拟实时物理位置变化）
        delta_pos = VELOCITY_UNITS_PER_SEC * dt * direction

        current_position += delta_pos'''

        #print(f"目标位置{target_X}，实际位置{current_position}") 

        # 如果超过目标，强制对齐并停止
        if (direction > 0 and current_position >= target_X) or (direction < 0 and current_position <= target_X):
            current_position = target_X
            stop_servo(CHANNEL)

        time.sleep(0)  # 非阻塞 



# 输入控制
def input_loop():
    global target_X
    print("✅ 输入任意正负小数移动位置，例如 '0.2' 向右移0.2，'-0.1' 向左移0.1，'q' 退出")
    while not stop_event.is_set():
        cmd = input("输入移动步长或 'q' 退出: ").strip().lower()
        if cmd == 'q':
            stop_event.set()
            break
        try:
            delta = float(cmd)
            target_X = round(target_X + delta, 3)
            print(f"🎯 目标位置更新为: {target_X}")
        except ValueError:
            print("❌ 输入无效，请输入小数或 'q'")
def start_controller():
    global move_thread
    stop_event.clear()
    move_thread = threading.Thread(target=control_loop)
    move_thread.daemon = True
    move_thread.start()

def stop_controller():
    stop_event.set()
    stop_servo(CHANNEL)
    if move_thread:
        move_thread.join()

# 主程序
if __name__ == "__main__":
    try:
        print("🚀 启动动态舵机控制器（支持实时中断与调整）")
        start_controller()
        input_loop()
    except KeyboardInterrupt:
        print("\n[INFO] 手动退出")
    finally:
        stop_controller()
        print("🛑 舵机停止")