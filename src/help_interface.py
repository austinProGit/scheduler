# Thomas Merino
# 2/20/23
# CPSC 4175 Group Project


# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, Any
    from io import TextIOWrapper


from menu_interface_base import GeneralInterface
from difflib import SequenceMatcher
import os # TODO: this is only used for one thing, and it not good (see below)

HELP_FILENAME: str = 'help.html' # The filename of the program's help documentation (this must be kept in a specific format)
HELP_TERMINATOR: str = '</body>' # The string that ends help documentation parsing
HELP_PRE_START: str = '<h1>' # The string that will start help documentation parsing
HELP_HEADER_START_TOKEN: str = '<h3>' # The string that will start header string
HELP_HEADER_END_TOKEN: str = '</h3>' # The string that will end header string
HELP_TAG_START_TOKEN: str = '<!--' # The string that will start tokens string
HELP_TAG_END_TOKEN: str = '-->' # The string that will end tokens string
HELP_PARAGRAPH_START_TOKEN: str = '<p>' # The string that will start paragraph string
HELP_PARAGRAPH_END_TOKEN: str = '</p>' # The string that will end paragraph string

# The following are string to remove from the article if ecnountered
HELP_REMOVED_FROM_PARAGRAPH: list[str] = ['<ul>', '</ul>', '<li>', '</li>', '<ol>', '</ol>', '<a>', '</a>']

HELP_QUERY_ACCEPTANCE: float = 0.7 # Level of tolerance (0.0 to 1.0) while searching help documentation

# The following is the help menu for the program. It handles presenting and searching for program documentation. It loads
# the contents of the help file upon being intialized. It stores the articles' headers, keywords (for searching), and content.
# Searching does accept slightly misspelled words.

class HelpMenu(GeneralInterface):
    '''A menu object used for parsing help documentation.'''
    
    def __init__(self):
        self.name: str = 'HELP MENU'
        self.headers: list[str] = [] # List of help article headers (for displaying the title of the article)
        self.keywords: list[str] = [] # List of help article keywords (what is used to search for articles)
        self.articles: list[str] = [] # List of article contents
        self.article_count: int = 0 # The number of articles loaded into the object
        
        # Open the help file and extract the headers, keywords, and articles
        # The help file is expected to have the following format (breaks are indicated by \n escapes):
        # Header \n Keywords seperated by white spaces \n Article contents \n Line seperator (for easier editing) \n ... \n <END>
        
        # TODO: This is not sustainable (using __file__)
        help_filename: Any = os.path.join(os.path.dirname(__file__), HELP_FILENAME)
        documentation: TextIOWrapper
        with open(help_filename, 'r') as documentation:

            # Consume head and other starting content
            while HELP_PRE_START not in documentation.readline(): pass
            
            while documentation:
                new_header: Optional[str] = self.parse_file_with_tokens(documentation, HELP_HEADER_START_TOKEN, HELP_HEADER_END_TOKEN)
                
                if not new_header:
                    break
                self.headers.append(new_header)
                new_tags = self.parse_file_with_tokens(documentation, HELP_TAG_START_TOKEN, HELP_TAG_END_TOKEN).split()
                self.keywords.append(new_tags)
                article = self.remove_tokens_from_string(self.parse_file_with_tokens(documentation, HELP_PARAGRAPH_START_TOKEN, HELP_PARAGRAPH_END_TOKEN), '<table>', '</table>')

                for string_to_removed in HELP_REMOVED_FROM_PARAGRAPH:
                    article = article.replace(string_to_removed, '')

                self.articles.append(
                    article
                )
                self.article_count += 1
    
    # Helper function for reading the contents of the help documentation
    def parse_file_with_tokens(self, file: TextIOWrapper, start_token: str, end_token: str) -> Optional[str]:
        result: str = ''
        line: str = file.readline()
        while line and start_token not in line:
            line = file.readline()
        if not line:
            return None # EOF
        if end_token in line:
            return line[line.index(start_token) + len(start_token):line.index(end_token)]
        result = line[line.index(start_token) + len(start_token):]
        line = file.readline()
        while end_token not in line:
            result += line
            line = file.readline()
        result += line[:line.index(end_token)]
        return result

    def remove_tokens_from_string(self, string: str, start_token: str, end_token: str) -> str:
        # TODO: verify the changes to this method is correct
        result: str = string
        start_index: int = string.find(start_token)
        end_index: int = string.find(end_token)
        if start_index != -1 and end_index != -1:
            result = self.remove_tokens_from_string(string[:start_index] + string[:end_index+len(end_token)], start_token, end_token)
        return result

        # TODO: HERE IS WERE I STOPPED ADDING ANNOTATIONS:

    def parse_input(self, controller, input):
        '''Handle input on behalf of the program.'''
        
        if input == 'exit' or input == 'quit' or input == '':
            # Exit the help menu
            controller.pop_interface(self)
        
        elif 'all' in input:
            # List all articles
            for article_index in range(self.article_count):
                controller.output(self.headers[article_index])
                controller.output(self.articles[article_index])
        else:
            # The input did not match a command (search for an article)
            controller.output('Now searching for "{0}"...'.format(input))
            possible_article_indices = self._search_for_keywords(input)
            self.list_articles(controller, possible_article_indices)
    
    
    def _search_for_keywords(self, query):
        '''Get a list of article indices that match the passed query.'''
        
        possible_article_indices = []
        matcher = SequenceMatcher()
        query_words = set(query.split())
        
        # Helper function for determining if the article matches the query (close enough, anyhow)
        def article_matches_query(keyword):
            matcher.set_seq1(keyword)
            for query_word in query_words:
                matcher.set_seq2(query_word)
                if matcher.ratio() >= HELP_QUERY_ACCEPTANCE:
                    return True
            return False
        
        for article_index in range(self.article_count):
            for keyword in self.keywords[article_index]:
                if article_matches_query(keyword):
                    possible_article_indices.append(article_index)
                    break
        
        return possible_article_indices
    
    
    def list_articles(self, controller, possible_article_indices):
        '''List the articles from the passed list of indices (as the result of a search).'''
        
        possible_articles_count = len(possible_article_indices)
        
        if possible_articles_count == 0:
            controller.output('Sorry, no matches found. Please try using different keywords.\n')
        elif possible_articles_count == 1:
            controller.output('This might help:\n')
            controller.output(self.headers[possible_article_indices[0]])
            controller.output(self.articles[possible_article_indices[0]])
        else:
            # TODO: We may introduce an article selection menu here
                    
            controller.output('These might help:\n')
            for article_index in possible_article_indices:
                controller.output(self.headers[article_index])
                controller.output(self.articles[article_index])
    
# End of HelpMenu definition