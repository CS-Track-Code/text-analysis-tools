import pandas as pd
from os import path, mkdir
import time

from analysis.research_areas_esa import ResearchAreasESA
from esa.analysis import analyse

# analysis of zooniverse project; input as excel table including ProjectName and About text
origin_filepath = input("Enter filepath for excel (press 'enter' to end program): ")
dbpedia = int("1")

while not origin_filepath == "" and (dbpedia == 0 or dbpedia == 1):
    research_areas_esa = ResearchAreasESA("esa_data/esa.db", cutoff_in_relation_to_max=0.75, tfidf_proportion=0.2)
    fp_fn_cols = ["RA", "FP (Both)", "FN (Only Project)", "FN (Only RA)"]

    zooniverse = pd.read_excel(origin_filepath, usecols=['ProjectName', 'About']).values.tolist()
    zooniverse_short = []
    for z in zooniverse:
        if not z in zooniverse_short:
            zooniverse_short.append(z)

    addendum = "results"
    result_filepath = origin_filepath.rsplit(".", 1)[0] + "_" + addendum + ".csv"
    fp_fn_filepath = origin_filepath.rsplit("/", 1)[0] + "/FN-FP/"
    if not path.exists(fp_fn_filepath):
        mkdir(fp_fn_filepath)
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
                    esa_research_areas_sim, esa_research_areas, categories_with_count, top_category = \
                        analyse.get_research_areas_esa(text, research_areas_esa=research_areas_esa)
                    db_research_areas = []
                else:
                    esa_research_areas_sim, esa_research_areas, categories_with_count, top_category, db_research_areas \
                        = analyse.get_research_areas_esa_with_dbpedia(text, research_areas_esa=research_areas_esa)

                categories = [c[0] for c in categories_with_count]

                print("\n## RESULT " + name + "  ##")
                print(esa_research_areas)
                print(db_research_areas)
                print(categories)
            else:
                print("\n\n## " + str(counter) + "/" + str(all_z) + " ## " + name + ":")
                print("\n## kein TEXT ##")
                esa_research_areas = categories = esa_research_areas_sim = db_research_areas= ""

            time_needed = str(time.time() - start_time)
            item = [name, categories, esa_research_areas, esa_research_areas_sim, db_research_areas, time_needed]
            zooniverse_results.append(item)

            # save result #
            sim_pd = pd.DataFrame(zooniverse_results,
                                  columns=["ProjectName", "Categories", "Topics", "Topics with Similarity",
                                           "DBPedia Topics", "Time"])
            sim_pd.to_csv(result_filepath)

        counter += 1

    print("\n## DONE ##\n")
    origin_filepath = input("Enter filepath (press 'enter' to end program): ")
    dbpedia = int("1")
