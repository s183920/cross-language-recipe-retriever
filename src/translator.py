"""
This module is responsible for translating the input text
"""

import json


class Translator():

    def __init__(self, languages, dictionary_approach=True, hf_model = "m2m100"):
        """
            Initialize the translator for the given languages.
            
            OBS: Using a non-dictionary approach requires the transformers library to be installed and will download the model which can take some time and requiere a lot of space.
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

            # define the translation function
            self.translate = self.translate_dict

        else: # using a translation model

            from transformers import pipeline
            
            # define available models
            self.models = {
                "m2m100" : "facebook/m2m100_418M",
                "nllb200" :"facebook/nllb-200-distilled-600M",
            }
            
            # get model
            if hf_model not in self.models.keys():
                raise Exception(f'The model {hf_model} is not supported.')
            else:
                self.hf_model = self.models[hf_model]
                
            # get language codes
            lang_codes = json.load(open(f"../hf_lang_codes/{hf_model}.json", "r"))
            
            # create translation models
            self.hf_translators = {}
            for language in self.languages:
                print(f"Creating translation model for {language}...")
                self.hf_translators[language] = pipeline('translation', self.hf_model, src_lang=lang_codes["english"], tgt_lang=lang_codes[language])

            # define the translation function
            self.translate = self.translate_hf

    def translate_hf(self, query, language):
        translations = self.hf_translators[language](query)
        return translations[0]["translation_text"].lower()

    def translate_dict(self, query, language):
        """
            Translate the query to the given language.            
        """
            
        # return a identity for the english language - query is in english
        if language == "english":
            return query
        
        # return the translation from the dictionary
        else:
            
            # split the query into words
            query_words = query.split()

            # translate the words
            translated_words = []

            # dictionary translate
            for word in query_words:
                if word in self.translation_dict[language].keys():
                    translated_words.append(self.translation_dict[language][word])
                else:
                    translated_words.append(word) # keep the original word if no translation is found

            # join the translated words into a string
            translated_query = ' '.join(translated_words)

            return translated_query
        
if __name__ == "__main__":
    translator = Translator(["danish"], dictionary_approach=False, hf_model="m2m100")
    translation = translator.translate("chicken egg potato", "danish")
    print(translation)