import sqlite3 as sql
import nltk
import math
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from collections import Counter
from os import path

from concept_extraction.tfidf_extractor import TfIdfExtractor


class ESA:
    def __init__(self, db_path='../esa_data/esa.db', filter_with_tfidf=False):
        # connect with sqlite db
        self.con = sql.connect(db_path)
        self.cursor = self.con.cursor()
        self.filter_with_tfidf = filter_with_tfidf

    def get_word_vector(self, word):
        # search for word and get corresponding vector rows from db
        self.cursor.execute('SELECT s.article_id, s.tf_idf FROM terms t, term_article_score s '
                            'WHERE t.term = "' + word + '" AND t.id = s.term_id ORDER BY s.article_id ASC;')
        vec = {}
        for row in self.cursor.fetchall():
            # article number and tf_idf  # todo switch to list mit len #articles?
            vec[row[0]] = row[1]
        return vec

    def get_text_vector_from_bow(self, text_bow):
        # text vector = sum of all word vectors
        text_vec = None

        # sorting words by number of occurrences (to get vector only once per word)
        counts = Counter([i for i in text_bow])
        unique_words = list({i: i for i in text_bow}.values())
        sorted_words = sorted(unique_words, key=lambda item: counts[item], reverse=True)
        all_words = [[item, counts[item]] for item in sorted_words]


        # all_words -> [0]: word; [1]: count
        for word_item in all_words:
            word = word_item[0]
            word_vec = self.get_word_vector(word)

            if word_item[1] > 1:
                # if word occurs more than once: vector multiplied by number of occurrences
                for key in word_vec:
                    word_vec[key] = word_vec[key] * word_item[1]

            if text_vec is None and len(word_vec) > 0:
                text_vec = word_vec
            elif len(word_vec) > 0:
                # word vector sorted/added into text vector
                text_vec = self.add_vectors(text_vec, word_vec)

        return text_vec

    def add_vectors(self, vec_one, vec_two):
        for key in vec_two:
            if key in vec_one:
                vec_one[key] += vec_two[key]
            else:
                vec_one[key] = vec_two[key]
        return vec_one

    def get_text_vector(self, text):
        if self.filter_with_tfidf:
            bow = text_to_most_important_tokens(text)
        else:
            bow = text_to_tokens(text)
        text_vec = self.get_text_vector_from_bow(bow)
        return text_vec

    def sparse_vector_dot(self, vector_one, vector_two):
        vec_mul_res = 0
        for key in vector_one:
            if key in vector_two:
                vec_mul_res += vector_one[key] * vector_two[key]
        return vec_mul_res

    def sparse_vector_dot_one_line(self, vector_one, vector_two):
        return sum(vector_two[key]*value for key, value in vector_one.items() if key in vector_two)

    def cos_of_vectors(self, vector_one, vector_two, word1_abs=None, word2_abs=None):
        vec_mul_res = self.sparse_vector_dot_one_line(vector_one, vector_two)

        if word1_abs is None:
            word1_abs = self.abs_val_of_vec(vector_one)
        if word2_abs is None:
            word2_abs = self.abs_val_of_vec(vector_two)

        cos = vec_mul_res / (word1_abs * word2_abs)
        return cos

    def abs_val_of_vec(self, vec):
        val = 0
        for key in vec:
            val += vec[key] * vec[key]
        val = math.sqrt(val)
        return val

    def similarity_of_words(self, word_one, word_two):
        vec_one = self.get_word_vector(word_one)
        vec_two = self.get_word_vector(word_two)

        cos = self.cos_of_vectors(vec_one, vec_two)
        return cos

    def similarity_of_texts(self, text_one, text_two):
        vec_one = self.get_text_vector(text_one)
        vec_two = self.get_text_vector(text_two)

        cos = self.cos_of_vectors(vec_one, vec_two)
        return cos

    def get_articles(self):
        self.cursor.execute('SELECT id, article FROM articles;')
        article_list = {}
        for row in self.cursor.fetchall():
            # article number and tf_idf  # todo switch to list mit len #articles?
            article_list[row[0]] = row[1]
        return article_list


def split_to_tokens_without_stopwords(text, lang):
    sw = set(stopwords.words(lang))
    t_tokens = nltk.word_tokenize(text, language=lang)
    t_tokens = [item.lower() for item in t_tokens if item not in sw and len(item) > 3 and not item.isdigit()]
    return t_tokens


def stem_tokens(t_tokens, lang):
    stemmer = SnowballStemmer(language=lang)
    t_tokens = [stemmer.stem(item) for item in t_tokens]
    return t_tokens


def text_to_tokens(text, lang="english"):
    t_tokens = split_to_tokens_without_stopwords(text, lang)
    t_tokens = stem_tokens(t_tokens, lang)
    return t_tokens


def text_to_most_important_tokens(text, lang="english", minimum_percentage=0.25, also_return_all_tokens=False):
    if not lang == "english":
        return 0
    t_tokens = split_to_tokens_without_stopwords(text, lang)

    tfidf_model_path = path.join(path.dirname(__file__), "../../concept_extraction/data", "tfidf_en.tfidf_model")
    tfidf = TfIdfExtractor(model_path=tfidf_model_path, tf_scaling="log")

    tfidf_result = tfidf.extract(t_tokens)
    tfidf_list = [[score, word, tf] for score, word, tf in
                  zip(tfidf_result['score'], tfidf_result['word'], tfidf_result['tf'])]

    tokens = []
    minimum = tfidf_list[0][0] * minimum_percentage
    # print("minimum percentage: " + str(minimum_percentage))
    # print("minimum tf-idf value: " + str(minimum))
    for tf_elem in tfidf_list:
        if tf_elem[0] >= minimum:
            for i in range(tf_elem[2]):
                tokens.append(tf_elem[1])

    t_tokens = stem_tokens(tokens, lang)
    # print("number of tokens: " + str(len(t_tokens)))
    if also_return_all_tokens:
        return t_tokens, tokens
    else:
        return t_tokens

