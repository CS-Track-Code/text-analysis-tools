import requests
import time
import pandas as pd
from collections import Counter


class DBPediaExtractor:

    def __init__(self, *, confidence, lang, chunk_size=100, percent_second_rank=0.01):
        self.confidence = confidence
        self.lang = lang
        self.chunk_size = chunk_size
        self.percent_second_rank = percent_second_rank

    def extract(self, word_token_list):
        url = "https://api.dbpedia-spotlight.org/{}/annotate".format(self.lang)
        headers = {
            "accept": "application/json"
        }
        resources = []
        word_token_listen = [item.lower() for item in word_token_list]
        n_tokens = len(word_token_listen)
        for chunk in chunks(word_token_list, self.chunk_size):
            time.sleep(0.5)
            text = " ".join(chunk)
            params = {
                "text": text,
                "confidence": self.confidence,
            }

            # print("Text:")
            # print(text)
            for i in range(3):
                response = requests.get(url, params=params, headers=headers)
                # print("RESPONSE: ")
                # print(response.text)
                # print(response.status_code)
                if response.status_code == requests.codes.ok:
                    annotation = response.json()
                    # print(annotation)
                    if "Resources" in annotation:
                        chunk_resources = annotation["Resources"]
                        # filter for percent of second rank, if second rank high, probably badly matched
                        chunk_resources = [item for item in chunk_resources if
                                           float(item["@percentageOfSecondRank"]) <= self.percent_second_rank]
                        words = [item["@URI"].split("/")[-1] for item in chunk_resources]
                        data = []
                        for i2, word in enumerate(words):
                            api_data = chunk_resources[i2]
                            concept_data = {
                                "word": word,
                                "uri": api_data["@URI"],
                                "surface_form": api_data["@surfaceForm"],
                                "types": api_data["@types"],
                                "similarity_score": api_data["@similarityScore"]
                            }
                            concept_data = HashDict(concept_data)
                            data.append(concept_data)
                        resources.extend(data)
                        break
                else:
                    time.sleep(0.3)
        count = Counter(resources)
        dedup_resources = []
        for k, v in count.items():
            k["tf"] = v
            dedup_resources.append(k)
        # resources.sort(key=lambda x: x["similarity_score"], reverse=True)
        dedup_resources.sort(key=lambda x: x["tf"], reverse=True)
        result_df = pd.DataFrame(dedup_resources,
                                 columns=["uri", "similarity_score", "surface_form", "types", "tf", "word"])
        return result_df


def chunks(l, n):
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i + n]


# From https://stackoverflow.com/questions/1151658/python-hashable-dicts/1151686
class HashDict(dict):
    """
    hashable dict implementation, suitable for use as a key into
    other dicts.

        >>> h1 = HashDict({"apples": 1, "bananas":2})
        >>> h2 = HashDict({"bananas": 3, "mangoes": 5})
        >>> h1+h2
        hashdict(apples=1, bananas=3, mangoes=5)
        >>> d1 = {}
        >>> d1[h1] = "salad"
        >>> d1[h1]
        'salad'
        >>> d1[h2]
        Traceback (most recent call last):
        ...
        KeyError: hashdict(bananas=3, mangoes=5)

    based on answers from
       http://stackoverflow.com/questions/1151658/python-hashable-dicts

    """
    def __key(self):
        return tuple(sorted(self.items()))
    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__,
            ", ".join("{0}={1}".format(
                    str(i[0]),repr(i[1])) for i in self.__key()))

    def __hash__(self):
        return hash(self.__key())

    # update is not ok because it mutates the object
    # __add__ is ok because it creates a new object
    # while the new object is under construction, it's ok to mutate it
    def __add__(self, right):
        result = HashDict(self)
        dict.update(result, right)
        return result

if __name__ == "__main__":
    import doctest
    doctest.testmod()