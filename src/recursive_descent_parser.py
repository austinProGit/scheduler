# Author: Max Lewis 02/25/23
import re

class ReqNode:

  def __init__(self, n_type="", children=[], value="", content=""):
    self.n_type = n_type
    self.children = children  # list of root nodes for other subtrees, or just the nodes for deliverables
    self.value = value  # single string value for node


def create_deliverable_node(course):
    d_node = ReqNode()
    d_node.n_type = "d"
    d_node.value = f"[d <n={course}>]"
    return d_node


def create_exhaustive_node(children):
    e_node = ReqNode()
    e_node.n_type = "e"
    e_node.children = children
    e_node.value = "[e <n=Requires All:>"
    return e_node


def create_selective_node(children):
    s_node = ReqNode()
    s_node.n_type = "s"
    s_node.children = children
    s_node.value = "[s <c=1, n=Requires 1:>"
    return s_node

def stringify_subtree(root, level=0):
    if root.n_type == "d":
        return "\t" * level + str(root.value) + "\n"
    else:
        result = "\t" * level + str(create_tree_header(root)) + "\n"
        for child in root.children:
          result += stringify_subtree(child, level + 1)
        result += "\t" * level + "]\n"
        return result

def create_tree_header(root):
    string = ""
    if root.n_type == "e" or root.n_type == "s":
        string += root.value
    return string


# ------------ END OF REQNODE CLASS AND HELPER METHODS --------------- END OF REQNODE CLASS AND HELPER METHODS ---------------

# ------------ RECURSIVE DESCENT PARSER CLASS AND METHODS -------------RECURSIVE DESCENT PARSER CLASS AND METHODS ------------

# The Recursive Descent Parser acts like a mini compiler and is able to parse through tokenized items that arbitrarily occur.  
# In this case we created a list of tokens with 'XXXX ####', '(', ')', 'and', 'or', which we parse through and return
# the root node of a tree.  Each node may have multiple children.  

class RecursiveDescentParser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = self.tokens[0] if self.tokens != [] else None
        self.previous_token = None
        self.pattern = r"[A-Z]{3}[A-Z]?\s\d{4}[A-Z]?"
        self.index = 0

    def advance(self):
        self.index += 1
        self.previous_token = self.current_token
        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
        else:
            self.current_token = None

    def factor(self):
        if re.search(self.pattern, self.current_token):
            self.advance()
            return create_deliverable_node(self.previous_token)
        elif self.current_token == "(":
            self.advance()
            subtree = self.expression()  #has to be an expression here
            if self.current_token == ")":
                self.advance()
                return subtree
            else:
                print("right paren not detected")
        else:
            print("factor: syntax error")
            return

    def term(self):
        factors = []
        new_factor = self.factor()  #has to be a factor
        factors.append(new_factor)
        while self.current_token == "and":  #zero or more factors?
            self.advance()
            new_factor = self.factor()
            factors.append(new_factor)
        if len(factors) == 1:
            return factors[0]
        else:
            return create_exhaustive_node(factors)

    def expression(self):
        terms = []
        new_term = self.term()  #has to be a term
        terms.append(new_term)
        while self.current_token == "or":  #zero or more terms?
            self.advance()
            new_term = self.term()  #has to be a term
            terms.append(new_term)
        if len(terms) == 1:
            return terms[0]
        else:
            return create_selective_node(terms)

# ------------ END OF RECURSIVE DESCENT PARSER CLASS AND METHODS ------END OF RECURSIVE DESCENT PARSER CLASS AND METHODS ----

# ------------ RECURSIVE DESCENT EDITOR CLASS AND METHODS -------------RECURSIVE DESCENT EDITOR CLASS AND METHODS -----------

# The Recursive Descent Editor performs cleaning specified for requisites.

class RecursiveDescentEditor:

    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = self.tokens[0] if self.tokens != [] else None
        self.previous_token = None
        self.pattern = r"[A-Z]{3}[A-Z]?\s\d{4}[A-Z]?"
        self.new_tokens = []
        self.count = 0
        self.index = 0

    def is_course(self, token):
        if token == None: return False
        if re.search(self.pattern, token): return True 
        return False

    def del_end(self):
        for token in reversed(self.new_tokens):
            if self.check_factor(token):
                break
            else:
                self.new_tokens.pop()

    def advance(self):
        self.index += 1
        self.previous_token = self.current_token
        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
        else:
            self.current_token = None
            self.del_end()
            self.del_paren()

    def check_factor(self, token):
        if token == None: return False
        found = False
        factors = ["(", ")"]
        if re.search(self.pattern, token): found = True
        if token in factors: found = True
        return found

    def check_operator(self, token):
        if token == None: return False
        found = False
        operators = ["and", "or"]
        if token in operators: found = True
        return found

    def del_paren(self):
        if self.count > 0 and "(" in self.new_tokens:
            for i in range(self.count):
                self.new_tokens.remove("(")
        elif self.count < 0 and ")" in self.new_tokens:
            absolute = abs(self.count)
            for i in range(absolute):
                self.new_tokens.remove(")")

    def paren(self):
        if self.current_token == "(":
            self.new_tokens.append(self.current_token)
            self.count += 1
            self.advance()
            return
        if self.current_token == ")":
            self.new_tokens.append(self.current_token)
            self.count -= 1
            self.advance()
            return
        else:
            return


    def course(self):
        self.paren()
        while not self.is_course(self.current_token):
            self.advance()
            if self.current_token == None: return
        while self.is_course(self.current_token):
            self.new_tokens.append(self.current_token)
            self.advance()
            self.paren()
        return

    def operator(self):
        self.course()           
        while not self.check_operator(self.current_token):
            self.advance()
            if self.current_token == None: return
        while self.check_operator(self.current_token):
            self.new_tokens.append(self.current_token)
            self.advance()
            self.course()
        return
#'''
#string = ") and EXSC 4131"# or (KINS 3135 with a minimum grade of C and EXSC 4131 with a minimum grade of C) or (EXSC 3135 with a minimum grade of C and KINS 4131 with a minimum grade of C)"

#def create_tokenized_logic(section):
#    tokens = None
#    regex_pattern = r"\(|\)|and|or|[A-Z]{3}[A-Z]?\s\d{4}[A-Z]?"
#    tokens = re.findall(regex_pattern, section)
#    return tokens

#tokensa = create_tokenized_logic(string)
#parser = RecursiveDescentEditor(tokensa)
#parser.operator()
#print(parser.new_tokens)
#print(tokensa)
#'''
