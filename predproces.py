import re
import math
import artm
import pymorphy2
import langdetect
import googletrans
import numpy as np

from collections import Counter
from heapq import heapify, heappop, heappush

from stop_words import get_stop_words

morph = pymorphy2.MorphAnalyzer()


def dump_vowpal_wabbit(tokens):
    return ' '.join(['|'+name+' '+' '.join([token+':'+str(count) if count>1 else token 
                                            for token, count in Counter(tokens).items()]) 
                     for name, tokens in [('unigram', ' '.join(tokens).split()), 
                                          ('ngram', [token.replace(' ', '_') 
                                                     for token in tokens if ' ' in token])]])
def save_vowpal_wabbit(texts_tokens, path):
    with open(path, 'w') as fl:
        fl.write(''.join(['doc%d '%i+dump_vowpal_wabbit(tokens)+'\n' for i, tokens in enumerate(texts_tokens)]))
        
def get_model(dictionary, batch_vectorizer):
    model = artm.ARTM(num_topics=250+3, dictionary=dictionary,  cache_theta=True, class_ids=['unigram', 'ngram'])
    model.scores.add(artm.TopTokensScore(name='TopTokensScore_u', num_tokens=10, class_id='unigram'))
    model.scores.add(artm.TopTokensScore(name='TopTokensScore_n', num_tokens=10, class_id='ngram'))

    model.regularizers.add(artm.SmoothSparsePhiRegularizer(name='SparsePhi', tau=-0.1, 
                                                       class_ids=['unigram', 'ngram'],
                                                       topic_names=model.topic_names[:-3]))
    model.regularizers.add(artm.SmoothSparsePhiRegularizer(name='SmoothPhi', tau=0.1, 
                                                       class_ids=['unigram', 'ngram'],
                                                       topic_names=model.topic_names[-3:]))
    model.fit_offline(batch_vectorizer=batch_vectorizer, num_collection_passes=5)
    return model 

class Tokenizer:
    
    def __init__(self, split_pattern=r'([^\w_-]|[+])', unigram_pattern=r'[а-яa-z][а-яa-z-]+[а-яa-z]',
                 chunk_delimiter='|', stopwords=True, min_support=2, threshold=2):
        
        self.split_pattern = re.compile(split_pattern)
        self.unigram_pattern = re.compile(unigram_pattern)
        self.chunk_delimiter = chunk_delimiter
        
        if hasattr(stopwords, '__iter__'): 
            self.stopwords = set(stopwords)
        elif stopwords: 
            self.stopwords = set(get_stop_words('ru'))
        else: 
            self.stopwords = set()
            
        self.min_support = min_support
        self.threshold = threshold
        
        self.counter = None
            
    def __predprocesser(self, text):
        tokens = [token.strip() for token in self.split_pattern.split(text.lower()) if token.strip()]
        tokens = map(lambda x: self.unigram_pattern.findall(x), tokens)
        tokens = np.hstack([token if token else self.chunk_delimiter for token in tokens])
        tokens = map(lambda x: morph.parse(x)[0].normal_form, tokens)
        tokens = [self.chunk_delimiter if (token in self.stopwords) else token for token in tokens]
        
        text = re.sub(r'\%s[\%s ]+\%s'%tuple(3*[self.chunk_delimiter]), self.chunk_delimiter, ' '.join(tokens))
        text = re.sub(r'^\%s '%self.chunk_delimiter, '', text)
        text = re.sub(r' \%s$'%self.chunk_delimiter, '', text)
        
        return text.split(' %s '%self.chunk_delimiter)
    
    def __vocabulary(self, texts):
        texts = [text.split() for text in texts]
        texts_flatten = np.hstack(texts)
        
        self.n_tokens = texts_flatten.shape[0]
        self.vocabulary = np.unique(texts_flatten).tolist()
        self.vocabulary_map = {token:index for index, token in enumerate(self.vocabulary)}
        
        return [[self.vocabulary_map[token] for token in text] for text in texts]
    
    def __phrase_frequency(self, texts):
        indices = [list(range(len(text))) for text in texts]
        counter = Counter(((token,) for token in np.hstack(texts)))
        
        n = 1
        while len(texts) > 0:
            for i, text in zip(range(len(texts)-1, -1, -1), reversed(texts)):
                indices[i] = [j for j in indices[i] if counter[tuple(text[j: j+n])] >= self.min_support]
                
                if len(indices[i]) == 0:
                    indices.pop(i)
                    texts.pop(i)
                    continue

                for j in indices[i]:
                    if j+1 in indices[i]:
                        counter.update([tuple(text[j: j+n+1])])
                indices[i].pop()
            n += 1
        return counter
    
    def __cost(self, a, b):
        ab = self.counter[tuple(np.hstack([a, b]))]
        if ab > 0: return (-(ab-(self.counter[a]*self.counter[b])/self.n_tokens)/math.sqrt(ab))
        else: return math.inf
        
    def __decoder(self, codes):
        return [' '.join([self.vocabulary[index] for index in code]) for code in codes]
    
    def __chunk_transform(self, chunk):
        code = []
        for token in chunk:
            if token in self.vocabulary_map: 
                code.append(self.vocabulary_map[token])
        
        phrases = [(index,) for index in code]
        phrase_start, phrase_end = np.arange(len(code)), np.arange(len(code))
        
        costs = [(self.__cost(phrases[i], phrases[i+1]), i, i+1, 2)
                for i in range(len(phrases)-1)]
        
        heapify(costs)
        while len(costs) > 0:
            cost, i_a, i_b, length = heappop(costs)
            if cost > -self.threshold:
                break
            if phrase_start[i_a] != i_a:
                continue
            if phrase_start[i_b] != i_b:
                continue
            if length != len(phrases[i_a]+phrases[i_b]):
                continue
            
            phrase_start[i_b] = i_a
            phrase_end[i_a] = phrase_end[i_b]
            merged_phrase = phrases[i_a]+phrases[i_b]
            phrases[i_a] = merged_phrase
            phrases[i_b] = None
            
            if i_a > 0:
                prev_phrase_start = phrase_start[i_a-1]
                prev_phrase = phrases[prev_phrase_start]
                if not(prev_phrase): continue
                heappush(costs, 
                         (self.__cost(prev_phrase, merged_phrase), 
                          prev_phrase_start, i_a, len(prev_phrase)+len(merged_phrase)))
            
            if phrase_end[i_b] < len(phrases)-1:
                next_phrase_start = phrase_end[i_b]+1
                next_phrase = phrases[next_phrase_start]
                if not(next_phrase): continue
                heappush(costs, (
                    self.__cost(merged_phrase, next_phrase),
                    i_a, next_phrase_start,
                    len(merged_phrase)+len(next_phrase)))

        code = [x for x in phrases if x is not None]
        return self.__decoder(code)
       
    def fit(self, texts):
        texts = np.hstack(map(lambda x: self.__predprocesser(x), texts))
        self.counter = self.__phrase_frequency(self.__vocabulary(texts))
        return self
        
    def transform(self, texts):
        if not(self.counter): return None 
        texts = map(lambda x: self.__predprocesser(x), texts)
        texts = [np.hstack([self.__chunk_transform(chunk.split()) for chunk in text]) for text in texts]
        return texts
    
    def fit_transform(self, texts):
        texts = [self.__predprocesser(text) for text in texts]
        self.counter = self.__phrase_frequency(self.__vocabulary(np.hstack(texts)))
        texts = [np.hstack([self.__chunk_transform(chunk.split()) for chunk in text]) for text in texts]
        return texts
