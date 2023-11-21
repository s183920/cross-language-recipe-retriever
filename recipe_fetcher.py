import os
import requests
from bs4 import BeautifulSoup
import time
import json
import re

class RecipeFetcher:
    recipe_translations = {
        "english": "recipe",
        "danish": "opskrift",
    }
    
    def __init__(self, language = "english", search_engine = "google"):
        self.language = language.lower()
        self.search_engine = search_engine
                
        # varible for keeping track of requests
        self.num_requests = 0
        
        # load translations
        self.translations = json.load(open("translations.json", encoding='utf-8'))
        if self.language not in self.translations:
            add_lang = input(f"Language {self.language} not found. Do you want to add it? (y/n) ")
            if add_lang.lower() in ["y", "yes"]:
                self.translations[self.language] = {}
                json.dump(self.translations, open("translations.json", 'w', encoding='utf-8'), indent=4, sort_keys=True)
                print(f"Language {self.language} added. Please add ingredient translations to translations.json")
            else:
                raise ValueError(f"Language {self.language} not supported")
        else:
            # dump to apply encoding to file if translations have been added manually
            json.dump(self.translations, open("translations.json", 'w', encoding='utf-8'), indent=4, sort_keys=True)
            
        # create dir for html files
        self.recipe_dir = f"{self.search_engine + '_results'}"
        os.makedirs(f"{self.recipe_dir}", exist_ok=True)
        self.recipe_key = self.translate("recipe")
            
    def save(self, content, fname):
        fname = os.path.split(fname)
        fname = os.path.join(fname[0], re.sub('[^\w\-_\. ]', '', fname[1]))
        with open(fname, 'w', encoding='utf-8') as fout:
            fout.write(content)
        
    def get_query(self, ingredients):
        return f"https://www.{self.search_engine}.com/search?q={self.recipe_key}+{'+'.join(ingredients)}"
    
    def request(self, url):
        if self.num_requests % 5 == 0:
            time.sleep(10)
        else:
            time.sleep(5)
            
        response = requests.get(url)
        self.num_requests += 1
        
        return response
        
    def translate(self, word):
        word = word.lower()
        if (not word in self.translations[self.language]) or (self.translations[self.language][word] == ""):
            add_word = input(f"{self.language.capitalize()} translation for {word} not found. Do you want to add it? (y/n) ")
            if add_word.lower() in ["y", "yes"]:
                self.translations[self.language][word] = input(f"Please enter {self.language} translation for '{word}': ").lower()
                json.dump(self.translations, open("translations.json", 'w', encoding='utf-8'), indent=4, sort_keys=True)
            else:
                raise ValueError(f"{self.language.capitalize()} translation for '{word}' not found")
        
        return self.translations[self.language][word]
        
    def fetch_recipe_links(self, *ingredients):
        print(f"Fetching recipes for {', '.join(ingredients)} in {self.language}...")
        
        # translate ingredients
        original_ingredients = ingredients
        ingredients = [self.translate(ingredient) for ingredient in ingredients]
        
        # create dir for recipe results
        recipe_result_dir = f"{self.recipe_dir}/{'+'.join(original_ingredients)}/{self.language}"
        os.makedirs(recipe_result_dir, exist_ok=True)
        
        # get result page
        response = self.request(self.get_query(ingredients))
        self.save(response.text, f"{recipe_result_dir + '/main'}.html")
        
        # extract all links
        soup = BeautifulSoup(response.text, "html.parser") 
        links = soup.find_all("a")
        
        # get recipe links and save html along with metadata
        metadata = {}
        num_recipes = 0
        for link in links:
            # find all headers
            headers = link.findAll("h3")
            assert len(headers) <= 1, "More than one header found"
            
            # skip to next link if no headers
            if len(headers) == 0:
                continue
            
            # extract metadata
            key = headers[0].text
            metadata[key] = {}
            metadata[key]["title"] = headers[0].text
            metadata[key]["link"] = link["href"].strip("/url?q=").split("&")[0]
            metadata[key]["rank_search_engine"] = num_recipes + 1
            
            # get recipe page and save if not already exists                
            if not os.path.exists(f"{recipe_result_dir + '/' + key}.html"):
                try:
                    recipe_response = self.request(metadata[key]["link"])
                    self.save(recipe_response.text, f"{recipe_result_dir + '/' + key}.html")
                    metadata[key]["downloaded"] = True
                except:
                    print(f"Could not fetch recipe: '{metadata[key]['title']}' from '{metadata[key]['link']}'")
                    metadata[key]["downloaded"] = False
            else:
                metadata[key]["downloaded"] = True
                
            # increment number of recipes
            print(f"Added recipe: '{metadata[key]['title']}'")
            num_recipes += 1

        # save metadata
        json.dump(metadata, open(f"{recipe_result_dir + '/metadata'}.json", 'w', encoding='utf-8'), indent=4, sort_keys=True)

        return metadata
    
if __name__ == "__main__":
<<<<<<< Updated upstream
    rf = RecipeFetcher(language = "danish")
=======
    rf = RecipeFetcher(language = "czech")
>>>>>>> Stashed changes
    
    # get test ingredients
    # for query in open("test_queries.txt", 'r').readlines():
    #     ingredients = query.strip().split()

    ingredients = ["egg", "chicken", "potato"]
    rf.fetch_recipe_links(*ingredients)
    
    # rf.fetch_recipe_links("chicken", "potato", "carrot")