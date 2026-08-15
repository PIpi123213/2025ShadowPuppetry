import cv2
import mediapipe as mp

# 初始化 MediaPipe Hands 模块
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# 手势识别阈值
THUMB_UP_THRESHOLD = 0.2  # 越小越收得近

# 启动摄像头
cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
) as hands:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 翻转图像，符合镜像视觉习惯
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # 转换颜色空间
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        gesture_text = ""

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # 可视化关键点
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # 获取关键点坐标（相对于图像尺寸）
                landmarks = hand_landmarks.landmark
                thumb_tip = landmarks[4]    # 拇指指尖
                index_tip = landmarks[8]    # 食指指尖
                middle_tip = landmarks[12]  # 中指指尖
                ring_tip = landmarks[16]    # 无名指指尖
                pinky_tip = landmarks[20]   # 小指指尖

                # 判断是否为“点赞手势”：拇指竖直，其他手指弯曲靠近掌心
                if (thumb_tip.y < landmarks[3].y and  # 拇指翘起
                    all(f.y > landmarks[0].y for f in [index_tip, middle_tip, ring_tip, pinky_tip])):  # 其他指弯下
                    gesture_text = "👍 你比了一个赞！"

                if gesture_text:
                    cv2.putText(frame, gesture_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                1.2, (0, 255, 0), 3)

        # 显示结果
        cv2.imshow("Hand Gesture Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
