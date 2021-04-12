from typing import List

class StudyList(List):
    def __init__(self, studies, *args, **kwargs):
        super(StudyList, self).__init__(*args, **kwargs)
        self.__studies = []
        self.__rgb_pixels_list = []
        for study in studies:
            self.__studies.append(study)
            self.__rgb_pixels_list.append(study.rgb_pixels)
    
    @property
    def rgb_pixels_list(self):
        return self.__rgb_pixels_list