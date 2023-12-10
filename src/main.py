import argparse
from cross_language_retriever import CrossLanguageRetriever


def Cross_language_recipes():
    """
        Retrieve the recipes for the given query in English
        Fully functional system of recipes retrieval in 4 languages

        Example: python3 main.py "eggplant onion soy-sauce"
    """
    
    # Initialize the command-line argument parser
    parser = argparse.ArgumentParser(description="Cross Language Information Retrieval System")
    parser.add_argument("query", type=str, help="Enter the search query in English\
                                                 surrounded by double quotes.")
    args = parser.parse_args()

    # choose translation method
    # method = "dictionary"
    # method = "hf"
    method = "translatepy"

    # Initialize the retriever
    retriever = CrossLanguageRetriever(["english", "czech", "chinese", "danish"], 
                                       translation_approach = method, verbose=True)

    # Perform search with the provided query
    results_merged, results_by_lan = retriever.search(args.query)

    # Print the merged results
    print("\n\nMerged results:")
    for i in range(len(results_merged)):
        print(f'{i+1:2} {results_merged[i].docid:4} {results_merged[i].score:.5f}')


if __name__ == "__main__":

    Cross_language_recipes()