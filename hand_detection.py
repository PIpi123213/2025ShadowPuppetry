import cv2
import mediapipe as mp
import numpy as np
import test_slow
import test

class HandDetector:
    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands()
        self.mpDraw = mp.solutions.drawing_utils
        self.handLmsStyle = self.mpDraw.DrawingSpec(color=(0, 0, 255), thickness=5)
        self.handConStyle = self.mpDraw.DrawingSpec(color=(0, 255, 0), thickness=8)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.prev_landmarks = {}  # 记录上一帧关键点位置
        self.MOVE_THRESHOLD = 6   # 移动像素阈值（单位：像素）

    def process_frame(self, callback=None):
        ret, img = self.cap.read()
        if not ret:
            return None

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = self.hands.process(imgRGB)
        imgHeight, imgWidth = img.shape[:2]

        if result.multi_hand_landmarks:
            for hand_idx, handLms in enumerate(result.multi_hand_landmarks):
                hand_type = result.multi_handedness[hand_idx].classification[0].label

                for i, lm in enumerate(handLms.landmark):
                    xPos = int(lm.x * imgWidth)
                    yPos = int(lm.y * imgHeight)

                    # 控制 test 中 target_X：右手中指（12）
                    if i == 12 and hand_type == "Right":
                        test.target_X = round(float(np.interp(640 - xPos, [0, 640], [-1.8, 1.8])), 3) #左右
                        print(f"手的位置{640-xPos}")

                    
                    if i in [8, 16] and hand_type == "Right":
                        yPos_flipped = 480 - yPos  # 反转坐标：手往上移动，值变大
                        key = f"{hand_type}_{i}"
                        prev_y = self.prev_landmarks.get(key, yPos_flipped)
                        delta_y = yPos_flipped - prev_y
                        self.prev_landmarks[key] = yPos_flipped

                        if abs(delta_y) > self.MOVE_THRESHOLD:
                            pwm_change = int(delta_y * 4)
                            if i == 8:
                                test_slow.target_leg1 = max(150, min(600, test_slow.target_leg1 + pwm_change))
                            elif i == 16:
                                test_slow.target_leg2 = max(150, min(600, test_slow.target_leg2 + pwm_change))
                             

                    # 控制 test_slow 中多个舵机：左手指尖上下移动
                    if i in [4, 8, 16, 20] and hand_type == "Left":
                        yPos_flipped = 480 - yPos  # 反转坐标：手往上移动，值变大
                        key = f"{hand_type}_{i}"
                        prev_y = self.prev_landmarks.get(key, yPos_flipped)
                        delta_y = yPos_flipped - prev_y
                        self.prev_landmarks[key] = yPos_flipped

                        if abs(delta_y) > self.MOVE_THRESHOLD:
                            pwm_change = int(delta_y * 4)
                            if i == 4:
                                test_slow.target_arm0 = max(150, min(600, test_slow.target_arm0 + pwm_change))
                            elif i == 8:
                                test_slow.target_arm1 = max(150, min(600, test_slow.target_arm1 + pwm_change))
                                #print(f"{test_slow.target_arm1 }")
                            elif i == 16:
                                test_slow.target_arm2 = max(150, min(600, test_slow.target_arm2 + pwm_change))
                            elif i == 20:
                                test_slow.target_arm3 = max(150, min(600, test_slow.target_arm3 + pwm_change))

                    if i == 12 and hand_type == "Left":
                        yPos_flipped = 480 - yPos  # 反转坐标：手往上移动，值变大
                        key = f"{hand_type}_{i}"
                        prev_y = self.prev_landmarks.get(key, yPos_flipped)
                        delta_y = yPos_flipped - prev_y
                        self.prev_landmarks[key] = yPos_flipped

                        if abs(delta_y) > self.MOVE_THRESHOLD:
                            pwm_change = int(delta_y * 4)
                            test_slow.target_head = max(150, min(600, test_slow.target_head + pwm_change))
                           
                    # 高亮显示关键点
                    if i in [0, 4, 8, 12, 16, 20]:
                        point_color = (0, 0, 255) if hand_type == "Left" else (255, 0, 0)
                        cv2.circle(img, (xPos, yPos), 8, point_color, cv2.FILLED)
                        cv2.putText(img, str(i), (xPos - 25, yPos + 5),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 2)

                        if callback:
                            callback(hand_type, i, xPos, yPos)

        return img

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()