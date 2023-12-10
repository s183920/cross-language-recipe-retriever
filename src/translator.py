"""
This module is responsible for translating the input text
"""

import json
import time


class Translator():

    def __init__(self, languages, approach="dictionary", hf_model = "nllb200", by_term = False, verbose = True):
        """
            Initialize the translator for the given languages.
            
            OBS: Using a non-dictionary approach requires the transformers library to be installed and will download the model which can take some time and requiere a lot of space.
        """

        self.languages = languages
        self.verbose = verbose
        self.by_term = by_term

        if approach == "dictionary":

            # load the translation dictionary
            with open(f'../translations.json', 'r') as file:
                self.translation_dict = json.load(file)

            # check if all languages are supported
            for language in self.languages:
                if language not in self.translation_dict.keys():
                    raise Exception(f'The language {language} is not supported.')
                else:
                    if verbose:
                        print(f'The language {language} is supported.')

            # define the translation function
            self.translate = self.translate_dict

        elif approach == "hf": # using a translation model

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
                if self.verbose:
                    print(f"Creating translation model for {language}...")
                self.hf_translators[language] = pipeline('translation', self.hf_model, src_lang=lang_codes["english"], tgt_lang=lang_codes[language])

            # define the translation function
            self.translate = self.translate_hf
            
        elif approach == "translatepy":
            from translatepy import Translator as translatepy_Translator
            self.pytranslator = translatepy_Translator()
            self.translate = self.translate_translatepy
            
        else:
            raise Exception(f'The approach {approach} is not supported. Use either "dictionary", "translatepy" or "hf".')
        
    def translate_translatepy(self, query, language):
        if language == "english":
            return query
        
        if self.by_term:
            query = query.split()
            
            translation = []
            for q in query:
                translation += [self.pytranslator.translate(q, destination_language=language, source_language="english").result]
                
            return " ".join(translation)
        else:
            return self.pytranslator.translate(query, destination_language=language, source_language="english")
        
        
        

    def translate_hf(self, query, language):
        if self.by_term:
            query = query.split()
        
        # translate the query
        translations = self.hf_translators[language](query)
        if self.by_term:
            return " ".join([translation["translation_text"].lower() for translation in translations])
        else:
            return translations[0]["translation_text"].lower()

    def translate_dict(self, query, language):
        """
            Translate the query to the given language.            
        """
            
        # return a identity for the english language - query is in english
        # if language == "english":
        #     return query
        
        # # return the translation from the dictionary
        # else:
            
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
        
def test_translators(verbose = True, by_term = True, acc_by_term = False, hf_translator = "nllb200"):
    # define languages
    languages = ["english", "czech", "chinese", "danish"]
    
    # initialize the translators
    t0 = time.time()
    translator_dict = Translator(languages, approach="dictionary", verbose=verbose, by_term=by_term)
    print(f"Dictionary translator initialized in {time.time() - t0:.3f} seconds")
    t0 = time.time()
    translator_hf = Translator(languages, approach="hf", verbose=verbose, hf_model=hf_translator, by_term=by_term)
    print(f"HuggingFace translator initialized in {time.time() - t0:.3f} seconds")
    t0 = time.time()
    translator_translatepy = Translator(languages, verbose=verbose, approach="translatepy", by_term=by_term)
    print(f"TranslatePy translator initialized in {time.time() - t0:.3f} seconds")
    
    # get the test queries
    test_queries = [line for line in open("../test_queries.txt", "r").read().split("\n") if line != ""]
    
    # initialize counts
    num_correct_hf = 0
    num_correct_py = 0
    num_translations = 0
    time_dict = 0
    time_hf = 0
    time_py = 0
    
    # test the translators
    for language in languages:
        num_correct_hf_lang = 0
        num_correct_py_lang = 0
        num_translations_lang = 0
        if verbose:
            print(f"Testing {language}...")
        for query in test_queries:
            # translate the query using dictionary approach
            t0 = time.time()
            dict_translation = translator_dict.translate(query, language)
            time_dict += time.time() - t0
            if verbose:
                print(f"Dictionary translation took {time.time() - t0:.3f} seconds")
            
            # translate the query using hugging face
            t0 = time.time()
            hf_translation = translator_hf.translate(query, language)
            time_hf += time.time() - t0
            if verbose:
                print(f"HuggingFace translation took {time.time() - t0:.3f} seconds")
                
            # translate the query using translatepy
            t0 = time.time()
            py_translation = translator_translatepy.translate(query, language)
            time_py += time.time() - t0
            if verbose:
                print(f"TranslatePy translation took {time.time() - t0:.3f} seconds")
            
            
            # update counts
            num_translations += 1 if not acc_by_term else len(query.split())
            num_translations_lang += 1 if not acc_by_term else len(query.split())
            if not acc_by_term:
                num_correct_hf += dict_translation == hf_translation
                num_correct_hf_lang += dict_translation == hf_translation
                num_correct_py += dict_translation == py_translation
                num_correct_py_lang += dict_translation == py_translation
            else:
                dict_translation_terms = dict_translation.split()
                hf_translation_terms = hf_translation.split()
                py_translation_terms = py_translation.split()
                num_correct_hf += sum([term in dict_translation_terms for term in hf_translation_terms])
                num_correct_hf_lang += sum([term in dict_translation_terms for term in hf_translation_terms])
                num_correct_py += sum([term in dict_translation_terms for term in py_translation_terms])
                num_correct_py_lang += sum([term in dict_translation_terms for term in py_translation_terms])
            
            # print results
            if verbose:
                print(f"Query: {query}")
                print(f"Translation (Dictionary): {dict_translation}")
                print(f"Translation (Hugging Face): {hf_translation}")
                print(f"Translation (TranslatePy): {py_translation}")
                print()
        
        # calculate accuracy for language
        print(f"Accuracy for {language} (Hugging Face): {num_correct_hf_lang / num_translations_lang:.3f}\n")
        print(f"Accuracy for {language} (TranslatePy): {num_correct_py_lang / num_translations_lang:.3f}\n")
    
    # calculate results
    results = {
        "accuracy_hf" : num_correct_hf / num_translations,
        "accuracy_py" : num_correct_py / num_translations,
        "time_dict" : time_dict / num_translations,
        "time_hf" : time_hf / num_translations,
        "time_py" : time_py / num_translations,
    }

    # print results
    print(f"Accuracy (Hugging Face): {results['accuracy_hf']:.3f}\n")
    print(f"Accuracy (TranslatePy): {results['accuracy_py']:.3f}\n")
    print(f"Average time for dictionary translation: {results['time_dict']:.3f} seconds")
    print(f"Average time for HuggingFace translation: {results['time_hf']:.3f} seconds")
    print(f"Average time for TranslatePy translation: {results['time_py']:.3f} seconds")    
    
    return results
    
        
        
if __name__ == "__main__":
    # translator = Translator(["danish", "english"], approach="translatepy", hf_model="m2m100", by_term=True, verbose=True)
    # translation = translator.translate("chicken egg potato", "english")
    # print(translation)
    
    test_translators(verbose=True, acc_by_term=True, hf_translator="nllb200")
    
    # from translatepy import Translator
    # translator = Translator()
    # translation = translator.translate("chicken egg potato".split(), "danish")
    # print(translation)