import cv2
from deskew import determine_skew

image = cv2.imread('../images/fuji45.png', cv2.IMREAD_GRAYSCALE)
angle = determine_skew(image)
print("Skew angle:", angle)