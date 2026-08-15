import time
import Adafruit_PCA9685
import threading

CHANNEL_arm0 = 0
CHANNEL_arm1 = 1
CHANNEL_arm2 = 2
CHANNEL_arm3 = 3
CHANNEL_head = 4
CHANNEL_leg1 = 5
CHANNEL_leg2 = 6
# 初始化PCA9685和舵机
servo_pwm = Adafruit_PCA9685.PCA9685(busnum=1)
servo_pwm.set_pwm_freq(60)  # 60Hz

# 当前PWM值
pid_arm0 = 150
pid_arm1 = 150
pid_arm2 = 150
pid_arm3 = 150
pid_head = 150
pid_leg1 = 150
pid_leg2 = 150

# 目标PWM值
target_arm0 = 150
target_arm1 = 150
target_arm2 = 150
target_arm3 = 150
target_head = 150
target_leg1 = 150
target_leg2 = 150

step = 4
interval = 0.01  # 每步间隔秒数（10ms）

def smooth_move(current, target):
    if current < target:
        return current + step
    elif current > target:
        return current - step
    else:
        return current

def Robot_servo():
    global pid_arm0 , pid_arm1 , pid_arm2 , pid_arm3 , pid_head , pid_leg1 , pid_leg2 , target_arm0 , target_arm1 , target_arm2 , target_arm3 , target_head , target_leg1 , target_leg2

    last_time = time.time()

    while True:
        now = time.time()
        if now - last_time >= interval:
            last_time = now

            pid_arm0 = smooth_move(pid_arm0, target_arm0)
            pid_arm1 = smooth_move(pid_arm1, target_arm1)
            pid_arm2 = smooth_move(pid_arm2, target_arm2)
            pid_arm3 = smooth_move(pid_arm3, target_arm3)
            pid_head = smooth_move(pid_head, target_head)
            pid_leg1 = smooth_move(pid_leg1, target_leg1)
            pid_leg2 = smooth_move(pid_leg2, target_leg2)



            servo_pwm.set_pwm(CHANNEL_arm0 , 0, pid_arm0)
            servo_pwm.set_pwm(CHANNEL_arm1 , 0, pid_arm1)
            servo_pwm.set_pwm(CHANNEL_arm2 , 0, pid_arm2)
            servo_pwm.set_pwm(CHANNEL_arm3 , 0, pid_arm3)
            servo_pwm.set_pwm(CHANNEL_head , 0, pid_head)
            servo_pwm.set_pwm(CHANNEL_leg1 , 0, pid_leg1)
            servo_pwm.set_pwm(CHANNEL_leg2 , 0, pid_leg2)
            

            # 这里可以取消注释打印，调试用
            #print(f"[{time.strftime('%H:%M:%S')}] PWM X: {pid_X_P}, PWM Y: {pid_Y_P},targetX:{target_X},targetY:{target_Y}")

        else:
            time.sleep(0.001)  # 空转等待，减少 CPU 占用

def start_servo_thread():
    """启动舵机控制线程"""
    servo_tid = threading.Thread(target=Robot_servo)
    servo_tid.daemon = True
    servo_tid.start()
    return servo_tid

#def main_loop():
   # """程序主循环，保持运行直到Ctrl+C退出"""
    #try:
      #  while True:
          #  time.sleep(1)
   # except KeyboardInterrupt:
        #print("\n[INFO] 程序退出")