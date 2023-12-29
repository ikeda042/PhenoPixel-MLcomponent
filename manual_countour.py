import cv2
import numpy as np
import datetime

class ImageDrawer:
    def __init__(self, image_path):
        self.image_path = image_path
        self.original_img = cv2.imread(image_path)
        try:
            self.original_img_size = self.original_img.shape[:2]
        except ValueError as e:
            print(e)
            exit()
        self.original_img = cv2.resize(self.original_img, (800, 800))
        self.img = self.original_img.copy()
        self.points = []

    def draw_point(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.points.append((x, y))
            cv2.circle(self.img, (x, y), 3, (0, 0, 255), -1)  
            self.redraw_image()

    def interpolate_points(self, p1, p2, num_points=10):
        return [(int(p1[0] + i * (p2[0] - p1[0]) / num_points), int(p1[1] + i * (p2[1] - p1[1]) / num_points)) for i in range(1, num_points)]

    def redraw_image(self):
        self.img = self.original_img.copy()
        all_points = []

        if len(self.points) > 1:
            for i in range(len(self.points)):
                all_points.append(self.points[i])
                next_point = self.points[(i + 1) % len(self.points)]
                all_points.extend(self.interpolate_points(self.points[i], next_point))

            for i in range(len(all_points) - 1):
                cv2.line(self.img, all_points[i], all_points[i + 1], (255, 0, 0), 2)
            cv2.line(self.img, all_points[-1], all_points[0], (255, 0, 0), 2)
        for point in self.points:
            cv2.circle(self.img, point, 5, (0, 0, 255), -1)

    def save_contour(self):
        contour_img = np.zeros(self.original_img.shape[:2], dtype=np.uint8)
        cv2.fillPoly(contour_img, [np.array(self.points)], 255)
        filename = f"{self.image_path.split('.')[0]}_label.png"
        contour_img_to_save = cv2.resize(contour_img, self.original_img_size)
        contour_img_to_save= cv2.threshold(contour_img_to_save, 127, 255, cv2.THRESH_BINARY)[1]

        cv2.imwrite(filename, contour_img_to_save)
        print(f"Contour image saved: {filename}")
        cv2.imshow("Saved Contour", contour_img)

    def run(self):
        cv2.namedWindow('image')
        cv2.setMouseCallback('image', self.draw_point)

        while True:
            cv2.imshow('image', self.img)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:  # ESCキーで終了
                break
            elif k == ord('z'):  # 'z'キーで最後の点を削除
                if self.points:
                    self.points.pop()
                    self.redraw_image()
            elif k == 13:  # Enterキーで輪郭出力
                self.save_contour()

        cv2.destroyAllWindows()

# 使用例
drawer = ImageDrawer('1.png')
drawer.run()
