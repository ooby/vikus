from typing import List


class StudyList(List):
    def __init__(self, *args, **kwargs):
        super(StudyList, self).__init__(*args, **kwargs)
        self.__rgb_pixels_list = []

    @property
    def rgb_pixels_list(self):
        return self.__rgb_pixels_list

    def append_study(self, study):
        self.append(study)
        self.__rgb_pixels_list.append(study.rgb_pixels)
