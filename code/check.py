import cv2 
import numpy as np
import pandas as pd

img = cv2.imread("data/new/00009.png")
scaled_img = cv2.resize(img, (1280, 720))
#arr = np.genfromtxt("data/new/00009.csv", delimiter= ",")
df = pd.read_csv("data/new/00009.csv")
print(df)

SCALE_WIDTH = 1920/1280
SCALE_HEIGHT = 1080/720


for index, row in df.iterrows():
    #print(row['species'],  row['id'], row['x'], row['y'])
    coordinates = (row['x'], row['y'])
    colour = (0, 0, 255)
    scaled_coordinates = ( int(row['x']/SCALE_WIDTH), int(row['y']/SCALE_HEIGHT))
    annotation = row['species']+ str(row['id'])

    img = cv2.circle(img, coordinates, 5, colour, -1)
    img = cv2.putText(img, annotation, (coordinates[0]+5, coordinates[1]+5), cv2.FONT_HERSHEY_SIMPLEX, 1, colour, 2, cv2.LINE_AA, False)

    scaled_img = cv2.circle(scaled_img, scaled_coordinates, 5, colour, -1)
    scaled_img = cv2.putText(scaled_img, annotation, (scaled_coordinates[0]+5, scaled_coordinates[1]+5), cv2.FONT_HERSHEY_SIMPLEX, 1, colour, 2, cv2.LINE_AA, False)

cv2.imshow("1920x1080", img)
cv2.imshow("1280X720", scaled_img)
cv2.waitKey(0)
