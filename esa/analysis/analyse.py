from collections import Counter

from concept_extraction.dbpedia import keyword_extraction_dbpedia, keywords_plain_dbpedia
from esa.analysis.research_areas_esa import ResearchAreasESA


def setup_research_area(research_areas_esa, edits, top, cutoff_in_relation_to_max, sort, tfidf_proportion):
    """

    :param research_areas_esa: object research_areas_esa (can be reused to not reload research areas every time)
    :param edits: boolean; True if changes for configuration were made
    :param top: int or None; if not None sort has to be True;
    absolute cutoff for matched research areas (return x first research areas)
    :param cutoff_in_relation_to_max: float (0 < x < 1); sets cutoff in relation to the maximal cutoff
    :param sort: boolean; True if research areas should be sorted by similarity (should be True if top is not None)
    :param tfidf_proportion: float (0 < x < 1); in relation to the highest tfidf score in the text
    how high has a words score to be for the word to be used in the esa calculation
    (used to only include high value words and to reduce calculation time by cutting out low value words)
    :return: research_areas_esa object with given configuration
    """
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
    """

    :param text:
    :param research_areas_esa: object research_areas_esa (can be reused to not reload research areas every time)
    :param edits: boolean; True if changes for configuration were made
    (if False and research_areas_esa is given: top, cutoff_in_relation_to_max, sort and tfidf_proportion don't have to be set!)
    :param top: int or None; if not None sort has to be True;
    absolute cutoff for matched research areas (return x first research areas)
    :param cutoff_in_relation_to_max: float (0 < x < 1); sets cutoff in relation to the maximal cutoff
    :param sort: boolean; True if research areas should be sorted by similarity (should be True if top is not None)
    :param tfidf_proportion: float (0 < x < 1); in relation to the highest tfidf score in the text
    how high has a words score to be for the word to be used in the esa calculation
    (used to only include high value words and to reduce calculation time by cutting out low value words)
    :return: res_areas_with_sim_list (list of matched research areas, each with category, research area, similarity),
    res_areas (list of matched research areas only),
    categories_with_count (counted how many research areas per category were matched),
    top_category (category with most matched research areas),
    bow (used bag of words for esa)
    """
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

    :param text:
    :param research_areas_esa: object research_areas_esa (can be reused to not reload research areas every time)
    :param edits: boolean; True if changes for configuration were made
    (if False and research_areas_esa is given: top, cutoff_in_relation_to_max, sort and tfidf_proportion don't have to be set!)
    :param top: int or None; if not None sort has to be True;
    absolute cutoff for matched research areas (return x first research areas)
    :param cutoff_in_relation_to_max: float (0 < x < 1); sets cutoff in relation to the maximal cutoff
    :param sort: boolean; True if research areas should be sorted by similarity (should be True if top is not None)
    :param tfidf_proportion: float (0 < x < 1); in relation to the highest tfidf score in the text
    how high has a words score to be for the word to be used in the esa calculation
    (used to only include high value words and to reduce calculation time by cutting out low value words)
    :return: res_areas_with_sim_list (list of matched research areas, each with category, research area, similarity),
    res_areas (list of matched research areas only),
    categories_with_count (counted how many research areas per category were matched),
    top_category (category with most matched research areas),
    db_research_areas (research areas that match found dbpedia keywords),
    bow (used bag of words for esa)
    """
    research_areas_esa = setup_research_area(research_areas_esa, edits, top, cutoff_in_relation_to_max, sort,
                                             tfidf_proportion)

    db_list = keyword_extraction_dbpedia(text, "en")
    db_keywords = keywords_plain_dbpedia(db_list)

    res_areas_with_sim_list, res_areas, categories_with_count, top_category, db_research_areas, bow = \
        research_areas_esa.get_research_areas_with_dbp(text, db_keywords)

    return res_areas_with_sim_list, res_areas, categories_with_count, top_category, db_research_areas, bow


def get_research_areas_esa_with_dbpedia_integrated(text, research_areas_esa, cutoff_in_rel_to_max=0.75):
    """
    method made specifically for workbench application, returns the complete list of all research areas additionally
    to the shortened list (using the cutoff). Used to give users the option to modify the results.
    And sorts db results in shortened result list

    assumes that configuration is already set, cutoff_in_relation_to_max is required because it is set to None to get
    all research areas and then perform the cutoff here to return both lists
    :param text:
    :param research_areas_esa: object research_areas_esa (can be reused to not reload research areas every time)
    :param cutoff_in_relation_to_max: float (0 < x < 1); sets cutoff in relation to the maximal cutoff
    :return:
    research_areas_similarity_shortlist (list of matched research areas, each with category, research area, similarity),
    res_areas_with_sim_list (list of ALL research areas, each with category, research area, similarity),
    categories_with_count(counted how many research areas per category were matched),
    top_category, (category with most matched research areas),
    db_research_areas (research areas that match found dbpedia keywords),
    unique_words (used bag of words for esa)
    """

    research_areas_esa.edit_cutoff(cutoff_in_relation_to_max=None)

    res_areas_with_sim_list, res_areas, categories_with_count, top_category, db_research_areas, tokens = \
        get_research_areas_esa_with_dbpedia(text, research_areas_esa=research_areas_esa)

    counts = Counter([i for i in tokens])
    unique_words = list({i: i for i in tokens}.values())

    max_sim = res_areas_with_sim_list[0][2]

    cutoff = max_sim * cutoff_in_rel_to_max
    research_areas_similarity_shortlist = [ras for ras in res_areas_with_sim_list if ras[2] > cutoff]

    categories = [ras[0] for ras in research_areas_similarity_shortlist]

    # sort categories by count
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
