#Result object is used to store target case (Case object), retrieved case (Case object), 
#recommended electives [], and similarity measure int

class Result():

    def __init__(self, target_case, retrieved_case, recommended_electives, similarity_measure):
        self.target_case = target_case
        self.retrieved_case = retrieved_case
        self.recommended_electives = recommended_electives
        self.similarity_measure = similarity_measure

    def set_target_case(self, target_case):
        self.target_case = target_case

    def set_retrieved_case(self, retrieved_case):
        self.retrieved_case = retrieved_case

    def set_recommended_electives(self, recommended_electives):
        self.recommended_electives = recommended_electives

    def set_similarity_measure(self, similarity_measure):
        self.similarity_measure = similarity_measure

    def get_target_case(self):
        return self.target_case
    
    def get_retrieved_case(self):
        return self.retrieved_case
    
    def get_recommended_electives(self):
        return self.recommended_electives
    
    def get_similarity_measure(self):
        return self.similarity_measure