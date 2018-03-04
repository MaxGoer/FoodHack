import dill
import json
import artm
import numpy as np
from predproces import save_vowpal_wabbit, get_model
from sklearn.metrics.pairwise import cosine_similarity


# Globals
#tokenizer = None
#recipes_features = None
#dictionary = None
#batch_vectorizer = None
#recipes = None
#model = None


#def init():
#    global tokenizer, recipes_feautures, dictionary, batch_vectorizer, recipes, model

#    tokenizer = dill.load(open('tokenizer', 'rb'))
#    recipes_features = np.load('recipes_features.npy')

#    with open('recipes.txt') as fl:
#        recipes = json.loads(fl.read())
        
    #dictionary = artm.Dictionary()
    #dictionary.gather(data_path='batches')
    #batch_vectorizer = artm.BatchVectorizer(data_path='batches', data_format='batches')

    #model = get_model(dictionary, batch_vectorizer)


def get_recipe(query):
    tokenizer = dill.load(open('tokenizer', 'rb'))
    recipes_features = np.load('recipes_features.npy')
    
    with open('recipes.txt') as fl:
        recipes = json.loads(fl.read())
    
    dictionary = artm.Dictionary()
    dictionary.gather(data_path='batches') 
    batch_vectorizer = artm.BatchVectorizer(data_path='batches', data_format='batches')

    model = get_model(dictionary, batch_vectorizer)

    save_vowpal_wabbit(tokenizer.transform([query]), 'query/query.txt')
    batch_vectorizer = artm.BatchVectorizer(data_path='query/query.txt',
                                            data_format='vowpal_wabbit',
                                            target_folder='query/batches',
                                            class_ids=['unigram', 'ngram'])
    query = model.transform(batch_vectorizer).T.values
    return recipes[cosine_similarity(query, recipes_features)[0].argmax()]


if __name__ == "__main__":
    #init()
    print(get_recipe('Очень люблю морепродукты и особенно креветки'))
