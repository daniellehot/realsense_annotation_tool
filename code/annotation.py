import os
import time
import cv2
#import random as rnd
import tkinter as tk
from tkinter import simpledialog, messagebox
import csv 
from pymsgbox import *


## SOURCES (some of them) 
# https://stackoverflow.com/questions/49799057/how-to-draw-a-point-in-an-image-using-given-co-ordinate-with-python-opencv
# https://chercher.tech/opencv/drawing-mouse-images-opencv
# https://mlhive.com/2022/04/draw-on-images-using-mouse-in-opencv-python

# GLOBAL VARIABLES
FOLDER_PATH = "data/new/"
#FILE = None

rgb, coordinates, fish, IDs = [], [], [], []
#header = ['species', 'id', 'x', 'y', 'r', 'g', 'b']
header = ['species', 'id', 'x', 'y']
options = ["cod", "haddock", "pollock", "whitting", "cancel"] 
img = None


def scan_for_new_files(path):
    for filename in os.listdir(path):
        if filename.endswith(".png"):
            return filename.replace(".png", "")
            

def get_species():
    root = tk.Tk()
    root.withdraw()    
    species = None
    while species not in options:
        species = simpledialog.askstring(title = "Annotate fish species", prompt="Fish species: ")
        if species == None:
            species = "cancel"
    if species != "cancel":
        id = simpledialog.askstring(title = "Annotate fish ID", prompt="ID: ")
    return species, id


def draw_point(event, x, y, flags, param):
    global img
    if event == cv2.EVENT_LBUTTONDOWN:
        coordinate = (x,y)
        #colour = (rnd.randint(0,255), rnd.randint(0,255), rnd.randint(0,255))
        colour = (0, 0, 255)
        species, id = get_species()
        annotation = id + species
        if species != "cancel":
            img = cv2.circle(img, coordinate, 5, colour, -1)
            img = cv2.putText(img, annotation, (coordinate[0]+5, coordinate[1]+5), cv2.FONT_HERSHEY_SIMPLEX, 1, colour, 2, cv2.LINE_AA, False)
            rgb.append(colour)
            coordinates.append(coordinate)
            fish.append(species)
            IDs.append(id)


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
                IDs.pop(idx)
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
        if k == 27: #ESC
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
    for (colour, coordinate, species, id) in zip(rgb, coordinates, fish, IDs):
        img = cv2.circle(img, coordinate, 5, colour, -1)
        annotation = id + species
        img = cv2.putText(img, annotation, (coordinate[0]+5, coordinate[1]+5), cv2.FONT_HERSHEY_SIMPLEX, 1, colour, 2, cv2.LINE_AA, False)
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

"""
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
"""

def save_annotations(path, data):
    #path = path + ".csv"
    #if os.path.exists(path):
    #    os.remove(path)
    with open(path, 'a') as f: 
        writer = csv.writer(f) 
        writer.writerow(header)
        for annotation in data:
            writer.writerow(annotation) 


def reset():
    rgb.clear()
    coordinates.clear()
    fish.clear()
    IDs.clear()
    global img
    img = None


if __name__=="__main__":
    previous_file = None
    while 1:
        file = scan_for_new_files(FOLDER_PATH)
        if file != None and previous_file != file:
            #img_output_path = os.path.join(image_output_folder, img_file)
            #annotation_file = os.path.join(annotation_output_folder, img_file[:-4])
            annotation_file = FOLDER_PATH + file + ".csv"
            img_path = FOLDER_PATH + file + ".png"
            mode = "annotating"
            print("temp 2")
            annotated_img = annotate(img_path, mode)

            if confirm_annotation(annotated_img):
                data_formated = []
                for (species, id, xy) in zip(fish, IDs, coordinates):
                    data_formated.append([species, id, xy[0],xy[1]])
                save_annotations(annotation_file, data_formated)
                previous_file = file
                reset()
            else:
                reset()
        else:
            time.sleep(2)
            continue

