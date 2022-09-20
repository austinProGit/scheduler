from course_info_container import *
import unittest

class TestContainer(unittest.TestCase):

    container = CourseInfoContainer(load_course_info('ClassInfo.xlsx'))

    courseIDs = ['MATH 1113', 'MATH 2125', 'MATH 5125', 'CPSC 2108', 'CPSC 1301', 'CPSC 1302', 'CPSC 2105', 
            'CYBR 2159', 'CYBR 2106', 'CPSC 3175', 'CPSC 3125', 'CPSC 3131', 'CPSC 5135', 'CPSC 3165', 
            'CPSC 3121', 'CPSC 5155', 'CPSC 5157', 'CPSC 4175', 'CPSC 5115', 'CPSC 5128', 'CPSC 4176', 
            'CPSC 4000', 'CPSC 3111', 'CPSC 3116', 'CPSC 3118', 'CPSC 3156', 'CPSC 3555', 'CPSC 4111', 
            'CPSC 4112', 'CPSC 4113', 'CPSC 4121', 'CPSC 4122', 'CPSC 4130', 'CPSC 4505', 'CPSC 4698', 
            'CPSC 4899', 'CPSC 5125', 'CPSC 5138', 'CPSC 5185', 'CPSC 5555']

    names = ['Pre-Calculus', 'Intro to Discrete Math', 'Discrete Math', 'Data Structures', 'Computer Science 1', 
            'Computer Science 2', 'Computer Organization', 'Fundamentals of Computer Networking', 'Intro to Information Security',
        'Object-Oriented Design', 'Operating Systems', 'Database Systems 1', 'Programming Languages', 
        'Professionalism in Computing', 'Assembly 1', 'Computer Architecture', 'Computer Networks', 
        'Software Engineering', 'Algorithm Analysis and Design', 'Theory of Computation', 'Senior Software Eng. Project', 
        'Baccalaureate Survey', 'COBOL Programming', 'z/OS and JCL', 'Graphical User Interface Development', 
        'Transaction Processing', 'Selected Topics in Computer Science', 'Game Programming 1', 'Game Programming 2', 
        'Game Jam', 'Robotics Programming 1', 'Robotics Programming 2', 'Mobile Computing', 'Undergraduate Research', 
        'Internship', 'Independent Study', 'Computer Graphics', 'Advanced Database Systems', 
        'Artificial Intelligence and Machine Learning', 'Selected Topics in Computer Science']

    availability = [['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su'], 
                ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', '--'], ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', '--'], 
                ['Fa', 'Sp', '--'], ['Fa', 'Sp', '--'], ['--', 'Sp', '--'], ['Fa', 'Sp', 'Su'], ['--', 'Sp', '--'], 
                ['Fa', '--', '--'], ['Fa', '--', 'Su'], ['Fa', '--', '--'], ['Fa', '--', '--'], ['--', 'Sp', '--'], 
                ['--', 'Sp', '--'], ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su'], 
                ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su'], 
                ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su'], 
                ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su'], ['Fa', 'Sp', 'Su']]

    prereqs = [[], ['MATH 1113'], ['MATH 2125'], ['CPSC 1302'], [], ['CPSC 1301'], ['CPSC 1301'], ['CPSC 1301'], ['CPSC 1301'], 
            ['CPSC 2108'], ['CPSC 2108', 'CPSC 2105'], ['CPSC 1302'], ['CPSC 3175'], [], ['CPSC 2105'], ['CPSC 3121'], 
            ['CYBR 2159', 'CPSC 2108'], ['CPSC 3175'], ['MATH 5125', 'CPSC 2108'], ['CPSC 5115'], ['CPSC 4175'], [], 
            ['CPSC 1301'], ['CPSC 1301'], ['CPSC 1302'], ['CPSC 3111'], ['CPSC 2108'], ['CPSC 3118', 'CPSC 3175'], 
            ['CPSC 4111'], ['CPSC 4111'], ['CPSC 1302'], ['CPSC 4121'], ['CPSC 2108', 'CPSC 3175'], ['CPSC 2108'], [], [], 
            ['CPSC 2108', 'CPSC 3175'], ['CPSC 3131'], ['CPSC 2108'], []]

    coreqs = [[], [], [], ['MATH 5125'], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], 
            [], [], ['CPSC 4113'], ['CPSC 4112'], [], [], [], [], [], [], [], [], [], []]

    recommended = [[], [], [], ['MATH 2125'], [], [], [], [], ['CYBR 2159'], [], [], [], [], [], [], [], [], [], [], [], [], [], 
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]

    isElective = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, 
                False, False, False, False, False, False, True, True, True, True, True, True, True, True, True, True, True, True, 
                True, True, True, True, True, True]

    restrictions = [[], [], [], [], [], [], [], [], [], [], [], [], [], ['jr', 'sr'], [], [], [], [], [], [], [], ['last semester'], 
                [], [], [], [], [], [], [], [], ['sp', 'jr', 'sr'], ['sp', 'jr', 'sr'], [], [], ['jr', 'sr'], ['jr', 'sr'], [], 
                [], [], ['jr', 'sr']]

    note = ['none', 'none', 'none', 'none', 'none', 'none', 'none', 'none','none', 'none', 'none', 'none','none', 'none', 
            'none', 'none','none', 'none', 'none', 'none','none', 'none', 'none', 'none','none', 'none', 'none', 'none',
            'none', 'none', 'none', 'none','none', 'none', 'none', 'none','none', 'none', 'none', 'none']

    def test_0_name(self):
        i = 0
        for course in self.courseIDs:
            test_name = self.container.get_name(course)
            confirmed_name = self.names[i]
            self.assertEqual(test_name, confirmed_name)
            i = i + 1
        print('Tested get_name to known list of names: ' + str(i) + ' test iterations passed')

    def test_1_availability(self):
        i = 0
        for course in self.courseIDs:
            test_availability = self.container.get_availability(course)
            confirmed_availability = self.availability[i]
            self.assertEqual(test_availability, confirmed_availability)
            i = i + 1
        print('Tested get_availabiity to known list of availability: ' + str(i) + ' test iterations passed')

    def test_2_prereqs(self):
        i = 0
        for course in self.courseIDs:
            test_prereqs = self.container.get_prereqs(course)
            confirmed_prereqs = self.prereqs[i]
            self.assertEqual(test_prereqs, confirmed_prereqs)
            i = i + 1
        print('Tested get_prereqs to known list of prereqs: ' + str(i) + ' test iterations passed')

    def test_3_coreqs(self):
        i = 0
        for course in self.courseIDs:
            test_coreqs = self.container.get_coreqs(course)
            confirmed_coreqs = self.coreqs[i]
            self.assertEqual(test_coreqs, confirmed_coreqs)
            i = i + 1
        print('Tested get_coreqs to known list of coreqs: ' + str(i) + ' test iterations passed')

    def test_4_recommended(self):
        i = 0
        for course in self.courseIDs:
            test_rec = self.container.get_recommended(course)
            confirmed_rec = self.recommended[i]
            self.assertEqual(test_rec, confirmed_rec)
            i = i + 1
        print('Tested get_recommended to known list of recommended: ' + str(i) + ' test iterations passed')

    def test_5_isElectives(self):
        i = 0
        for course in self.courseIDs:
            test_isElect = self.container.get_isElective(course)
            confirmed_isElect = self.isElective[i]
            self.assertEqual(test_isElect, confirmed_isElect)
            i = i + 1
        print('Tested get_isElective to known list of electives: ' + str(i) + ' test iterations passed')

    def test_6_restrictions(self):
        i = 0
        for course in self.courseIDs:
            test_res = self.container.get_restrictions(course)
            confirmed_res = self.restrictions[i]
            self.assertEqual(test_res, confirmed_res)
            i = i + 1
        print('Tested get_restrictions to known list of restrictions: ' + str(i) + ' test iterations passed')

    def test_7_note(self):
        i = 0
        for course in self.courseIDs:
            test_note = self.container.get_note(course)
            confirmed_note = self.note[i]
            self.assertEqual(test_note, confirmed_note)
            i = i + 1
        print('Tested get_note to known list of notes: ' + str(i) + ' test iterations passed')

# -----------END OF TESTCONTAINER---------------END OF TESTCONTAINER-----------------------END OF TESTCONTAINER----------

# this statement runs the test methods above; methods that start with test_xxxx... are assumed to be tested and are sorted
# so I number them to ensure order as written

if __name__ == '__main__':
    unittest.main()


