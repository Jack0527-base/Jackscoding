import cv2
import numpy as np

# 初始化摄像头控制
camera_on = True
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 按钮位置参数
button_positions = {
    "switch": (10, 10, 120, 40),    # x1, y1, x2, y2
    "refresh": (140, 10, 260, 40)
}

def draw_controls(frame):
    """绘制控制面板"""
    # 绘制半透明背景
    control_bg = np.zeros((60, 640, 3), dtype=np.uint8)
    frame[0:60, 0:640] = cv2.addWeighted(frame[0:60, 0:640], 0.7, control_bg, 0.3, 0)
    
    # 绘制开关按钮
    switch_color = (0, 255, 0) if camera_on else (0, 0, 255)
    cv2.rectangle(frame, 
                 (button_positions["switch"][0], button_positions["switch"][1]),
                 (button_positions["switch"][2], button_positions["switch"][3]),
                 switch_color, -1)
    cv2.putText(frame, "CAMERA ON" if camera_on else "CAMERA OFF", 
               (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    
    # 绘制刷新按钮
    cv2.rectangle(frame, 
                 (button_positions["refresh"][0], button_positions["refresh"][1]),
                 (button_positions["refresh"][2], button_positions["refresh"][3]),
                 (255, 200, 0), -1)
    cv2.putText(frame, "REFRESH", (160, 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    return frame

def mouse_callback(event, x, y, flags, param):
    """鼠标事件处理"""
    global camera_on, cap
    if event == cv2.EVENT_LBUTTONDOWN:
        # 检测开关按钮点击
        if (button_positions["switch"][0] < x < button_positions["switch"][2] and
            button_positions["switch"][1] < y < button_positions["switch"][3]):
            camera_on = not camera_on
            if not camera_on and cap.isOpened():
                cap.release()
        
        # 检测刷新按钮点击
        if (button_positions["refresh"][0] < x < button_positions["refresh"][2] and
            button_positions["refresh"][1] < y < button_positions["refresh"][3]):
            if not cap.isOpened():
                cap = cv2.VideoCapture(0)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera_on = True

def process_frame(frame):
    """图像预处理流水线"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7,7), 0)
    binary = cv2.adaptiveThreshold(blurred, 255, 
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    kernel = np.ones((5,5), np.uint8)
    return cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

def detect_line_region(binary_img):
    """黑线检测算法"""
    cnts = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = cnts[-2]
    
    if not contours:
        return None, None

    max_contour = max(contours, key=cv2.contourArea)
    if cv2.contourArea(max_contour) < 500:
        return None, None

    try:
        [vx, vy, x, y] = cv2.fitLine(max_contour, cv2.DIST_L2, 0, 0.01, 0.01)
        slope = vy[0] / vx[0]
        intercept = y[0] - slope * x[0]
        y_max = binary_img.shape[0]
        x_start = int((y_max - intercept) / slope)
        x_end = int((y_max*0.6 - intercept) / slope)
    except:
        return None, None

    return (x_start, y_max, x_end, int(y_max*0.6)), max_contour

# 创建窗口并设置鼠标回调
cv2.namedWindow('Line Tracking')
cv2.setMouseCallback('Line Tracking', mouse_callback)

while True:
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

    frame = np.zeros((480,640,3), dtype=np.uint8)
    processed = np.zeros((480,640), dtype=np.uint8)
    
    if camera_on and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue
            
        processed = process_frame(frame)
        line_coords, _ = detect_line_region(processed)
        
        if line_coords is not None:
            x1, y1, x2, y2 = line_coords
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            deviation = x1 - 320
            cv2.putText(frame, f"Deviation: {deviation}px", (10,90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            status_text = "STEERING ADJUST" if abs(deviation) > 50 else "NORMAL"
            status_color = (0,0,255) if abs(deviation) > 50 else (0,255,0)
            cv2.putText(frame, status_text, (10,120),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        else:
            cv2.putText(frame, "LINE LOST", (10,90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

    # 绘制控制面板
    frame = draw_controls(frame)
    
    # 显示双画面
    cv2.imshow('Line Tracking', frame)
    cv2.imshow('Processed View', processed)

# 资源释放
if cap.isOpened():
    cap.release()
cv2.destroyAllWindows()