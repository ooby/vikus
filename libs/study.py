from .import_files import get_pixels
from .utils import get_level_window, windowed_rgb, Worker


class Study():
    def __init__(self, study_data):
        for series in study_data:
            if len(series) > 1:
                if hasattr(series[0], "ImagePositionPatient"):
                    series.sort(key=lambda x: float(
                        x.ImagePositionPatient[2]), reverse=True)
        self.__study_data = study_data
        self.__current_series_index = 0
        self.__current_series = self.__study_data[self.__current_series_index]
        self.__pixels = get_pixels(self.__current_series)
        self.__level, self.__window = get_level_window(
            self.__current_series[0])
        self.__rgb = windowed_rgb(self.__pixels, self.__level, self.__window)

    @property
    def current_series_index(self):
        return self.__current_series_index

    @current_series_index.setter
    def current_series_index(self, index):
        self.__current_series_index = int(index)
        self.__current_series = self.__study_data[self.__current_series_index]
        self.__pixels = get_pixels(self.__current_series)
        self.__level, self.__window = get_level_window(
            self.__current_series[0])
        self.__rgb = windowed_rgb(self.__pixels, self.__level, self.__window)

    @property
    def study_data(self):
        return self.__study_data

    @property
    def current_series(self):
        return self.__current_series

    @property
    def rgb_pixels(self):
        return self.__rgb

    @property
    def pixels(self):
        return self.__pixels

    @property
    def level_window(self):
        return self.__level, self.__window
