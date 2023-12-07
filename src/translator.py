"""
This module is responsible for translating the input text
"""

import json

class Translator():

    def __init__(self, languages, dictionary_approach=True):
        """
            Initialize the translator for the given languages.
        """

        self.languages = languages

        if dictionary_approach:

            # load the translation dictionary
            with open(f'../translations.json', 'r') as file:
                self.translation_dict = json.load(file)

            # check if all languages are supported
            for language in self.languages:
                if language not in self.translation_dict.keys():
                    raise Exception(f'The language {language} is not supported.')
                else:
                    print(f'The language {language} is supported.')


    def translate(self, query, language):
        """
            Translate the query to the given language.            
        """
            
        # return a identity for the english language - query is in english
        if language == "english":
            return query
        
        # return the translation from the dictionary
