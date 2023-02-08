# coding: utf-8
from PIL import Image
import matplotlib.image as mpimg
import numpy as np
import glob
import cv2
import os

file_dir = './'
save_dir = os.path.join(file_dir, 'instagram_version') 
if not os.path.isdir(save_dir):        # if save folder not exist
    os.mkdir(save_dir)

full_path = os.path.join(file_dir, '*.jpg')
fns = glob.glob(full_path)

width = 2100            # you can customize this
height = 2800
margin_ratio = 0.00     # you can customize this
border_color = 255       # you can customize this

for i, fn in enumerate(fns):
    pil_img = Image.open(fn)
    img_exif = pil_img.getexif()
    if len(img_exif):
        if img_exif[274] == 3:
            pil_img = pil_img.transpose(Image.ROTATE_180)
        elif img_exif[274] == 6:
            pil_img = pil_img.transpose(Image.ROTATE_270)
        elif img_exif[274] == 8:
            pil_img = pil_img.transpose(Image.ROTATE_90)
    
    img = np.array(pil_img)      
    # img = mpimg.imread(fn)

    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    # brightness = img.astype(np.float32)*1.10
    # brightness[np.where(brightness>255)]=255
    # brightness = brightness.astype(np.uint8)
    # img = brightness

    # blue_channel = img[:,:,0].astype(np.float32)*0.98
    # blue_channel[np.where(blue_channel>255)]=255
    # blue_channel = blue_channel.astype(np.uint8)
    # img[:,:,0] = blue_channel

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    saturation_channel = hsv[:,:,1].astype(np.float32)*1.25
    saturation_channel[np.where(saturation_channel>255)]=255
    saturation_channel = saturation_channel.astype(np.uint8)
    hsv[:,:,1] = saturation_channel
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    print('Processing: ', fn, ', Original size: ',img.shape)
    
    # factor = max(img.shape)/(width/(1+margin_ratio))
    # if landscape, use width to fit width
    if img.shape[0]<img.shape[1]:
        factor = img.shape[1]/(width/(1+margin_ratio))
    # if portrait, use height to fit height
    else:
        factor = img.shape[0]/(height/(1+margin_ratio))
    img = cv2.resize(img, (int(img.shape[1]/factor), int(img.shape[0]/factor)), interpolation = cv2.INTER_AREA)
    result = np.full((height, width, 3), border_color, np.uint8)
    x_offset = int((width - img.shape[1])/2)
    y_offset = int((height - img.shape[0])/2)
    result[y_offset:y_offset+img.shape[0], x_offset:x_offset+img.shape[1]] = img

    save_name = os.path.join(save_dir, f'{i}.jpg')
    cv2.imwrite(save_name, result, [int(cv2.IMWRITE_JPEG_QUALITY), 60])