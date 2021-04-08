import pandas as pd
from os import path, mkdir
import time

from analysis.research_areas_esa import ResearchAreasESA
from esa.analysis import analyse

# analysis of zooniverse project; input as excel table including ProjectName and About text
origin_filepath = input("Enter filepath for excel (press 'enter' to show example, enter 'X' to stop programm): ")
example_path = "esa_data/projects_example.xls"
dbpedia = int(input("Research Areas found with DBPedia sepearately (0) or integrated (1)?: "))

if origin_filepath == "":
    origin_filepath = example_path

cutoff_in_relation_to_max = 0.75
research_areas_esa = ResearchAreasESA("esa_data/esa.db", cutoff_in_relation_to_max=cutoff_in_relation_to_max,
                                      tfidf_proportion=0.2)
research_areas_esa.get_research_areas()
research_areas_esa.get_research_area_vectors()

while not origin_filepath == "" and not origin_filepath == 'X' and (dbpedia == 0 or dbpedia == 1):

    zooniverse = pd.read_excel(origin_filepath, usecols=['ProjectName', 'About']).values.tolist()
    zooniverse_short = []
    for z in zooniverse:
        if not z in zooniverse_short:
            zooniverse_short.append(z)

    addendum = "results"
    result_filepath = origin_filepath.rsplit(".", 1)[0] + "_" + addendum + ".csv"
    if path.exists(result_filepath):
        zooniverse_results = pd.read_csv(result_filepath, usecols=["ProjectName", "Categories", "Topics",
                                                                   "Topics with Similarity", "DBPedia Topics",
                                                                   "Time"]).values.tolist()
    else:
        zooniverse_results = []

    done = len(zooniverse_results)

    counter = 1
    all_z = len(zooniverse_short)

    for project in zooniverse_short:
        start_time = time.time()
        name = project[0]
        text = project[1]

        if counter > done:
            if isinstance(text, str):
                text = name + " " + text
                print("\n\n## " + str(counter) + "/" + str(all_z) + " ## " + name + ":\n" + text.replace("\n", " "))
                """
                change use_old_version to True to switch to the list version, 
                add sort=False to get list ordered alphabetically
                """
                if dbpedia == 0:
                    esa_research_areas_sim, esa_research_areas, categories_with_count, top_category, db_research_areas, bow \
                        = analyse.get_research_areas_esa_with_dbpedia(text, research_areas_esa=research_areas_esa)
                else:
                    esa_research_areas_sim, res_areas_with_sim_list, categories_with_count, top_category, \
                        db_research_areas, unique_words = analyse.get_research_areas_esa_with_dbpedia_integrated\
                        (text, research_areas_esa=research_areas_esa, cutoff_in_rel_to_max=cutoff_in_relation_to_max)
                    db_research_areas = "integrated"

                categories = [c[0] for c in categories_with_count]

                print("\n## RESULT " + name + "  ##")
                print(esa_research_areas_sim)
                print(db_research_areas)
                print(categories)
            else:
                print("\n\n## " + str(counter) + "/" + str(all_z) + " ## " + name + ":")
                print("\n## kein TEXT ##")
                esa_research_areas = categories = esa_research_areas_sim = db_research_areas= ""

            time_needed = str(time.time() - start_time)
            item = [name, categories, esa_research_areas_sim, db_research_areas, time_needed]
            zooniverse_results.append(item)

            # save result #
            sim_pd = pd.DataFrame(zooniverse_results,
                                  columns=["ProjectName", "Categories", "Topics with Similarity",
                                           "DBPedia Topics", "Time"])
            sim_pd.to_csv(result_filepath)

        counter += 1

    print("\n## DONE ##\n")
    print("Saved result in: " + result_filepath)
    origin_filepath = input("Enter filepath for excel (press 'enter' to show example, enter 'X' to stop programm): ")
    if origin_filepath == "":
        origin_filepath = example_path
    dbpedia = int("1")
