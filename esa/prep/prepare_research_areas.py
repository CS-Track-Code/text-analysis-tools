import pandas as pd
import copy
import mysql.connector
import nltk

from esa.analysis import esa as esa
from esa.analysis.esa import ESA
from web_text_extraction import mercury_web_parser as Mercury
import esa.config as config


def init():

    nltk.download('stopwords')
    nltk.download('punkt')

    try:
        mydb = mysql.connector.connect(
            host=config.host,
            user=config.user,
            password=config.password,
            database=config.database
        )

        mycursor = mydb.cursor()
        print("connected")

    except mysql.connector.errors.ProgrammingError:
        mydb = mysql.connector.connect(
            host=config.host,
            user=config.user,
            password=config.password
        )

        mycursor = mydb.cursor(buffered=True)

        mycursor.execute("CREATE DATABASE " + config.database)
        print("created")

    mycursor.execute("SHOW TABLES")

    tables = []
    for x in mycursor:
        tables.append(x[0])
        print(x[0])

    if 'research_areas' not in tables:
        mycursor.execute(
            "CREATE TABLE research_areas (id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY, wos_category TEXT NOT NULL, wos_topic TEXT NOT NULL)")
    if 'research_areas_vec' not in tables:
        mycursor.execute(
            "CREATE TABLE research_areas_vec (area_id INTEGER NOT NULL, article_id INTEGER NOT NULL, tf_idf REAL NOT NULL, PRIMARY KEY(area_id, article_id))")
    if 'research_areas_wiki' not in tables:
        mycursor.execute(
            "CREATE TABLE research_areas_wiki (id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY, wos_category TEXT NOT NULL, wos_topic TEXT NOT NULL, wiki_name TEXT NOT NULL)")
    if 'research_areas_vec' not in tables:
        mycursor.execute(
            "CREATE TABLE research_areas_wiki_vec (area_id INTEGER NOT NULL, article_id INTEGER NOT NULL, tf_idf REAL NOT NULL, PRIMARY KEY(area_id, article_id))")

    return mydb, mycursor


mydb, mycursor = init()

api_endpoint = "http://localhost:8888/myapp/"

data_dir = "../esa_data/"

esa_db = ESA(data_dir + "esa.db")

# use prepared list of research areas (includes: category, topic, wikipedia page name, wikipedia link)
research_areas = pd.read_csv(data_dir+"research_areas.csv", header=None, encoding='utf8', delimiter=";")
research_areas = research_areas.values.tolist()

last_category = ""
last_topic = ""
topic_vec = []

for area in research_areas:
    wos_category = area[0]
    wos_topic = area[1]
    wiki_name = area[2]
    wiki_link = area[3]

    # research area topic only processed if not saved yet
    mycursor.execute('SELECT id FROM research_areas WHERE wos_topic = "' + wos_topic + '";')
    if mycursor.fetchone() is None:
        # check if wiki text in db
        mycursor.execute('SELECT id FROM research_areas_wiki WHERE wiki_name = "' + wiki_name + '";')

        row_id = mycursor.fetchone()
        if row_id is None:
            # fetch wikipedia text for wiki_name
            text = Mercury.extract_text(api_endpoint, wiki_link).rsplit("References", 1)[0]

            tokens = esa.text_to_most_important_tokens(text, minimum_percentage=0.20)  # extract tokens from text
            vec = esa_db.get_text_vector_from_bow(tokens)  # calculate vec for text

            # add topic to db (wiki!)
            sql = 'INSERT into research_areas_wiki (wos_category, wos_topic, wiki_name) VALUES (%s, %s, %s)'
            val = (wos_category, wos_topic, wiki_name)
            mycursor.execute(sql, val)
            mydb.commit()

            mycursor.execute('SELECT id FROM research_areas_wiki WHERE wiki_name = "' + wiki_name + '";')
            row_id = mycursor.fetchone()[0]

            # add every vec line to db (wiki)
            print("saving vec -- DO NOT STOP")
            for key in vec:
                mycursor.execute('INSERT into research_areas_wiki_vec (area_id, article_id, tf_idf) VALUES (' +
                                 str(row_id) + ', ' + str(key) + ', ' + str(vec[key]) + ');')
            mydb.commit()
            print("saving vec: " + wiki_name + " -- DONE")
        else:
            print("Already in db: " + wiki_name)

            mycursor.execute('SELECT article_id, tf_idf FROM research_areas_wiki_vec WHERE area_id = ' + str(row_id[0]) + ';')
            vec = {}
            for pair in mycursor.fetchall():
                vec[pair[0]] = pair[1]

        if last_topic == wos_topic:
            # add wiki vectors if they belong to the same wos topic
            topic_vec = esa_db.add_vectors(topic_vec, vec)
        else:
            if not last_topic == "":
                # save computed wos topic to db
                mycursor.execute('INSERT into research_areas (wos_category, wos_topic) VALUES ("' +
                                 last_category + '", "' + last_topic + '");')
                mydb.commit()

                mycursor.execute('SELECT id FROM research_areas WHERE wos_topic = "' + last_topic + '";')
                row_id = mycursor.fetchone()[0]

                print("saving vec -- DO NOT STOP")
                for key in topic_vec:
                    mycursor.execute("INSERT into research_areas_vec (area_id, article_id, tf_idf) VALUES (" +
                                     str(row_id) + ", " + str(key) + ", " + str(topic_vec[key]) + ");")
                mydb.commit()
                print("saving vec: " + last_topic + " -- DONE")
            topic_vec = copy.deepcopy(vec)
            last_topic = wos_topic
            last_category = wos_category

    else:
        print("-- " + wos_topic + " already in db")

# save last wos topic
mycursor.execute('INSERT into research_areas (wos_category, wos_topic) VALUES ("' +
                 last_category + '", "' + last_topic + '");')
mydb.commit()

mycursor.execute('SELECT id FROM research_areas WHERE wos_topic = "' + last_topic + '";')
row_id = mycursor.fetchone()[0]

print("saving vec -- DO NOT STOP")
for key in topic_vec:
    mycursor.execute("INSERT into research_areas_vec (area_id, article_id, tf_idf) VALUES (" +
                     str(row_id) + ", " + str(key) + ", " + str(topic_vec[key]) + ");")
mydb.commit()
print("saving vec: " + last_topic + " -- DONE")
print("ALL DONE")
