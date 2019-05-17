import numpy as np
import matplotlib.pyplot as plt
import os
import cv2
from valload import get_annotations_map as get

d = './train'
TDATADIR=[os.path.join(d, o) for o in os.listdir(d) 
                    if os.path.isdir(os.path.join(d,o))]

CATAGORIES=os.listdir(d)

d2 = './val'
VDATADIR=[os.path.join(d2, q) for q in os.listdir(d2)
                    if os.path.isdir(os.path.join(d2, q))]

#
