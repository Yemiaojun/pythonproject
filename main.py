import cv2
img_path = "34.png"
img = cv2.imread(img_path)
cv2.imshow("img", img)
cv2.waitKey(0)
cv2.destroyAllWindows()