from datetime import datetime
import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QRunnable
import traceback, sys


def get_level_window(series_item):
    if hasattr(series_item, 'WindowCenter') and hasattr(series_item, 'WindowWidth'):
        try:
            level = np.array(
                list(series_item.WindowCenter), dtype=np.int16)
            window = np.array(
                list(series_item.WindowWidth), dtype=np.int16)
            level = level[0]
            window = window[0]
        except TypeError:
            level = int(series_item.WindowCenter)
            window = int(series_item.WindowWidth)
    else:
        level = -5000
        window = 0
    return level, window


def get_rgb_pixels(pixels: np.ndarray, min_hu: int, max_hu: int) -> np.ndarray:
    pixels = np.where(pixels < min_hu, min_hu, pixels)
    pixels = np.where(pixels > max_hu, max_hu, pixels)
    abs_delta = abs(max_hu - min_hu)
    if abs_delta == 0:
        abs_delta = 1
    pixels_value = (abs(pixels - min_hu) / abs_delta) * 255
    rgb_pixels = np.zeros((*pixels.shape, 3), dtype=np.uint8)
    rgb_pixels[..., 0] = pixels_value.astype(np.uint8)
    rgb_pixels[..., 1] = pixels_value.astype(np.uint8)
    rgb_pixels[..., 2] = pixels_value.astype(np.uint8)
    return rgb_pixels


def windowed_rgb(pixels: np.ndarray, level: int = -5000, window: int = 0) -> np.ndarray:
    if level == -5000 and window == 0:
        min_hu = np.min(pixels)
        max_hu = np.max(pixels)
    else:
        min_hu = level - (window // 2)
        max_hu = level + (window // 2)
    return get_rgb_pixels(pixels, min_hu, max_hu)


def get_studies_metadata(studies):
    results = []
    for study in studies:
        study_description = ""
        patient_name = ""
        patient_id = ""
        modality = ""
        study_id = ""
        study_date = ""
        study_time = ""
        for series in study:
            for instance in series:
                study_description = instance.StudyDescription
                patient_name = instance.PatientName
                patient_id = instance.PatientID
                modality = instance.Modality
                study_id = instance.StudyID
                study_date = instance.StudyDate
                study_time = instance.StudyTime
        results.append({
            "study_description": str(study_description),
            "patient_name": str(patient_name),
            "patient_id": str(patient_id),
            "modality": str(modality),
            "study_id": str(study_id),
            "study_date": f"{datetime.strptime(study_date, '%Y%m%d'):%d-%m-%Y}",
            "study_time": f"{datetime.strptime(study_time, '%H%M%S.%f'):%H:%M:%S}"
        })
    return results


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()
