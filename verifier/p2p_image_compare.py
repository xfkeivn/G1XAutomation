import numpy as np
from PIL import Image
from utils.singleton import Singleton


class P2PImageCompare(metaclass=Singleton):

    def compare(self,capture_image_path,sample_image_path,rect):
        # Load the images
        img1 = Image.open(capture_image_path)
        img2 = Image.open(sample_image_path)
        # Define the rectangular region of interest
        x, y, width, height = rect
        # Convert the images to NumPy arrays
        arr1 = np.array(img1)
        arr2 = np.array(img2)
        # Slice the arrays to extract the region of interest
        cropped_arr1 = arr1[y:y+height, x:x+width]
        cropped_arr2 = arr2[y:y+height, x:x+width]
        # Compare the arrays
        if np.array_equal(cropped_arr1, cropped_arr2):
            return True
        else:
            return False
