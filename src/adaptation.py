#adaptation module – takes result object
#Get elective count from target object, case object
#if different, adapt recommended electives as needed (rules from adaptation phase above)
#update result object's elective list

import insertion

#returns elective count matrix - [target count, retrieved count]
def get_elective_count(result):
    target_case = result.get_target_case()
    target_elective_count = 0
    retrieved_case = result.get_retrieved_case()
    retrieved_elective_count = 0
    elective_count_matrix = []
    for target_case_course in target_case.get_course_list():
        if target_case_course == "CPSC 3000":
            target_elective_count += 1
    for retrieved_case_course in retrieved_case.get_course_list():
        if retrieved_case_course == "CPSC 3000":
            retrieved_elective_count += 1
    elective_count_matrix.append(target_elective_count)
    elective_count_matrix.append(retrieved_elective_count)
    return elective_count_matrix

#elective count matrix - [target count, retrieved count]
def resolve_difference(result, elective_count_matrix):
    elective_list = result.get_recommended_electives()
    if elective_count_matrix[0] > elective_count_matrix[1]:
        #target needs MORE electives than source recommended
        electives_needed = elective_count_matrix[0] - elective_count_matrix[1]
        print("Student needs", electives_needed, " more electives")
        while electives_needed != 0:
            course_input = input("Please enter an elective course: ")
            elective_list.append(course_input)
            electives_needed -= 1
        result.set_recommended_electives(elective_list)
        insertion.insert_into_case_base_solution(result)
        insertion.insert_into_case_base_problem(result)
        return result
    elif elective_count_matrix[0] < elective_count_matrix[1]:
        #target needs LESS electives than source recommended 
        electives_to_remove = elective_count_matrix[1] - elective_count_matrix[0]
        print("Student needs ", electives_to_remove, " less electives... Select one of the following to remove")
        while electives_to_remove != 0:
            for each in elective_list:
                print(each)
            course_to_remove = input("Please enter a course to remove: ")
            if course_to_remove in elective_list:
                elective_list.remove(course_to_remove)
                electives_to_remove -= 1
            else:
                print("Please enter a course that is present in recommended electives")
        result.set_recommended_electives(elective_list)
        insertion.insert_into_case_base_solution(result)
        insertion.insert_into_case_base_problem(result)
        return result
    else:
        #debug line
        print("No resolution needed - elective count is the same")
        #added below line to insert result into case base even if elective count is same
        #this means even if case a and case b have the SAME result, case a will still be added to case base (different problem, same solution)
        #versus if case a is input, and case a is retrieved then it would NOT be added as they are identical cases (same problem, same solution)
        insertion.insert_into_case_base_solution(result)
        insertion.insert_into_case_base_problem(result)
        return result
    
#determines how many electives needed to be added or removed
#returns string describing what is needed from the user 
def resolve_differences_new(elective_matrix):
    if elective_matrix[0] > elective_matrix[1]:
            elective_count_to_add = elective_matrix[0] - elective_matrix[1]
            return '\nPlease add ' + str(elective_count_to_add) + " electives"
    elif elective_matrix[0] < elective_matrix[1]:
            elective_count_to_remove = elective_matrix[1] - elective_matrix[0]
            return "\nPlease remove " + str(elective_count_to_remove) + " electives"
    else:
            return "\nNo elective adaptation required - count is the same"
    
def adaptation_main(result):
        if result.get_similarity_measure() == 1.0:
            print("No adaptation needed - identical case retrieved")
        else:
            elective_count = get_elective_count(result)
            resolve_difference(result, elective_count)