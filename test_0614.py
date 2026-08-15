import time
import Adafruit_PCA9685
import threading

# 初始化PCA9685和舵机
servo_pwm = Adafruit_PCA9685.PCA9685(busnum=1)
servo_pwm.set_pwm_freq(60)  # 设置频率为60HZ

# 初始舵机角度
pid_X_P = 150
pid_Y_P = 150

# 舵机控制函数（循环变换角度测试）
def Robot_servo():
    global pid_X_P, pid_Y_P
    while True:
        servo_pwm.set_pwm(0, 0, pid_X_P)
        servo_pwm.set_pwm(1, 0, pid_Y_P)
        servo_pwm.set_pwm(2, 0, pid_X_P)
        servo_pwm.set_pwm(3, 0, pid_Y_P)
        servo_pwm.set_pwm(4, 0, pid_X_P)
        servo_pwm.set_pwm(5, 0, pid_Y_P)
        servo_pwm.set_pwm(6, 0, pid_X_P)
        
        print("X舵机角度PWM值:", pid_X_P, "Y舵机角度PWM值:", pid_Y_P)
        time.sleep(1)
        #pid_X_P = 600 if pid_X_P == 150 else 150
        #pid_Y_P = 600 if pid_Y_P == 150 else 150

# 启动控制线程
servo_tid = threading.Thread(target=Robot_servo)
servo_tid.setDaemon(True)
servo_tid.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n [INFO] 退出程序\n")
