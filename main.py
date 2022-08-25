import os
import time
import cv2
import random as rnd
import tkinter as tk
from tkinter import simpledialog, messagebox
import csv 

rgb, coordinates, fish = [],[],[]
header = ['rgb', 'coordinates (xy)', 'species']
options = ["cod", "haddock", "pollock", "whitting"]
# https://stackoverflow.com/questions/49799057/how-to-draw-a-point-in-an-image-using-given-co-ordinate-with-python-opencv
# https://chercher.tech/opencv/drawing-mouse-images-opencv
# https://mlhive.com/2022/04/draw-on-images-using-mouse-in-opencv-python

def scan_for_new_files(path):
    files = []
    while 1:
        files = os.listdir(path)
        #print(files)
        if len(files) != 0:
            break
        else:
            print("No new image")
            time.sleep(1.0)
    image_path = os.path.join(path, files[0])
    return image_path, files[0]

""""
def get_species_v2():
    root = tk.Tk()
    root.geometry("500x250")
    menu= tk.StringVar()
    menu.set("Select Fish Species")
    drop= tk.OptionMenu(root, menu,"cod", "haddock", "pollock", "whitting")
    drop.pack()
    root.update_idletasks()
    root.update()
    species = "temp"
    return species
"""

def get_species():
    root = tk.Tk()
    root.withdraw()    
    # the input dialog
    species = None
    while species not in options:
        species = simpledialog.askstring(title="Annotate fish species", prompt="Fish species: ")
    return species

def draw_point(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        coordinate = (x,y)
        colour = (rnd.randint(0,255), rnd.randint(0,255), rnd.randint(0,255))
        cv2.circle(img, coordinate, 10, colour, -1)
        rgb.append(colour)
        coordinates.append(coordinate)
        fish.append(get_species())

def confirm(img):
    for (colour, coordinate, species) in zip(rgb, coordinates, fish):
        img = cv2.putText(img, species, coordinate, cv2.FONT_HERSHEY_SIMPLEX, 1, colour, 2, cv2.LINE_AA, False)
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
        if correct == 'Y' or correct == 'y':
            cv2.destroyAllWindows()
            return True
        elif correct == 'N' or correct == 'n':
            cv2.destroyAllWindows()
            return False
        else:
            continue
        """

def save_annotations(path):
    with open('student.csv', 'w') as f: 
        write = csv.writer(f) 
        write.writerow(Details) 
        write.writerows(rows) 


if __name__=="__main__":
    image_folder = "/home/daniel/annotation_tool/image_folder"
    image_output_folder = "/home/daniel/annotation_tool/dataset_folder/img"
    annotation_output_folder = "/home/daniel/annotation_tool/dataset_folder/gt"

    while 1:
        img_path, img_file = scan_for_new_files(image_folder)
        img_output_path = os.path.join(image_output_folder, img_file)

        img = cv2.imread(img_path)
        annotated_img = cv2.imread(img_path)
        
        cv2.namedWindow("annotation window")
        cv2.setMouseCallback("annotation window", draw_point)

        while 1:
            cv2.imshow("annotation window", img)
            if cv2.waitKey(20) & 0xFF == 27:
                break
        cv2.destroyAllWindows()


        correct = confirm(annotated_img)
        if correct == True:
            #os.rename(img_path, img_output_path)
            save_annotations()
            exit(8)
            continue
        else:
            #RESET ANNOTATION 
            rgb.clear()
            coordinates.clear()
            fish.clear()
            continue
            #exit(5)


    
    
    
