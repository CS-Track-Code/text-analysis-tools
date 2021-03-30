from collections import Counter
import numpy as np
import mysql.connector
import time

import esa.analysis.esa as esa_class
from esa.analysis.esa import ESA

import esa.config as config


class ResearchAreasESA:
    def __init__(self, esa_db_path, research_areas=None, research_area_wikis=None, research_area_vectors=None,
                 cutoff_in_relation_to_max=0.75, top=None, sort=True, tfidf_proportion=0.2, esa=None):
        if esa is None:
            self.esa = ESA(esa_db_path)
        else:
            self.esa = esa
        self.ra_con = mysql.connector.connect(
            host=config.host,
            user=config.user,
            password=config.password,
            database=config.database
        )

        self.mycursor = self.ra_con.cursor()
        self.research_areas = research_areas
        self.research_area_wikis = research_area_wikis
        self.research_area_vectors = research_area_vectors
        self.article_list = None

        self.mycursor.execute("SHOW TABLES")

        tables = []
        for x in self.mycursor:
            tables.append(x[0])

        if 'absolute_value' not in tables:
            self.mycursor.execute('CREATE TABLE IF NOT EXISTS absolute_value (area_id INTEGER NOT NULL PRIMARY KEY, '
                                  'abs_val REAL NOT NULL)')

        self.cutoff_in_relation_to_max = cutoff_in_relation_to_max
        self.top = top
        self.sort = sort
        self.tfidf_proportion = tfidf_proportion

    def edit_cutoff(self, cutoff_in_relation_to_max):
        self.cutoff_in_relation_to_max = cutoff_in_relation_to_max

    def edit_top(self, top):
        self.top = top

    def edit_sort(self, sort):
        self.sort = sort

    def edit_tfidf(self, tfidf_proportion):
        self.tfidf_proportion = tfidf_proportion

    def edit_esa(self, esa):
        self.esa = esa

    def get_research_areas(self, min_row_id=0):
        if self.research_areas is None:
            start_time = time.time()
            self.mycursor.execute('SELECT id, wos_category, wos_topic FROM research_areas;')
            self.research_areas = []
            for row in self.mycursor.fetchall():
                self.research_areas.append([row[0], row[1], row[2]])
            print("~~ got research areas in: " + str(time.time() - start_time))
        return self.research_areas[min_row_id:]

    def get_research_area_vectors(self):
        start_time = time.time()
        self.research_area_vectors = {}
        for area in self.get_research_areas():
            area_id = area[0]
            self.mycursor.execute(
                'SELECT article_id, tf_idf FROM research_areas_vec WHERE area_id = ' + str(area_id) + ';')

            vec = {}
            for pair in self.mycursor.fetchall():
                vec[pair[0]] = pair[1]
            self.research_area_vectors[area_id] = vec
        print("~~ got research area vecs in: " + str(time.time() - start_time))
        return self.research_area_vectors

    def get_research_area_wikis(self, min_row_id=0):
        if self.research_area_wikis is None:
            start_time = time.time()
            self.mycursor.execute('SELECT id, wos_category, wos_topic, wiki_name FROM research_areas_wiki;')
            self.research_area_wikis = []
            for row in self.mycursor.fetchall():
                self.research_area_wikis.append([row[0], row[1], row[2], row[3]])
            print("~~ got research area wikis in: " + str(time.time() - start_time))
        return self.research_area_wikis[min_row_id:]

    def get_research_area_similarities_from_text(self, text):
        start_time = time.time()
        if not self.tfidf_proportion == 0:
            bow, tokens = esa_class.text_to_most_important_tokens(text, minimum_percentage=self.tfidf_proportion,
                                                                  also_return_all_tokens=True)
            text_vec = self.esa.get_text_vector_from_bow(bow)
        else:
            text_vec = self.esa.get_text_vector(text)
            tokens = ""
        text_vec_abs_val = self.esa.abs_val_of_vec(text_vec)
        print("~~ got text vector in " + str(time.time() - start_time))

        research_areas_with_sim, res_areas, categories, top_category = \
            self.get_research_area_similarities_from_vec(text_vec, text_vec_abs_val)

        return research_areas_with_sim, res_areas, categories, top_category, tokens

    def get_research_area_similarities_from_vec(self, text_vec, text_vec_abs_val, min_row_id_of_ra=0):
        research_areas_similarity = []
        i = 0
        max_sim = 0

        if self.research_area_vectors is None:
            print("how'd i get here?")
            self.get_research_area_vectors()

        print("calculating similarities")
        for row in self.get_research_areas(min_row_id_of_ra):
            i += 1
            area_id = row[0]
            res_area_category = row[1]
            res_area_topic = row[2]

            vec = self.research_area_vectors[area_id]

            res_area_vec_abs_val = self.get_abs_value_of_ra_vec(row[0], vec)

            # get similarity between text and research area
            sim = self.esa.cos_of_vectors(text_vec, vec, text_vec_abs_val, res_area_vec_abs_val)
            if sim > max_sim:
                max_sim = sim

            research_areas_similarity.append([res_area_category, res_area_topic, sim])

        if self.cutoff_in_relation_to_max is not None:
            cutoff = max_sim * self.cutoff_in_relation_to_max
            research_areas_similarity = [ras for ras in research_areas_similarity if ras[2] > cutoff]

        categories = [ras[0] for ras in research_areas_similarity]

        # sort categories by count
        counts = Counter([i for i in categories])
        unique_categories = list({i: i for i in categories}.values())
        sorted_categories = sorted(unique_categories, key=lambda item: counts[item], reverse=True)
        categories = [[item, counts[item]] for item in sorted_categories]
        if len(categories) > 0:
            top_category = categories[0][0]
        else:
            top_category = ""

        print("sorting")
        if self.sort:
            sorted_research_areas = sorted(research_areas_similarity, key=lambda x: x[2], reverse=True)
            if self.top is not None:
                sorted_research_areas = sorted_research_areas[:self.top]

            res_areas = [ra[1] for ra in sorted_research_areas]

            return sorted_research_areas, res_areas, categories, top_category
        else:
            res_areas = [ra[1] for ra in research_areas_similarity]
            return research_areas_similarity, res_areas, categories, top_category

    def get_abs_value_of_ra_vec(self, ra_id, vec):
        self.mycursor.execute('SELECT abs_val FROM absolute_value WHERE area_id = ' + str(ra_id) + ';')
        value_row = self.mycursor.fetchone()
        if value_row is None:
            res_area_vec_abs_val = self.esa.abs_val_of_vec(vec)
            self.mycursor.execute('INSERT into absolute_value (area_id, abs_val) VALUES (' + str(ra_id) + ',' +
                                  str(res_area_vec_abs_val) + ');')
            self.ra_con.commit()
        else:
            res_area_vec_abs_val = value_row[0]
        if res_area_vec_abs_val == 0:
            res_area = [line for line in self.get_research_areas() if line[0] == ra_id]
            print("The absolute value of the research area '" + res_area[0][2] +
                  "' is 0. This likely means that something went wrong in preprocessing the research areas. "
                  "If this happened for multiple research areas you should try to rerun preprocessing. "
                  "(For this you will have to first delete the database 'esa_research_areas' manually)")
        return res_area_vec_abs_val

    def get_research_area_sim_matrix(self):
        research_areas = self.get_research_areas()
        ra_index = {}
        ra_matrix = np.zeros(shape=(len(research_areas), len(research_areas)))

        counter = 0

        for id, category, topic in research_areas:
            ra_index[counter] = topic
            ra_index[topic] = counter
            counter += 1

        if self.research_area_vectors is None:
            self.get_research_area_vectors()

        done = 0
        for row in research_areas:
            area_id = row[0]
            res_area_topic = row[2]
            current_area_matrixid = ra_index[res_area_topic]

            vec = self.research_area_vectors[area_id]

            res_area_vec_abs_val = self.get_abs_value_of_ra_vec(row[0], vec)

            ra_matrix[current_area_matrixid, current_area_matrixid] = 1

            if len(research_areas) >= done+1:
                store_sort = self.sort
                self.sort = False
                research_areas_similarity, res_areas, categories, top_category = \
                    self.get_research_area_similarities_from_vec(vec, res_area_vec_abs_val, min_row_id_of_ra=done+1)
                self.sort = store_sort

                for category, topic, sim in research_areas_similarity:
                    second_area_matrix_id = ra_index[topic]
                    ra_matrix[current_area_matrixid, second_area_matrix_id] = sim
                    ra_matrix[second_area_matrix_id, current_area_matrixid] = sim
            done += 1

            print(str(done) + ": " + res_area_topic)
            line = str([str(r) + "\t" for r in ra_matrix[done-1:done, :]])
            print(line.replace("\n", ""))

        return ra_matrix, ra_index

    def get_research_areas_with_dbp(self, text, db_results):
        db_research_areas = []

        wiki_res_area = {}
        for ra in self.get_research_area_wikis():
            research_area = ra[2]
            wiki = ra[3]
            if wiki in wiki_res_area:
                wiki_res_area[wiki].append(research_area)
            else:
                wiki_res_area[wiki] = [research_area]

        for db_res in db_results:
            if db_res in wiki_res_area:
                for entry in wiki_res_area[db_res]:
                    db_research_areas.append(entry)

        research_areas_with_sim, res_areas, categories, top_category, tokens = \
            self.get_research_area_similarities_from_text(text)

        return research_areas_with_sim, res_areas, categories, top_category, db_research_areas, tokens



