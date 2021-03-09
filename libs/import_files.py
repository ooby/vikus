from itertools import groupby
import numpy as np
import os
import pydicom
from pydicom.pixel_data_handlers import gdcm_handler, pillow_handler
from typing import List


def series_projection(val):
    '''Projection by SeriesDescription'''
    return val.SeriesDescription


def study_projection(val):
    '''Projection by StudyDescription'''
    return val.StudyDescription


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


def get_studies(dicom_files: List[str]) -> List:
    """
    Read DICOM-files, group by StudyDescription and SeriesDescription
    Returns nested Lists: List of Sudies with List of Series with List of Instances
    """
    dicom_datas = [
        pydicom.read_file(file, force=True)
        for file in dicom_files
    ]
    for dicom_data in dicom_datas:
        if not 'StudyDescription' in dicom_data:
            dicom_data.StudyDescription = "default"
        if not 'SeriesDescription' in dicom_data:
            dicom_data.SeriesDescription = "default"
    studies = []
    for item in [list(it) for k, it in groupby(dicom_datas, study_projection)]:
        groupped_by_series = [list(it)
                              for k, it in groupby(item, series_projection)]
        studies.append(groupped_by_series)
    return studies


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
            image[slice_number] = slope * image[slice_number].astype(np.float64)
            image[slice_number] = image[slice_number].astype(np.int16)
        image[slice_number] += np.int16(intercept)
    return np.array(image, dtype=np.int16)