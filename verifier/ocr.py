"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: GX1
@file: BackPlaneSimulator.py
@time: 2023/4/20 15:02
@desc:
"""
from utils.singleton import Singleton
from PIL import Image
import pytesseract


class TessertOCR(metaclass=Singleton):

    def get_string(self, img_scr, left_top_xy, right_bottom_xy):
        src_image = Image.open(img_scr)
        cropped_image = src_image.crop((left_top_xy[0], left_top_xy[1], right_bottom_xy[0], right_bottom_xy[1]))
        text = pytesseract.image_to_string(cropped_image, lang='eng')
        return text.strip(),cropped_image


if __name__ == "__main__":
    ocr = TessertOCR()
    print( ocr.get_string("../sim_desk/screenshot/20234月04_18_42_06.png",(333,111),(467,149)))
    print(ocr.get_string("../sim_desk/screenshot/20234月04_18_42_06.png", (333, 111), (467, 149)))