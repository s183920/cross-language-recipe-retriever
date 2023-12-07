"""
Module which includes functions for creating index .json files
and indexes.
"""

from bs4 import BeautifulSoup
import os
import json
import subprocess

def html_to_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

def save_json(recipe_text, recipe_name, lang):
    """
    Saves the given recipe text as a .json file.
    """

    # create a dictionary with "docid" and "content" keys
    doc_data = {"id": recipe_name[:-5], "contents": recipe_text}

    # create the directory if it doesn't exist
    if not os.path.exists(f"../indexes/json_files/{lang}"): 
        os.makedirs(f"../indexes/json_files/{lang}")

    # save the json file
    with open(f"../indexes/json_files/{lang}/{recipe_name[:-5]}.json", 'w') as file:
        json.dump(doc_data, file)

def build_index_json(lang = "english"):
    """
    Builds the json index for the given recipes and given language.
    """

    # recipes folder
    recipesDir = f"../google_results/"

    # iterate over recipes
    for recipe in os.listdir(recipesDir):

        print("converting documents from: ", recipe)

        langDir = recipesDir + recipe + "/" + lang + "/"

        # iterate over html files for a specific recipe and language
        for filename in os.listdir(langDir):

            # skip the redundant files
            if filename == "main.html": continue 
            if not filename.endswith(".html"): continue

            # open the html file
            with open(langDir + filename, 'r') as file:
                recipe_html = file.read()

            # convert to text
            recipe_text = html_to_text(recipe_html)

            # process the text
            recipe_text = text_process(recipe_text)

            # save the json file
            save_json(recipe_text, filename, lang)

def text_process(text):
    """
    Processes the given text.
    """

    # remove the \n characters
    text = text.replace("\n", " ")

    return text

def build_index(lang="english"):

    # specify the index name
    index_name = lang + "_index"

    # specify the iso language code
    if lang == "english": ISO_lan_code = "en"
    elif lang == "czech": ISO_lan_code = "cs"
    elif lang == "chinese": ISO_lan_code = "zh"
    elif lang == "danish": ISO_lan_code = "da"

    # the following command builds the index from the json files
    subprocess.run(f"python -m pyserini.index.lucene \
                --collection JsonCollection \
                --language {ISO_lan_code} \
                --input ../indexes/json_files/{lang} \
                --index ../indexes/{index_name} \
                --generator DefaultLuceneDocumentGenerator \
                --threads 1 \
                --storeDocvectors", shell=True)

if __name__ == "__main__":
    
    # lang = "english"
    # lang = "czech"
    lang = "chinese"

    # build the json index
    build_index_json(lang=lang)

    # build the index
    build_index(lang=lang)