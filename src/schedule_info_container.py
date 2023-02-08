# Max Lewis 01/20/23
# CPSC 4176 Project

import pickle

class ScheduleInfoContainer:
    
    # cf = confidence factor
    def __init__(self, schedule, cf):
        self._schedule = schedule
        self._cf = cf

    # This method pickles ScheduleInfoContainer class object so data can be saved
    def pickle(self):
        pickled_data = pickle.dumps(self)
        return pickled_data

    def display_container(self):
        print(self._schedule)
        print(self._cf)

    def display_schedule(self):
        print(self._schedule)

    def display_cf(self):
        print(self._cf)

    def get_container(self):
        return self._schedule, self._cf

    def get_schedule(self):
        return self._schedule

    def get_cf(self):
        return self._cf

    def semester_count(self):
        return len(self._schedule)

    def course_count(self):
        count = 0
        for semester in self._schedule:
            for course in semester:
                count = count + 1
        return count

#lst = [['c'], ['d'], ['p'], [], ['m', 'h', 'e'], ['r', 't', 'f']]
#cf = 0.87

#container = ScheduleInfoContainer(lst, cf)
#pickled_data = container.pickle()
#print(pickled_data)
#reconstucted_data = pickle.loads(pickled_data)
#print(container)
#print(reconstucted_data)
#container.display_container()
#reconstucted_data.display_container()
#print(container.semester_count())
#print(container.course_count())

