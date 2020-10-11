import numpy as np
import glob
import os
import shutil
from PIL import Image
import math

#正方形にする関数
def expand2square(pil_img, background_color):
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result
    
#拡張色指定
def GetPixel(img):
    imgBox = img.crop((0,0,30,30)) 
    pixelSizeTuple = imgBox.size
    rlist = []
    glist = []
    blist = []

    for i in range(pixelSizeTuple[0]):
        for j in range(pixelSizeTuple[1]):
            r,g,b = img.getpixel((i,j))
            rlist.append(r)
            glist.append(g)
            blist.append(b)
    r=sum(rlist)/len(rlist)
    g=sum(glist)/len(glist)
    b=sum(blist)/len(blist)
    r = math.floor(r)
    g = math.floor(g)
    b = math.floor(b)
    
    return r,g,b

#正方形に拡張(事前にpillowで画像をopen)
def Square_main(im):
    if np.array(im).ndim==3:
        im_new = expand2square(im, GetPixel(im))
    else:
        im=im.convert("L").convert("RGB")
        im_new = expand2square(im, GetPixel(im))
    return im_new


def Select_image(crop_images):
    #抽出画像の中で最も大きいものを選択
    if len(crop_images) >= 2:
        big_img = crop_images[0]
        for i in range(len(crop_images)-1):
            if np.array(big_img).shape[0] <= np.array(crop_images[i+1]).shape[0]:
                big_img = crop_images[i+1]
    else:
        big_img = crop_images[0]
    return big_img
