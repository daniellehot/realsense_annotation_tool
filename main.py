from distutils.command import clean
import os
import time
import cv2
import random as rnd
import tkinter as tk
from tkinter import simpledialog, messagebox
import csv 
from pymsgbox import *


## SOURCES (some of them) 
# https://stackoverflow.com/questions/49799057/how-to-draw-a-point-in-an-image-using-given-co-ordinate-with-python-opencv
# https://chercher.tech/opencv/drawing-mouse-images-opencv
# https://mlhive.com/2022/04/draw-on-images-using-mouse-in-opencv-python

# GLOBAL VARIABLES
rgb, coordinates, fish = [],[],[]
header = ['species', 'x', 'y', 'r', 'g', 'b']
options = ["cod", "haddock", "pollock", "whitting", "cancel"] 
img = None

def scan_for_new_files(path):
    files = []
    while 1:
        files = os.listdir(path)
        if len(files) != 0:
            break
        else:
            print("No new image")
            time.sleep(1.0)
    image_path = os.path.join(path, files[0])
    return image_path, files[0]


def get_species():
    root = tk.Tk()
    root.withdraw()    
    species = None
    while species not in options:
        species = simpledialog.askstring(title="Annotate fish species", prompt="Fish species: ")
        if species == None:
            species = "cancel"
    return species


def draw_point(event, x, y, flags, param):
    global img
    if event == cv2.EVENT_LBUTTONDOWN:
        coordinate = (x,y)
        colour = (rnd.randint(0,255), rnd.randint(0,255), rnd.randint(0,255))
        species = get_species()
        if species != "cancel":
            img = cv2.circle(img, coordinate, 5, colour, -1)
            img = cv2.putText(img, species, (coordinate[0]+5, coordinate[1]+5), cv2.FONT_HERSHEY_SIMPLEX, 1, colour, 2, cv2.LINE_AA, False)
            rgb.append(colour)
            coordinates.append(coordinate)
            fish.append(species)


def remove_point(event, x, y, flags, param):    
    global img
    if event == cv2.EVENT_LBUTTONDOWN:
        for coordinate in coordinates:
            sum = abs(x-coordinate[0] + y-coordinate[1])
            if sum < 10:
                idx = coordinates.index(coordinate)
                cv2.drawMarker(img, coordinates[idx], rgb[idx], cv2.MARKER_TILTED_CROSS, 50, 2)
                coordinates.pop(idx)
                fish.pop(idx)
                rgb.pop(idx)
                break


def annotate(img_path, mode):
    global img
    img = cv2.imread(img_path)
    annotated_img = cv2.imread(img_path)
    
    cv2.namedWindow("annotation window")
    cv2.setMouseCallback("annotation window", draw_point)
    
    while 1:     
        cv2.imshow("annotation window", img)
        k = cv2.waitKey(20) & 0xFF
        if k == 27:
            break
        if k == ord('m'):
            if mode == "annotating":
                mode = "correcting"
                print(mode)
                cv2.setMouseCallback("annotation window", remove_point)
            else:
                mode = "annotating"
                print(mode)
                cv2.setMouseCallback("annotation window", draw_point)
    
    cv2.destroyAllWindows()
    return annotated_img
    

def confirm_annotation(img):
    for (colour, coordinate, species) in zip(rgb, coordinates, fish):
        img = cv2.circle(img, coordinate, 5, colour, -1)
        img = cv2.putText(img, species, (coordinate[0]+5, coordinate[1]+5), cv2.FONT_HERSHEY_SIMPLEX, 1, colour, 2, cv2.LINE_AA, False)
    cv2.namedWindow("confirmation window")

    while 1:
        cv2.imshow("confirmation window", img)
        cv2.waitKey()
        #correct = input("Is this correct? Y/N \n")
        correct = messagebox.askyesno(" ", "Is this correct annotation?")
        if correct == True:
            cv2.destroyAllWindows()
            return True
        elif correct == False:
            cv2.destroyAllWindows()
            return False

def re_annotate(clean_img, mode):
    global img
    img = clean_img
    for (colour, coordinate, species) in zip(rgb, coordinates, fish):
        cv2.circle(img, coordinate, 5, colour, -1)
        cv2.putText(img, species, (coordinate[0]+5, coordinate[1]+5), cv2.FONT_HERSHEY_SIMPLEX, 1, colour, 2, cv2.LINE_AA, False)
    
    cv2.namedWindow("annotation window")
    cv2.setMouseCallback("annotation window", draw_point)
    
    while 1:     
        cv2.imshow("annotation window", img)
        k = cv2.waitKey(20) & 0xFF
        if k == 27:
            break
        if k == ord('m'):
            if mode == "annotating":
                mode = "correcting"
                print(mode)
                cv2.setMouseCallback("annotation window", remove_point)
            else:
                mode = "annotating"
                print(mode)
                cv2.setMouseCallback("annotation window", draw_point)
    
    cv2.destroyAllWindows()
    return annotated_img


def save_annotations(path, data):
    path = path + ".csv"
    if os.path.exists(path):
        os.remove(path)
    with open(path, 'a') as f: 
        writer = csv.writer(f) 
        writer.writerow(header)
        for annotation in data:
            writer.writerow(annotation) 


def reset():
    rgb.clear()
    coordinates.clear()
    fish.clear()
    global img
    img = None


if __name__=="__main__":
    image_folder = "image_folder"
    image_output_folder = "dataset_folder/img"
    annotation_output_folder = "dataset_folder/gt"

    while 1:
        mode = "annotating"

        img_path, img_file = scan_for_new_files(image_folder)
        img_output_path = os.path.join(image_output_folder, img_file)
        annotation_file = os.path.join(annotation_output_folder, img_file[:-4])
        
        annotated_img = annotate(img_path, mode)

        if confirm_annotation(annotated_img):
            os.rename(img_path, img_output_path)
            data_formated = []
            for (species, xy, colour) in zip(fish, coordinates, rgb):
                data_formated.append([species, xy[0],xy[1],colour[0],colour[1],colour[2]])
            save_annotations(annotation_file, data_formated)
            reset()
        else:
            reset()

