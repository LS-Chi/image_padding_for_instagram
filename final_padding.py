# coding: utf-8
from PIL import Image
import math
import matplotlib.image as mpimg
import numpy as np
import glob
import cv2
import os

WIDTH = 2100            # the width of the output frame
assert WIDTH%3==0, "WIDTH must be divisible by 3"
HEIGHT = WIDTH//3*4     # to maximize the frame, we set 3:4 as the ratio
MARGIN_RATIO = 0.00     # you can customize the border percentage
BORDER_COLOR = 255      # grey scale color of padding
IMAGE_QUALITY = 60      # save image quality, 0-100

def retrieve_color(img):
    '''
    Compensate the problem of color saturation loss due to imread
    '''
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    saturation_channel = hsv[:,:,1].astype(np.float32)*1.25
    saturation_channel[np.where(saturation_channel>255)]=255
    saturation_channel = saturation_channel.astype(np.uint8)
    hsv[:,:,1] = saturation_channel
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    return img

def correct_white_balance(img):
    '''
    Deprecated, performance not good
    '''
    brightness = img.astype(np.float32)*1.10
    brightness[np.where(brightness>255)]=255
    brightness = brightness.astype(np.uint8)
    img = brightness

    blue_channel = img[:,:,0].astype(np.float32)*0.98
    blue_channel[np.where(blue_channel>255)]=255
    blue_channel = blue_channel.astype(np.uint8)
    img[:,:,0] = blue_channel

    return img

def main():
    file_dir = './'
    save_dir = os.path.join(file_dir, 'instagram_version') 
    if not os.path.isdir(save_dir):        # if save folder not exist
        os.mkdir(save_dir)

    full_path = os.path.join(file_dir, '*.jpg')
    fns = glob.glob(full_path)

    for i, fn in enumerate(fns):
        # read in image using PIL to get EXIF data
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
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        img = retrieve_color(img)

        multi_frame_flag = fn.startswith('.\-')

        print('Processing: ', fn, ', Original size: ',img.shape)
       
        # if landscape, use WIDTH to fit WIDTH
        if img.shape[0]<img.shape[1]:
            factor = img.shape[1]/(WIDTH/(1+MARGIN_RATIO))
        # if portrait or square, use HEIGHT to fit HEIGHT
        else:
            factor = img.shape[0]/(HEIGHT/(1+MARGIN_RATIO))
        
        img = cv2.resize(img, (int(img.shape[1]/factor), int(img.shape[0]/factor)), interpolation = cv2.INTER_AREA)
        
        result = np.full((HEIGHT, WIDTH, 3), BORDER_COLOR, np.uint8)
        x_offset = int((WIDTH - img.shape[1])/2)
        y_offset = int((HEIGHT - img.shape[0])/2)
        result[y_offset:y_offset+img.shape[0], x_offset:x_offset+img.shape[1]] = img

        save_name = os.path.join(save_dir, f'{i}.jpg')
        cv2.imwrite(save_name, result, [int(cv2.IMWRITE_JPEG_QUALITY), IMAGE_QUALITY])
        
        # slice the image and save multiple frame
        if multi_frame_flag:
            img = np.array(pil_img)      
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            img = retrieve_color(img)    
            factor = img.shape[0]/(HEIGHT/(1+MARGIN_RATIO))
            img = cv2.resize(img, (int(img.shape[1]/factor), int(img.shape[0]/factor)), interpolation = cv2.INTER_AREA)
        
            result = []
            img_h = img.shape[0]    #
            img_w = img.shape[1]    #
            
            frame_h = HEIGHT
            frame_w = int((frame_h/4)*3)

            frame_count = math.ceil(((img_w-frame_w)/2)/frame_w)*2 + 1
            img_padding = np.full((frame_h, frame_count*frame_w, 3), BORDER_COLOR, np.uint8)

            pad_width = frame_w * frame_count
            x_offset = int((pad_width - img_w)/2)
            y_offset = int((frame_h - img_h)/2)

            img_padding[y_offset:y_offset+img_h, x_offset:x_offset+img_w] = img

            for j in range(frame_count):
                save_name = os.path.join(save_dir, f'{i}_{j}.jpg')
                cv2.imwrite(save_name, img_padding[:, j*frame_w:(j+1)*frame_w], [int(cv2.IMWRITE_JPEG_QUALITY), IMAGE_QUALITY])

if __name__=="__main__":
    main()