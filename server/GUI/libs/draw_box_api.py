import os
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def draw_chinese_box(im, font, box, label="", color=(128, 128, 128)):
    im = Image.fromarray(im)
    lw = max(round(sum(im.size) / 2 * 0.003), 2)
    draw = ImageDraw.Draw(im)
    size = max(round(sum(im.size) / 2 * 0.035), 12)
    font = ImageFont.truetype(str(font), size)
    p1 = (box[0], box[1])
    draw.rectangle(box, width=lw, outline=color)  # box
    if label:
            w, h = font.getbbox(label)[2:] # text width, height
            outside = p1[1] - h >= 0  # label fits outside box
            draw.rectangle(
                (p1[0], p1[1] - h if outside else p1[1], p1[0] + w + 1, p1[1] + 1 if outside else p1[1] + h + 1),
                fill=color,
            )
            # self.draw.text((box[0], box[1]), label, fill=txt_color, font=self.font, anchor='ls')  # for PIL>8.0
            draw.text((p1[0], p1[1] - h if outside else p1[1]), label, fill=(128,128,128), font=font)
    im = np.asarray(im)
    return im
