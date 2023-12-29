import cv2
import numpy as np

class ImageDrawer:
    def __init__(self, image_path):
        self.image_path = image_path
        self.original_img = cv2.imread(image_path)
        try:
            self.original_img_size = self.original_img.shape[:2]
        except AttributeError as e:
            print(f"Image load error: {e}")
            exit()
        self.original_img = cv2.resize(self.original_img, (800, 800))
        self.img = self.original_img.copy()
        self.points = []
        self.points_to_draw = []

    def draw_point(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.points.append((x, y))
            cv2.circle(self.img, (x, y), 1, (0, 0, 255), -1)  
            self.redraw_image()

    def interpolate_points(self, p1, p2, num_points=10):
        return [(int(p1[0] + i * (p2[0] - p1[0]) / num_points), int(p1[1] + i * (p2[1] - p1[1]) / num_points)) for i in range(1, num_points)]

    def bezier_interpolate(self, points, num_points=100):
        if len(points) < 3:
            return self.interpolate_points(points[0], points[1], num_points)
        
        curve = []
        for t in np.linspace(0, 1, num=num_points):
            x = (1-t)**2*points[0][0] + 2*(1-t)*t*points[1][0] + t**2*points[2][0]
            y = (1-t)**2*points[0][1] + 2*(1-t)*t*points[1][1] + t**2*points[2][1]
            curve.append((int(x), int(y)))
        return curve

    def redraw_image(self):
        self.img = self.original_img.copy()
        all_points = []

        if len(self.points) > 2:
            for i in range(len(self.points)):
                p0 = self.points[i]
                p1 = self.points[(i + 1) % len(self.points)]
                p2 = self.points[(i + 2) % len(self.points)]
                point = self.bezier_interpolate([p0, p1, p2])
                all_points.extend(point)
                self.points_to_draw.append(point)
                

            for i in range(len(all_points) - 1):
                # 曲線の色を青に変更 (BGR形式で(255, 0, 0)は青色)
                cv2.line(self.img, all_points[i], all_points[i + 1], (0,255, 0), 2)
        for point in self.points:
            cv2.circle(self.img, point, 3, (0, 0, 255), -1)

    def get_bezier_contour(self):
        all_points = []
        if len(self.points) > 2:
            for i in range(len(self.points)):
                p0 = self.points[i]
                p1 = self.points[(i + 1) % len(self.points)]
                p2 = self.points[(i + 2) % len(self.points)]
                all_points.extend(self.bezier_interpolate([p0, p1, p2]))
        return np.array(all_points, dtype=np.int32)

    def save_contour(self):
        bezier_contour = self.get_bezier_contour()
        contour_img = np.zeros(self.original_img.shape[:2], dtype=np.uint8)
        cv2.drawContours(contour_img, [bezier_contour], -1, 255, thickness=cv2.FILLED)
        filename = f"{self.image_path.split('.')[0]}_label.png"
        contour_img_to_save = cv2.resize(contour_img, self.original_img_size)
        contour_img_to_save = cv2.threshold(contour_img_to_save, 127, 255, cv2.THRESH_BINARY)[1]

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

drawer = ImageDrawer('0.png')
drawer.run()
