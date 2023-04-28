#this module gives reasoning when button 'Give reasoning for recommendation" is pressed
#compares features in common between target case and retrieved case

import output_fetch
import similarity_measure

def similar_pair_retrive(selected_file):
    similar_pair = output_fetch.get_similar_pair(selected_file)
    return similar_pair

def compare_gpa(similar_pair):
    target_gpa = similar_pair[0].get_gpa()
    source_gpa = similar_pair[1].get_gpa()
    print("GPA is currently the highest weighted feature for selecting electives")
    print("Your GPA: ", target_gpa)
    print("Most similar case's GPA: ", source_gpa)

def compare_programming_courses(similar_pair):
    target_programming_courses = similarity_measure.get_programming_classes_needed(similar_pair[0])
    source_programming_courses = similarity_measure.get_programming_classes_needed(similar_pair[1])
    print("The second highest weighted feature is which programming courses you've taken")
    print("Specifically, we look for CPSC 1301, 1302, and 2108")
    if target_programming_courses == []:
        print("You have taken all of the above classes")
        print("The most similar case has also taken all of those classes")
    else:
        print("You still need to take... ")
        for course_target in target_programming_courses:
            print(course_target)
        print("Most similar case also needs to take... ")
        for course_source in source_programming_courses:
            print(course_source)

def results_driver(selected_file):
    similar_pair = similar_pair_retrive(selected_file)
    compare_gpa(similar_pair)
    compare_programming_courses(similar_pair)

def compare_gpa_new(similar_pair):
    gpa_string = ""
    target_gpa = similar_pair.get_target_case().get_gpa()
    source_gpa = similar_pair.get_retrieved_case().get_gpa()
    gpa_string += "GPA is currently the highest weighted feature for selecting electives"
    gpa_string += ("\nYour GPA: " + target_gpa)
    gpa_string += ("\nMost similar case's GPA: " + source_gpa)
    return gpa_string

def compare_programming_courses_new(similar_pair):
    compare_courses_string = "\n"
    target_programming_courses = similarity_measure.get_programming_classes_needed(similar_pair.get_target_case())
    source_programming_courses = similarity_measure.get_programming_classes_needed(similar_pair.get_retrieved_case())
    compare_courses_string += "\nThe second highest weighted feature is which programming courses you've taken"
    compare_courses_string += "\nSpecifically, we look for CPSC 1301, 1302, and 2108"
    if target_programming_courses == []:
        compare_courses_string += "\nYou have taken all of the above classes"
        compare_courses_string += "\nThe most similar case has also taken all of those classes"
    else:
        compare_courses_string += "\nYou still need to take... "
        for course_target in target_programming_courses:
            compare_courses_string += course_target
        compare_courses_string += "\nMost similar case also needs to take... "
        for course_source in source_programming_courses:
            compare_courses_string += course_source
    return compare_courses_string


def results_driver_new(result):
    results_string = " "
    if isinstance(result, str):
        return result
    results_string += compare_gpa_new(result)
    results_string += compare_programming_courses_new(result)
    return results_string
