from polyglot.text import Text

from concept_extraction.dbpedia_extractor import DBPediaExtractor


def keyword_extraction_dbpedia(text, lang):
    """
    to extract keywords using dbpedia
    :param text: input text (string)
    :param lang: language of text (string)
    shortened to two letters ("en" for english, "de" for german), limited by the languages dbpedia supports
    :return: list of dbpedia results, per result a list with word, tf, surface_form, types
    """
    dbpedia_ex = DBPediaExtractor(confidence=0.5, lang=lang, chunk_size=300)
    tokenized_words = Text(text).tokens
    token_list = []
    for i, token in enumerate(tokenized_words):
        item = {
            "word": token
        }
        token_list.append(item)
    token_list = [item for item in token_list if item["word"] != "."]

    word_tokenlist = [item["word"] for item in token_list]

    db_result = dbpedia_ex.extract(word_tokenlist)
    dbpedia_list = [[word, tf, surface_form, types] for word, tf, surface_form, types in
                    zip(db_result['word'], db_result['tf'],
                        db_result['surface_form'], db_result['types'])]

    dbpedia_list_unique = []
    for item in dbpedia_list:
        item_not_in_unique_list = True
        for unique_item in dbpedia_list_unique:
            if item[0] == unique_item[0]:
                unique_item[1] = unique_item[1] + item[1]
                item_not_in_unique_list = False
        if item_not_in_unique_list:
            dbpedia_list_unique.append(item)

    sorted_dbpedia_list = sorted(dbpedia_list_unique, key=lambda item: item[1], reverse=True)

    del dbpedia_ex

    # sorted_dbpedia_list -> [word, tf, surface_form, types]
    return sorted_dbpedia_list


def keywords_plain_dbpedia(dbpedia_list):
    """

    :param dbpedia_list: output list from keyword_extraction_dbpedia(..)
    :return: filtered one-dimensional list containing only the found dbpedia words
    """
    db_keywords = [word[0] for word in dbpedia_list]
    return db_keywords