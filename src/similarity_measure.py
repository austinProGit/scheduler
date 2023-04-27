import case_creator
import Case

def measure_global_similarity(local_similarity_gpa, course_similarity_matrix):
    weight1 = 6
    weight2 = 2
    list_similarity_values = []
    sim_value_weight1 = (weight1 * local_similarity_gpa) / (weight1 + weight2)
    list_similarity_values.append(sim_value_weight1)
    different_count = 0
    for value in course_similarity_matrix:
        if value == 0:
            different_count += 1
    same_count = 3 - different_count
    sim_value_weight2 = (weight2 / (weight1 + weight2)) * same_count
    list_similarity_values.append(sim_value_weight2)
    global_similarity = sum(list_similarity_values)
    rounded_global_similarity = round(global_similarity, 4)
    #max value for these features/weights is 1.435 - normalizing this down to a value of 1 for identical cases
    #this makes it more user friendly as people are used to a percentage scale where 1 or 100% is the maximum
    normalized_global_similarity = rounded_global_similarity - .5
    return round(normalized_global_similarity, 4)

#works correctly if gpa in source file is in format "GPA: X.XX"
def format_gpa(case_object):
    gpa = float(case_object.get_gpa()[5:9])
    return gpa

def distance_measure_gpa(target_gpa, source_gpa):
    numerator = abs(target_gpa - source_gpa)
    #denominator in distance measure equations is maximum value - minimum value
    denominator = (4-1)
    distance_measure = numerator / denominator
    return distance_measure

def calculate_local_similarity_gpa(distance_measure):
    local_similarity_gpa = 1 - distance_measure
    return local_similarity_gpa

#programming classes is feature 1
def get_programming_classes_needed(case_object):
    programming_courses = []
    for course_target in case_object.get_course_list():
        if course_target == "CPSC 1301":
            programming_courses.append(course_target)
        elif course_target == "CPSC 1302":
            programming_courses.append(course_target)
        elif course_target == "CPSC 2108":
            programming_courses.append(course_target)
    return programming_courses

#order matters in this function - comparing target to source and source to target gives diff values for similarity
def get_similarity_matrix_courses(target_programming_courses, source_programming_courses):
    course_similarity_matrix = []
    if target_programming_courses == [] and source_programming_courses == []:
        course_similarity_matrix = [1, 1, 1]
        return course_similarity_matrix
    else:
        for target_course in target_programming_courses:
            if target_course in source_programming_courses:
                course_similarity_matrix.append(1)
            else:
                course_similarity_matrix.append(0)
    return course_similarity_matrix

def single_input_driver(selected_file):
    #print("Maximum similarity measure for selected weights and features: 1.0")
    target = case_creator.single_input_object_driver(selected_file)
    target_object = case_creator.create_single_input_object(target)
    target_filename = target_object.get_file_name()
    target_programming_courses = get_programming_classes_needed(target_object)
    #debug line
    #print("target programming courses: ", target_programming_courses)
    target_gpa = format_gpa(target_object)
    case_base_object_list = case_creator.case_base_object_driver()
    index = 0
    most_similar_pair = None
    for case_object in case_base_object_list:
        source_programming_courses = get_programming_classes_needed(case_object)
        source_gpa = format_gpa(case_object)
        course_similarity_matrix = get_similarity_matrix_courses(target_programming_courses, source_programming_courses)
        distance_measure = distance_measure_gpa(target_gpa, source_gpa)
        local_similarity_gpa = calculate_local_similarity_gpa(distance_measure)
        global_similarity = measure_global_similarity(local_similarity_gpa, course_similarity_matrix)
        case_object_filename = case_base_object_list[index].get_file_name()
        #print("Target filename: ", target_filename)
        #print("Case Base filename: ", case_object_filename)
        #print("Global similarity measure: ", global_similarity)
        #print("########################################################################")
        index += 1
        if not most_similar_pair:
            most_similar_pair = [target_object, case_object, global_similarity]
        elif most_similar_pair[2] < global_similarity:
            most_similar_pair = [target_object, case_object, global_similarity]
        else:
            continue
    return most_similar_pair

def sim_measure_main(selected_file):
    most_similar_pair = single_input_driver(selected_file)
    #print("Most similar pair: ", most_similar_pair[0].get_file_name(), "-", most_similar_pair[1].get_file_name())
    #print("Global Simiilarity Measure: ",most_similar_pair[2])
    return most_similar_pair
