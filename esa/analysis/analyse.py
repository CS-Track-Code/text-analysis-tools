from polyglot.text import Text
from collections import Counter

from concept_extraction.dbpedia_extractor import DBPediaExtractor
from esa.analysis.research_areas_esa import ResearchAreasESA


def keyword_extraction_dbpedia(text, lang):
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
    # returns one-dimensional list -> only keywords
    db_keywords = [word[0] for word in dbpedia_list]
    return db_keywords


def setup_research_area(research_areas_esa, edits, top, cutoff_in_relation_to_max, sort, tfidf_proportion):
    if research_areas_esa is None:
        research_areas_esa = ResearchAreasESA("esa_data/esa.db", cutoff_in_relation_to_max=cutoff_in_relation_to_max,
                                              sort=sort, tfidf_proportion=tfidf_proportion, top=None)
    elif edits:
        research_areas_esa.edit_cutoff(cutoff_in_relation_to_max)
        research_areas_esa.edit_sort(sort)
        research_areas_esa.edit_tfidf(tfidf_proportion)
        research_areas_esa.edit_top(top)

    return research_areas_esa


def get_research_areas_esa(text, research_areas_esa=None, edits=False, top=None, cutoff_in_relation_to_max=None,
                           sort=True, tfidf_proportion=0.2):
    research_areas_esa = setup_research_area(research_areas_esa, edits, top, cutoff_in_relation_to_max, sort,
                                             tfidf_proportion)

    res_areas_with_sim_list, res_areas, categories_with_count, top_category, bow = \
        research_areas_esa.get_research_area_similarities_from_text(text)
    print("-- RESEARCH AREAS:")
    print(res_areas)

    return res_areas_with_sim_list, res_areas, categories_with_count, top_category, bow


def get_research_areas_esa_with_dbpedia(text, research_areas_esa=None, edits=False, top=None,
                                        cutoff_in_relation_to_max=None, sort=True, tfidf_proportion=0.25):
    """
    top: cutoff -> top X research areas
    """
    research_areas_esa = setup_research_area(research_areas_esa, edits, top, cutoff_in_relation_to_max, sort,
                                             tfidf_proportion)

    db_list = keyword_extraction_dbpedia(text, "en")
    db_keywords = keywords_plain_dbpedia(db_list)

    res_areas_with_sim_list, res_areas, categories_with_count, top_category, db_research_areas, bow = \
        research_areas_esa.get_research_areas_with_dbp(text, db_keywords)

    return res_areas_with_sim_list, res_areas, categories_with_count, top_category, db_research_areas, bow


def get_research_areas_esa_with_dbpedia_integrated(text, research_areas_esa, cutoff_in_rel_to_max=0.75):
    # method made specifically for workbench application, returns the complete list of all research areas additionally
    # to the shortened list (using the cutoff). Used to give users the option to modify the results.
    # And sorts db results in shortened result list

    research_areas_esa.edit_cutoff(cutoff_in_relation_to_max=None)

    res_areas_with_sim_list, res_areas, categories_with_count, top_category, db_research_areas, tokens = \
        get_research_areas_esa_with_dbpedia(text, research_areas_esa=research_areas_esa)

    counts = Counter([i for i in tokens])
    unique_words = list({i: i for i in tokens}.values())

    max_sim = res_areas_with_sim_list[0][2]

    cutoff = max_sim * cutoff_in_rel_to_max
    research_areas_similarity_shortlist = [ras for ras in res_areas_with_sim_list if ras[2] > cutoff]

    categories = [ras[0] for ras in research_areas_similarity_shortlist]

    # sort categories by count #todo: sinnvoll bei verschieden vielen topics je category?
    counts = Counter([i for i in categories])
    unique_categories = list({i: i for i in categories}.values())
    sorted_categories = sorted(unique_categories, key=lambda item: counts[item], reverse=True)
    categories_with_count = [[item, counts[item]] for item in sorted_categories]
    if len(categories_with_count) > 0:
        top_category = categories_with_count[0][0]
    else:
        top_category = ""

    db_results_throwaway = [d for d in db_research_areas]
    for ra in research_areas_similarity_shortlist:
        if ra[1] in db_results_throwaway:
            db_results_throwaway.remove(ra[1])

    add_ras = [ra for ra in res_areas_with_sim_list if ra[1] in db_results_throwaway]

    for ra in add_ras:
        research_areas_similarity_shortlist.append(ra)

    return research_areas_similarity_shortlist, res_areas_with_sim_list, categories_with_count, top_category, \
           db_research_areas, unique_words
