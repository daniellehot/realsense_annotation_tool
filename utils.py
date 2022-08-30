import cv2
import numpy as np

stop_flag = False

def show_mode_window(mode):
    mode_window = np.zeros((100,300,3), np.uint8)
    cv2.namedWindow("mode")
    cv2.moveWindow("mode", 1600, 150)  # Move it to (40,30)
    cv2.putText(mode_window, mode, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA, False)
    cv2.imshow("mode", mode_window)

def kill_mode_window():
    cv2.destroyAllWindows()