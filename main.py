import cv2
from hand_detection import HandDetector
from communication import Communication
import test_slow
import test

def main():
# 初始化手部检测
    detector = HandDetector()
    # 初始化通讯
    comm = Communication()
    comm.start_server()

    test_slow.start_servo_thread()
    test.start_controller()

    try:
        while True:
            # 处理每一帧并发送手部位置信息
            img = detector.process_frame(callback=comm.send_point_info)
            if img is None:
                continue

            # 显示图像
            cv2.imshow('Hand Tracking', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # 清理资源
        detector.release()
        comm.close()

if __name__ == "__main__":
    main()

