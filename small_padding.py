# coding: utf-8
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

width = 2200            # you can customize this
margin_ratio = 0.1      # you can customize this

for i, fn in enumerate(fns):
    img = mpimg.imread(fn)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    print('Processing: ', fn, ', Original size: ',img.shape)
    
    factor = max(img.shape)/(width/(1+margin_ratio))
    img = cv2.resize(img, (int(img.shape[1]/factor), int(img.shape[0]/factor)), interpolation = cv2.INTER_AREA)
    result = np.full((width, width, 3), 255, np.uint8)
    x_offset = int((width - img.shape[1])/2)
    y_offset = int((width - img.shape[0])/2)
    result[y_offset:y_offset+img.shape[0], x_offset:x_offset+img.shape[1]] = img

    save_name = os.path.join(save_dir, f'{i}.jpg')
    cv2.imwrite(save_name, result, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
