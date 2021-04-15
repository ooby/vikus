from itertools import groupby
import numpy as np
import os
import pydicom
from pydicom.pixel_data_handlers import gdcm_handler, pillow_handler
from typing import List


def series_projection(val):
    '''Projection by SeriesDescription'''
    return val.SeriesInstanceUID


def study_projection(val):
    '''Projection by StudyDescription'''
    return val.StudyInstanceUID


def is_dicom(path: str) -> bool:
    """Check file whether DICOM-file or not"""
    if not os.path.isfile(path):
        return False
    try:
        with open(path, 'rb') as file_name:
            return file_name.read(132).decode('ASCII')[-4:] == 'DICM'
    except UnicodeDecodeError:
        return False


def read_filenames(path: str) -> List:
    """Read files from directory, is DICOM-file check, get filenames with paths"""
    return [
        os.path.join(root, file)
        for root, _, files in os.walk(os.path.abspath(path))
        for file in files
        if is_dicom(os.path.join(root, file))
    ]


def get_study(study_filename: str):
    data = pydicom.read_file(study_filename, force=True)
    if not hasattr(data, "StudyDescription"):
        data.StudyDescription = "default"
    if not hasattr(data, "SeriesDescription"):
        data.SeriesDescription = "default"
    return data


def get_pixels(slices: np.ndarray) -> np.ndarray:
    '''Get pixel data from DICOM-file Dataset'''
    try:
        image = np.stack([s.pixel_array for s in slices])
    except RuntimeError:
        for slice_item in slices:
            slice_item.pixel_data_handlers = [gdcm_handler, pillow_handler]
        image = np.stack([s.pixel_array for s in slices])
    image = image.astype(np.int16)
    image[image == -2000] = 0
    for slice_number, _ in enumerate(slices):
        intercept = slices[slice_number].RescaleIntercept
        slope = slices[slice_number].RescaleSlope
        if slope != 1:
            image[slice_number] = slope * \
                image[slice_number].astype(np.float64)
            image[slice_number] = image[slice_number].astype(np.int16)
        image[slice_number] += np.int16(intercept)
    return np.array(image, dtype=np.int16)
