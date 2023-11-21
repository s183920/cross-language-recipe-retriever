import json

def fetch_rankings():

    languages = ["czech", "danish", "chinese"]



    with open(f'rankings/{languages[0]}.json', 'r') as file:
        data = json.load(file)


    # TODO: do for all languages and merge

    return data
    


if __name__ == "__main__":

    fetch_rankings()