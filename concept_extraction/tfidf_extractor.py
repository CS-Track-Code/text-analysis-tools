import gensim as gs
import pandas as pd
from math import log
from collections import Counter


class TfIdfExtractor:

    def __init__(self, *, model_path, threshold=0, tf_scaling="relative"):
        """
        Extracts tf_idf for a list of word tokens
        :param model_path: Gensim TFIDF File Path
        :type model_path:
        :param threshold: Filter out tokens below this threshold
        :type threshold:
        :param tf_scaling: How to scale term frequency.
        Possible values are "none" , "relative", "binary", "log", "relative_log"
        relative scales the value through the size of the text.
        :type tf_scaling:
        """
        self.model_path = model_path
        self.threshold = threshold
        self.model = gs.models.TfidfModel.load(str(model_path))

        self.tf_scaling = tf_scaling

    def extract(self, word_token_list):
        """
        Extracts tf_idf for a given word token list
        :param word_token_list: List of word tokens
        :type word_token_list:
        :return: Pandas dataframe containing the columns
        ["tf", "tf_scaled", "idf", "score", "word"]
        :rtype: pd.Dataframe
        """
        word_token_list = [item.lower() for item in word_token_list]
        n_tokens = len(word_token_list)
        counter = Counter(word_token_list)
        resources = []
        for token, times in counter.items():
            tf_scaled = self.scaled_tf(times, n_tokens)
            transformed_tf = tf_scaled
            score = self.token_idf(token) * transformed_tf
            if score >= self.threshold:
                concept_data = {
                    "tf": times,
                    "tf_scaled": tf_scaled,
                    "idf": self.token_idf(token),
                    "score": score,
                    "word": token,
                }
                resources.append(concept_data)
        resources.sort(key=lambda x: x["score"], reverse=True)
        print(resources)
        result_df = pd.DataFrame(resources, columns=["tf", "tf_scaled", "idf", "score", "word"])
        return result_df

    def token_idf(self, token):
        """
        Get idf for token from Gensim Model.
        Returns 0 if token not in model
        :param token:
        :type token:
        :return:
        :rtype:
        """
        try:
            token_id = self.model.id2word.token2id[token]
            token_idf = self.model.idfs[token_id]
            return token_idf
        except Exception as e:
            return 0

    def scaled_tf(self, tf, n_tokens):
        """
        Returns a scaled version of tf based on the chosen scaling
        :param tf:
        :type tf:
        :param n_tokens:
        :type n_tokens:
        :return:
        :rtype:
        """
        if self.tf_scaling == "relative":
            return tf / n_tokens
        if self.tf_scaling == "none":
            return tf
        if self.tf_scaling == "binary":
            if tf == 0:
                return 0
            else:
                return 1
        if self.tf_scaling == "log":
            return log(tf+1, 2)
        if self.tf_scaling == "relative_log":
            return 1 / abs(tf / n_tokens)
