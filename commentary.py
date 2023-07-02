import numpy as np
import cv2

class Commentary:
    def __init__(self, phrases, comment_label):
        self.phrases = phrases
        self.comment_label = comment_label
        self.timer_id = None

    def insert_newlines(self, text, every=8):
        return '\n'.join(text[i:i + every] for i in range(0, len(text), every))

    def random_comment(self):
        comment = np.random.choice(self.phrases)
        return self.insert_newlines(comment)

    def set_random_comment(self):
        comment = self.random_comment()
        self.comment_label.config(text=comment)
        self.timer_id = self.comment_label.after(20000, lambda: self.set_random_comment())

    def reset_timer(self):
        if self.timer_id is not None:
            self.comment_label.after_cancel(self.timer_id)
            self.timer_id = None
        # Set a delay before the next random comment is displayed
        self.timer_id = self.comment_label.after(20000, lambda: self.set_random_comment())

    def analyze_image(self, image):
        default_comment_list = []
        comment_list = []

        comment1 = self.color_greater_than_three(image)
        comment2 = self.color_less_than_three(image)

        if comment1:
            print(f"Triggered function: {self.color_greater_than_three.__name__}")
            default_comment_list.append(comment1)
        if comment2:
            print(f"Triggered function: {self.color_less_than_three.__name__}")
            default_comment_list.append(comment2)

        comment3 = self.more_than_five_shapes(image)
        if comment3:
            print(f"Triggered function: {self.more_than_five_shapes.__name__}")
            comment_list.append(comment3)
        comment4 = self.large_empty_space(image)
        if comment4:
            print(f"Triggered function: {self.large_empty_space.__name__}")
            comment_list.append(comment4)
        comment5 = self.large_number_of_lines(image)
        if comment5:
            print(f"Triggered function: {self.large_number_of_lines.__name__}")
            comment_list.append(comment5)
        comment6 = self.centered_content(image)
        if comment6:
            print(f"Triggered function: {self.centered_content.__name__}")
            comment_list.append(comment6)
        comment7 = self.dominant_color_temperature(image)
        if comment7:
            print(f"Triggered function: {self.dominant_color_temperature.__name__}")
            comment_list.append(comment7)
        comment8 = self.contains_pink(image)
        if comment8:
            print(f"Triggered function: {self.contains_pink.__name__}")
            comment_list.append(comment8)

        # If no other conditions met, add default comments
        if len(comment_list) == 0:
            comment_list = default_comment_list

        if comment_list:
            comment = np.random.choice(comment_list)
        else:
            comment = self.random_comment()
        comment = self.insert_newlines(comment)
        self.comment_label.config(text=comment)
        self.reset_timer()

    def color_greater_than_three(self, image):
        unique_colors = len(np.unique(image.reshape(-1, image.shape[2]), axis=0))
        if unique_colors > 3:
            return "多彩的作品"

    def color_less_than_three(self, image):
        unique_colors = len(np.unique(image.reshape(-1, image.shape[2]), axis=0))
        if unique_colors <= 3:
            return "单调中浮现的艺术"

    def more_than_five_shapes(self, image):
        # 首先将图片转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 使用阈值进行二值化处理，阈值设为127，最大值设为255
        ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        # 查找二值化图中的轮廓
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # 判断轮廓数量是否大于5
        if len(contours) > 5:
            return "蕴含几何的杰作"

    def large_empty_space(self, image, min_contour_area=5000):
        # Special case: If the image is completely white, trigger this function
        if np.all(image == 255):
            return "空白之处，留给观者无限的遐想"

        # Convert image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Threshold the image to get a binary image
        _, thresh = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY_INV)

        # Find contours in the threshold image
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours based on area
        large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]

        if len(large_contours) > 0:
            return "留白本身就是一种遐想"

    def large_number_of_lines(self, image, min_lines=5):
        # Convert image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Use Canny edge detection to get edges in the image
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Use Probabilistic Hough Line Transform to detect line segments in the image
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=10, maxLineGap=10)

        # If there are more than min_lines lines, return the comment
        if lines is not None and len(lines) > min_lines:
            return "线条的力量，使得作品充满张力"

    def centered_content(self, image, center_tolerance=0.1):
        # Convert image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Threshold the image
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

        # Find contours in the thresholded image
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Calculate the image's center coordinates
        center_x = image.shape[1] / 2
        center_y = image.shape[0] / 2

        # Calculate the tolerance for the center region
        tolerance_x = center_tolerance * image.shape[1]
        tolerance_y = center_tolerance * image.shape[0]

        # Initialize variables to hold total x and y coordinates
        total_x = 0
        total_y = 0
        num_points = 0

        for cnt in contours:
            # Calculate the centroid of the contour
            M = cv2.moments(cnt)

            # Check if the contour has an area
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])

                # Add to total x and y coordinates
                total_x += cX
                total_y += cY
                num_points += 1

        # Check if there are any contours
        if num_points > 0:
            # Calculate average centroid
            avg_cX = total_x / num_points
            avg_cY = total_y / num_points

            # Check if the average centroid is within the center region
            if abs(avg_cX - center_x) <= tolerance_x and abs(avg_cY - center_y) <= tolerance_y:
                return "醒目的中心吸引了我的目光"

    def dominant_color_temperature(self, image, min_percentage=0.9):
        # Convert the image to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Calculate the color histogram
        hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])

        # Normalize the histogram
        cv2.normalize(hist, hist)

        # Get the most dominant hue
        dominant_hue = np.argmax(hist)

        # Calculate the percentage of black and white pixels
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, bw = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        percentage_bw = np.count_nonzero(bw) / (image.shape[0] * image.shape[1])

        # Check the dominant hue and return the corresponding comment
        if percentage_bw < min_percentage:
            if 0 <= dominant_hue <= 30 or 150 < dominant_hue <= 180:
                return "从暖色中感受到了你的活力"
            elif 30 < dominant_hue <= 150:
                return "从冷色中感受到了你的宁静"

    def contains_pink(self, image):
        # Define pink in BGR color space
        pink_bgr = np.array([255, 174, 201])

        # Check if there are any pink pixels in the image
        pink_pixels = np.all(image == pink_bgr, axis=-1)

        if np.any(pink_pixels):
            return "粉色是我最喜欢的颜色"


