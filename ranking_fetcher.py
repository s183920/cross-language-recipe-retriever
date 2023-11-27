import json
import glob
import re
import os

def fetch_rankings():

    languages = ["czech", "danish", "chinese"]



    with open(f'rankings/{languages[0]}.json', 'r') as file:
        data = json.load(file)


    # TODO: do for all languages and merge

    return data
    
    
def create_ranking_file(language):
    # get files
    rankings_file = f"rankings/{language}.json"
    metadata_files = glob.glob(f"google_results/*/{language}/*metadata.json")
    # print(metadata)
    
    # check if rankings file exists
    if os.path.exists(rankings_file):
        with open(rankings_file, 'r') as file:
            rankings = json.load(file)
    else:
        rankings = {}
    
    # 
    for metadata_file in metadata_files:
        # get query key
        metadata_file = metadata_file.replace("\\", "/")
        query_key = re.search(fr"google_results/(.*)/{language}.*", metadata_file).group(1)
        
        # check if query key is already in rankings - if so, skip to avoid overwriting
        if query_key in rankings:
            continue
        
        # load metadata
        with open(metadata_file, 'r') as file:
            metadata = json.load(file)
            
        # add ranking to dict
        for entry in metadata:
            metadata[entry]["ranking_manual"] = None

        rankings[query_key] = metadata
    
    # save rankings
    with open(f'rankings/{language}.json', 'w') as file:
        json.dump(rankings, file, indent=4, sort_keys=True)


if __name__ == "__main__":

    # fetch_rankings()
    create_ranking_file("danish")