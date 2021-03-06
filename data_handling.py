import os
import rasterio
import numpy as np


def read_img(path, read_pre=True, read_post=True, pre_names=None, post_names=None):
    """
    Reading files from a folder in a 3-dimensional numpy array. channels first,
    if both pre- and post- images are read, one 6-layer array is created,
    pre-event image first, post-event image last without georeferencing

    :param path: string, path to the folder with the files, for example './ventura_train/'
    :param read_pre: can be set to False if you do not want to read pre image
    :param read_post: can be set to False if you do not want to read post image
    :param pre_names: filenames for R, G and B channel in pre-image
    :param post_names: filenames for R, G and B channel in post-image
    """
    if not pre_names:
        pre_names = ['pre_r.tif', 'pre_g.tif', 'pre_b.tif']
    if not post_names:
        post_names = ['post_r.tif', 'post_g.tif', 'post_b.tif']
    
    # with rasterio.open(os.path.join(path, 'pre_r.tif')) as src:
    #    size = src.size

    img = None
    if read_pre:
        for name_ in pre_names:
            with rasterio.open(os.path.join(path, name_)) as src:
                channel = src.read()
            if img is None:
                img = channel.copy()
            else:
                img = np.concatenate((img, channel.copy()), axis=0)
                
    if read_post:
        for name_ in post_names:
            with rasterio.open(os.path.join(path, name_)) as src:
                channel = src.read()
            if img is None:
                img = channel.copy()
            else:
                img = np.concatenate((img, channel.copy()), axis=0)
    return img


def read_mask(path, cls='all'):
    """
    Reading mask for a class in a 2-dimensional numpy array without georeference

    :param path: string, path to the folder with the files, for example './ventura_train/'
    :param cls: string, one of the classes present in the dataset (all, burned, non_burned).
    """
    if cls not in ['all', 'burned', 'non_burned']:
        raise ValueError('classes are: all, burned, non-burned')
    name = os.path.join(path, cls + '.tif')
    with rasterio.open(name) as src:
        mask = src.read(1)
    return mask


def save_img(img, name):
    """
    Saves the image to the file

    :param img:  2- or 3- dimensional numpy array, if 3-dimensional then channels first
        if the array is 3-dimensional, the image saved is multi-channel with any given number of
        channels (layers) (can save RGB) georeferencing is not supported
    :param name: full path with name. Extension is not needed, anyway the file will be a .tif
    """
    if img.ndim == 2:
        layers = 1
        w = img.shape[1]
        h = img.shape[0]
    elif img.ndim == 3:
        layers = img.shape[0]
        w = img.shape[2]
        h = img.shape[1]
    else:
        raise ValueError('img must be 2- or 3-dimensional array')
    if name[-4:] != '.tif' and name[-5:] != '.tiff':
        name_ = name + '.tif'
    else:
        name_ = name
    with rasterio.Env():
        with rasterio.open(name_, 'w', 
                           width=w, height=h,
                           driver='GTiff', count=layers, 
                           dtype=str(img.dtype)) as dst:
            if img.ndim == 2:
                dst.write(img, 1)
            else:
                dst.write(img)
