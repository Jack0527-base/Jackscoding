import cv2
import numpy as np

# HSV 颜色阈值（按需校准）
red_lower1 = np.array([0, 70, 50])
red_upper1 = np.array([10, 255, 255])
red_lower2 = np.array([170, 70, 50])
red_upper2 = np.array([180, 255, 255])
yellow_lower = np.array([20, 100, 100])
yellow_upper = np.array([30, 255, 255])
blue_lower = np.array([100, 150, 50])
blue_upper = np.array([140, 255, 255])
green_lower = np.array([75, 100, 100])
green_upper = np.array([95, 255, 255])

# 摄像头初始化
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 形态学核
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

def ellipse_aspect(cnt):
    if len(cnt) >= 5:
        (_, _), (ea, eb), _ = cv2.fitEllipse(cnt)
        major = max(ea, eb)
        minor = min(ea, eb)
        return minor / major if major > 0 else 0
    return 0


def classify_object(cnt):
    # 面积与周长
    area = cv2.contourArea(cnt)
    peri = cv2.arcLength(cnt, True)
    if area <= 0 or peri <= 0:
        return "Unknown", (0, 0)
    circularity = 4 * np.pi * area / (peri * peri)

    # 外接矩形长宽比
    x, y, w, h = cv2.boundingRect(cnt)
    aspect_ratio = float(w) / h if h > 0 else 0

    # 凸度
    hull = cv2.convexHull(cnt)
    hull_area = cv2.contourArea(hull)
    solidity = float(area) / hull_area if hull_area > 0 else 0

    # 椭圆拟合长短轴比
    ell_ratio = ellipse_aspect(cnt)

    # 遮挡补偿：凸包重算圆度
    if solidity < 0.9:
        per_hull = cv2.arcLength(hull, True)
        if per_hull > 0:
            circularity = 4 * np.pi * hull_area / (per_hull * per_hull)

    # 判决
    if circularity > 0.8 and ell_ratio > 0.9:
        obj = "Sphere"
    else:
        obj = "Drum Cylinder"

    # 中心点
    (cx, cy), _ = cv2.minEnclosingCircle(cnt)
    return obj, (int(cx), int(cy))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 分别生成三色及绿色掩码
    mask_r1 = cv2.inRange(hsv, red_lower1, red_upper1)
    mask_r2 = cv2.inRange(hsv, red_lower2, red_upper2)
    mask_red = cv2.bitwise_or(mask_r1, mask_r2)
    mask_yellow = cv2.inRange(hsv, yellow_lower, yellow_upper)
    mask_blue = cv2.inRange(hsv, blue_lower, blue_upper)
    mask_green = cv2.inRange(hsv, green_lower, green_upper)

    masks = [mask_red, mask_yellow, mask_blue, mask_green]

    for mask in masks:
        # 形态学闭运算
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if cv2.contourArea(cnt) < 500:
                continue

            obj_type, center = classify_object(cnt)
            cx, cy = center

            # 绘制轮廓与标签
            cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)
            cv2.putText(frame, obj_type, (cx - 40, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.drawMarker(frame, (cx, cy), (0, 0, 255),
                           markerType=cv2.MARKER_CROSS, markerSize=15, thickness=2)

    cv2.imshow("Result", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()