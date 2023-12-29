import cv2
import numpy as np

def draw_point(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(img, (x, y), 2, (0, 0, 255), -1)  
        points.append((x, y))

def draw_contour():
    if len(points) > 1:
        for i in range(len(points) - 1):
            cv2.line(img, points[i], points[i + 1], (255, 0, 0), 2)
        cv2.line(img, points[-1], points[0], (255, 0, 0), 2)

img = np.zeros((100, 100, 3), np.uint8)
cv2.namedWindow('image')
points = []

cv2.setMouseCallback('image', draw_point)

while True:
    cv2.imshow('image', img)
    k = cv2.waitKey(1)
    if k == 27:  # ESCキーで終了
        break
    elif k == 13:  # Enterキーで輪郭を描画
        draw_contour()
    elif cv2.getWindowProperty('image', cv2.WND_PROP_VISIBLE) < 1:  
        break  # ウィンドウが閉じられた場合に終了

cv2.destroyAllWindows()
