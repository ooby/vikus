from .import_files import get_pixels
from .utils import get_level_window, windowed_rgb, Worker


class Study():
    def __init__(self, study_data, pool):
        self.__pool = pool
        self.__study_data = study_data
        self.__current_series_index = 0
        self.__current_series = self.__study_data[self.__current_series_index]
        self.__pixels = get_pixels(self.__current_series)
        self.__level, self.__window = get_level_window(
            self.__current_series[0])
        self.__calc_rgb()

    def __worker_wrapper(self):
        return windowed_rgb(self.__pixels, self.__level, self.__window)

    def __process_result(self, res):
        self.__rgb = res

    def __process_complete(self):
        pass

    def __calc_rgb(self):
        worker = Worker(self.__worker_wrapper)
        worker.signals.result.connect(self.__process_result)
        worker.signals.finished.connect(self.__process_complete)
        self.__pool.start(worker)

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
        self.__calc_rgb()

    @property
    def current_series(self):
        return self.__current_series

    @property
    def rgb_pixels(self):
        return self.__rgb
