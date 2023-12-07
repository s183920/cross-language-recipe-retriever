# cross-language-recipe-retriever
Information retrieval system for finding recipes in multiple languages


queries we want to annotate (disregard the recipe in our model): 

  1. "recipe egg chicken potato"
  2. "recipe pork garlic butter"
  3. "recipe chocolate butter sugar"
  4. "recipe carrots chicken rice"
  5. "recipe cheese cabbage chilli"
  6. "recipe beef mushrooms pasta"
  7. "recipe milk flour vanilla"
  8. "recipe broccoli tomato mozzarella"
  9. "recipe eggplant onion soy-sauce"
  10. "recipe sugar spinach seaweed"

Google these in both your natural language and english, parse the document and save them, rank them 0-5. 


## Ranking criteria

**Score 0**: 
The recipe does not contain all the ingredients or the recipe could not be accessed properly

**Score 1**:
The recipe contains all ingredients, but some of them are only used faintly, i.e. the ingredient is not a significant part of the recipe and could be left out without affecting the recipe too much.

**Score 2**:
The recipe contains and uses all ingredients, but it combines them strangely or the recipe does not look like something you would cook.


**Score 3**:
The recipe contains all ingredients and all ingredients are a significant part of the dish. Furthermore, you would be willing to actually try out the recipe.

## Installation
```console
pip install -r requirements.txt
```
