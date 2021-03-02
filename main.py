import spacy
from ner.spacy_ner import SpacyNer

from translator import translation_tool

from esa.analysis.esa import ESA

from esa.analysis.research_areas_esa import ResearchAreasESA
from esa.analysis import analyse


""" NER example """

sentences = "Serena Williams plays tennis at Wimbledon. Alexis Ohanian is married to Serena Williams."
ner_spacy = SpacyNer("en")

# list with (text, label, start_char, end_char)
ner_labels = ner_spacy.get_labels(sentences)
print(ner_labels)
# OUTPUT: [('Serena Williams', 'PERSON', 0, 15), ('Wimbledon', 'ORG', 32, 41), ('Alexis Ohanian', 'PERSON', 43, 57), ('Serena Williams', 'PERSON', 72, 87)]

# list with (text, label, descriptor)
ner_labels_and_descriptions = ner_spacy.process_text(sentences)
print(ner_labels_and_descriptions)
# OUTPUT: [('Serena Williams', 'PERSON', 'People, including fictional.'), ('Wimbledon', 'ORG', 'Companies, agencies, institutions, etc.'), ('Alexis Ohanian', 'PERSON', 'People, including fictional.'), ('Serena Williams', 'PERSON', 'People, including fictional.')]

# list with (text, label, descriptor) no duplicates
ner_list = ner_spacy.process_text_get_filtered_results(sentences)
print(ner_list)
# OUTPUT: [('Serena Williams', 'PERSON', 'People, including fictional.'), ('Wimbledon', 'ORG', 'Companies, agencies, institutions, etc.'), ('Alexis Ohanian', 'PERSON', 'People, including fictional.')]

# list with strings "text, label (descriptor)"
ner_text_list = ner_spacy.process_text_get_filtered_1d_resultlist(sentences)
print(ner_text_list)
# OUTPUT: ['Serena Williams, PERSON (People, including fictional.)', 'Wimbledon, ORG (Companies, agencies, institutions, etc.)', 'Alexis Ohanian, PERSON (People, including fictional.)']

# Get description for label:
label = "ORG"
print(spacy.explain(label))
# OUTPUT: Companies, agencies, institutions, etc.


""" Translation """

text = "Serena William spielt Tennis in Wimbledon. Sie ist verheiratet mit Alexis Ohanian."
language = translation_tool.get_language(text)
print(language)
#OUTPUT: de

en_text = translation_tool.translate(text, language, "en")
print(en_text)
#OUTPUT: Serena William plays tennis at Wimbledon. She is married to Alexis Ohanian.


""" ESA - text similarity """

esa_db_path = "esa/esa_data/esa.db"
esa = ESA(esa_db_path)

text_a = "Serena Williams plays tennis at Wimbledon. She is married to Alexis Ohanian one of the co-founders of reddit."
text_b = "Steffi Graf is a former professional tennis player from germany."
text_c = "Vincent van Gogh only got the recognition he deserved posthumously."

print("text_a and text_b: " + str(esa.similarity_of_texts(text_a, text_b)))
# OUTPUT: text_a and text_b: 0.25075657146851704

print("text_a and text_c: " + str(esa.similarity_of_texts(text_a, text_c)))
# OUTPUT: text_a and text_c: 0.020145517272858546


# if you want to filter the used terms with tf-idf:
esa = ESA(esa_db_path, filter_with_tfidf=True)

text_a = "Serena Williams plays tennis at Wimbledon. She is married to Alexis Ohanian one of the co-founders of reddit."
text_b = "Steffi Graf is a former professional tennis player from germany."
text_c = "Vincent van Gogh only got the recognition he deserved posthumously."

print("FILTERED: text_a and text_b: " + str(esa.similarity_of_texts(text_a, text_b)))
# OUTPUT: FILTERED: text_a and text_b: 0.2545854223129472

print("FILTERED: text_a and text_c: " + str(esa.similarity_of_texts(text_a, text_c)))
# OUTPUT: FILTERED: text_a and text_c: 0.019436801562132136


""" ESA for Research Areas"""
research_areas_esa = ResearchAreasESA(esa_db_path)

# can optionally be used to load in all research area vectors before starting the analysis of a text (takes about 30min)
research_area_vectors = research_areas_esa.get_research_area_vectors()

description = "In this project we ask you to help us analyse pictures of the alpregion and tag which birds are " \
              "visible in the respective picture. This helps us discern flightpaterns of endangered species' which " \
              "will in the next step help us to argue in our proposal regarding the placement of wind " \
              "turbines in this region."

research_areas_similarity_shortlist, res_areas_with_sim_list, categories_with_count, top_category, \
db_research_areas, unique_words = analyse.get_research_areas_esa_with_dbpedia_integrated(description, research_areas_esa)

print("Assigned Research Areas: " + str(research_areas_similarity_shortlist))
# OUTPUT: Assigned Research Areas: [['Life Sciences & Biomedicine', 'Biodiversity & Conservation', 0.4837322323261886], ['Life Sciences & Biomedicine', 'Environmental Sciences & Ecology', 0.4491885270514278], ['Life Sciences & Biomedicine', 'Parasitology', 0.39404344668922847]]

print("All Research Areas with similarities: " + str(res_areas_with_sim_list))
# OUTPUT: All Research Areas with similarities: [['Life Sciences & Biomedicine', 'Biodiversity & Conservation', 0.4837322323261886], ['Life Sciences & Biomedicine', 'Environmental Sciences & Ecology', 0.4491885270514278], ['Life Sciences & Biomedicine', 'Parasitology', 0.39404344668922847], ['Life Sciences & Biomedicine', 'Zoology', 0.30616495562237933], ['Life Sciences & Biomedicine', 'Marine & Freshwater Biology', 0.24224898331707892], ['Life Sciences & Biomedicine', 'Plant Sciences', 0.23726605805336753], ['Life Sciences & Biomedicine', 'Paleontology', 0.20558741374360676], ['Life Sciences & Biomedicine', 'Anatomy & Morphology', 0.19573806615227712], ['Life Sciences & Biomedicine', 'Agriculture', 0.17051345977599558], ['Social Sciences', 'Family Studies', 0.1566373305002562], ['Physical Sciences', 'Meteorology & Atmospheric Sciences', 0.1515938093631127], ['Life Sciences & Biomedicine', 'Respiratory System', 0.14940106108570422], ['Arts & Humanities', 'Film, Radio & Television', 0.1400743554804806], ['Life Sciences & Biomedicine', 'Mycology', 0.1387928270162344], ['Technology', 'Construction & Building Technology', 0.13150978495054028], ['Life Sciences & Biomedicine', 'Forestry', 0.13103223420204674], ['Social Sciences', 'Development Studies', 0.13030654173166115], ['Social Sciences', 'Geography', 0.1299946954690501], ['Life Sciences & Biomedicine', 'Biotechnology & Applied Microbiology', 0.1298337245221993], ['Technology', 'Spectroscopy', 0.12936260205066955], ['Life Sciences & Biomedicine', 'Life Sciences Biomedicine Other Topics', 0.12768220328726837], ['Physical Sciences', 'Astronomy & Astrophysics', 0.12689374756357077], ['Technology', 'Mechanics', 0.12279733343928431], ['Social Sciences', 'Urban Studies', 0.11841872506423926], ['Life Sciences & Biomedicine', 'Allergy', 0.11796527685788935], ['Social Sciences', 'Demography', 0.11349593018623971], ['Life Sciences & Biomedicine', 'Tropical Medicine', 0.11218147831932022], ['Technology', 'Materials Science', 0.11190395929008924], ['Physical Sciences', 'Geochemistry & Geophysics', 0.1115107973109702], ['Physical Sciences', 'Oceanography', 0.10896794003719247], ['Physical Sciences', 'Geology', 0.1086637468616887], ['Life Sciences & Biomedicine', 'Developmental Biology', 0.10805975171011332], ['Life Sciences & Biomedicine', 'Legal Medicine', 0.1046661979856806], ['Technology', 'Transportation', 0.10440995896751272], ['Technology', 'Energy & Fuels', 0.10046804447405856], ['Life Sciences & Biomedicine', 'Reproductive Biology', 0.09990434352369046], ['Technology', 'Instruments & Instrumentation', 0.09975455539690613], ['Life Sciences & Biomedicine', 'Evolutionary Biology', 0.09890395381057801], ['Life Sciences & Biomedicine', 'Otorhinolaryngology', 0.0979104592502702], ['Life Sciences & Biomedicine', 'Medical Laboratory Technology', 0.09681344984337056], ['Technology', 'Automation & Control Systems', 0.09568658060937607], ['Life Sciences & Biomedicine', 'Fisheries', 0.09448457433162065], ['Physical Sciences', 'Physics', 0.09406286500139166], ['Physical Sciences', 'Physical Geography', 0.09335204710558169], ['Physical Sciences', 'Water Resources', 0.09069813681991179], ['Physical Sciences', 'Thermodynamics', 0.09041570058077829], ['Physical Sciences', 'Mineralogy', 0.09026489775446592], ['Technology', 'Operations Research & Management Science', 0.0899294109626101], ['Life Sciences & Biomedicine', 'Behavioral Sciences', 0.08975895906698705], ['Technology', 'Imaging Science & Photographic Technology', 0.08721992242014139], ['Life Sciences & Biomedicine', 'Physiology', 0.0869222752841908], ['Social Sciences', 'International Relations', 0.08523653953167713], ['Life Sciences & Biomedicine', 'Anesthesiology', 0.08473299924336178], ['Social Sciences', 'Government & Law', 0.0828629607908552], ['Arts & Humanities', 'Arts & Humanities Other Topics', 0.07963452524729368], ['Life Sciences & Biomedicine', 'Geriatrics & Gerontology', 0.0792641388626193], ['Life Sciences & Biomedicine', 'Pharmacology & Pharmacy', 0.07925943700176616], ['Social Sciences', 'Ethnic Studies', 0.07920577688759839], ['Life Sciences & Biomedicine', 'Toxicology', 0.07856283354311441], ['Life Sciences & Biomedicine', 'Research & Experimental Medicine', 0.07829495020179525], ['Social Sciences', 'Area Studies', 0.07812133338939502], ['Life Sciences & Biomedicine', 'Nutrition & Dietetics', 0.07713773887632026], ['Life Sciences & Biomedicine', 'Endocrinology & Metabolism', 0.07713717412325063], ['Social Sciences', 'Business & Economics', 0.07560360910740566], ['Arts & Humanities', 'Philosophy', 0.0755839774397], ['Technology', 'Remote Sensing', 0.07480558496317491], ['Technology', 'Nuclear Science & Technology', 0.07465065971862431], ['Life Sciences & Biomedicine', 'Mathematical & Computational Biology', 0.07306752978571575], ['Life Sciences & Biomedicine', 'Neurosciences & Neurology', 0.07261948026880632], ['Life Sciences & Biomedicine', 'Sport Sciences', 0.07145503042414203], ['Technology', 'Metallurgy & Metallurgical Engineering', 0.0696514589086657], ['Physical Sciences', 'Crystallography', 0.06957004709936851], ['Physical Sciences', 'Optics', 0.0687362712852331], ['Life Sciences & Biomedicine', 'Audiology & Speech-Language Pathology', 0.06835793017016668], ['Life Sciences & Biomedicine', 'Obstetrics & Gynecology', 0.06826245678285318], ['Social Sciences', 'Social Sciences Other Topics', 0.0667418047545578], ['Life Sciences & Biomedicine', 'Biophysics', 0.06641296091899004], ['Life Sciences & Biomedicine', 'Rehabilitation', 0.06605290617319688], ['Technology', 'Telecommunication', 0.06548343634741596], ['Social Sciences', 'Archaeology', 0.06538727201052338], ['Life Sciences & Biomedicine', 'Biochemistry & Molecular Biology', 0.06523904799262394], ['Life Sciences & Biomedicine', 'Veterinary Sciences', 0.06467170769550207], ['Technology', 'Microscopy', 0.06447856304902988], ['Life Sciences & Biomedicine', 'Medical Informatics', 0.06331397996101373], ['Physical Sciences', 'Electrochemistry', 0.06312713582990694], ['Life Sciences & Biomedicine', 'Food Science & Technology', 0.06263282132730683], ['Social Sciences', 'Biomedical Social Sciences', 0.06194920010823337], ['Physical Sciences', 'Chemistry', 0.06191543291017545], ['Life Sciences & Biomedicine', 'Public, Environmental & Occupational Health', 0.06127824544350292], ['Social Sciences', 'Mathematical Methods In Social Sciences', 0.06123068564157861], ['Social Sciences', 'Social Issues', 0.06100533470169243], ['Social Sciences', 'Public Administration', 0.06065046026246993], ['Technology', 'Science & Technology Other Topics', 0.06010201132253006], ['Life Sciences & Biomedicine', 'Anthropology', 0.05963811815646112], ['Life Sciences & Biomedicine', 'Microbiology', 0.059479786934310906], ['Life Sciences & Biomedicine', 'Radiology, Nuclear Medicine & Medical Imaging', 0.058854561554516745], ['Life Sciences & Biomedicine', 'Infectious Diseases', 0.05877456638716398], ['Life Sciences & Biomedicine', 'Genetics & Heredity', 0.058698204492777746], ['Physical Sciences', 'Polymer Science', 0.057256190584469006], ['Social Sciences', 'Social Work', 0.057222874644856994], ['Social Sciences', 'Cultural Studies', 0.05690056759679584], ['Arts & Humanities', 'History', 0.05657045159448344], ['Arts & Humanities', 'Asian Studies', 0.05650567490343727], ['Social Sciences', 'Criminology & Penology', 0.056106952803964195], ['Technology', 'Robotics', 0.05562630497367818], ['Technology', 'Information Science & Library Science', 0.054947704341704255], ['Life Sciences & Biomedicine', 'Health Care Sciences & Services', 0.054786149710611375], ['Technology', 'Acoustics', 0.05467729642399159], ['Physical Sciences', 'Mining & Mineral Processing', 0.052983590347788226], ['Life Sciences & Biomedicine', 'Surgery', 0.05288593076992321], ['Life Sciences & Biomedicine', 'Immunology', 0.05248846694808827], ['Social Sciences', 'Psychology', 0.052226455634191614], ['Social Sciences', 'Linguistics', 0.05215848842265114], ['Life Sciences & Biomedicine', 'Urology & Nephrology', 0.05078549534188497], ['Life Sciences & Biomedicine', 'Critical Care Medicine', 0.05074322163771845], ['Life Sciences & Biomedicine', 'Dentistry, Oral Surgery & Medicine', 0.050713022519567864], ['Life Sciences & Biomedicine', 'Transplantation', 0.05056430814604018], ['Social Sciences', 'Communication', 0.05045268803769646], ['Life Sciences & Biomedicine', 'Ophthalmology', 0.04996134975893431], ['Life Sciences & Biomedicine', 'Hematology', 0.04982586547698531], ['Technology', 'Engineering', 0.04852910444928319], ['Technology', 'Computer Science', 0.04766074664782724], ['Life Sciences & Biomedicine', 'Substance Abuse', 0.047143939658204306], ['Life Sciences & Biomedicine', 'Pathology', 0.046233853392606876], ['Life Sciences & Biomedicine', 'Psychiatry', 0.04444485247577085], ['Life Sciences & Biomedicine', 'Dermatology', 0.04411715181587212], ['Life Sciences & Biomedicine', 'Orthopedics', 0.04409645643063434], ['Life Sciences & Biomedicine', 'Cardiovascular System & Cardiology', 0.04306833244877368], ['Arts & Humanities', 'Classics', 0.04266992156570319], ['Life Sciences & Biomedicine', 'Rheumatology', 0.042491811835764316], ['Life Sciences & Biomedicine', 'Pediatrics', 0.041902587618189456], ['Life Sciences & Biomedicine', 'Emergency Medicine', 0.04070516101399312], ['Social Sciences', 'Sociology', 0.04032791534288806], ['Life Sciences & Biomedicine', 'Entomology', 0.04020651097960294], ['Social Sciences', 'Education & Educational Research', 0.038818915338502936], ['Arts & Humanities', 'History & Philosophy of Science', 0.03735919846862997], ['Social Sciences', "Women's Studies", 0.03577157288421724], ['Life Sciences & Biomedicine', 'Gastroenterology & Hepatology', 0.03430003484932052], ['Arts & Humanities', 'Theatre', 0.03367426066481723], ['Life Sciences & Biomedicine', 'Oncology', 0.03323355590080867], ['Arts & Humanities', 'Religion', 0.03318553952734169], ['Life Sciences & Biomedicine', 'Integrative & Complementary Medicine', 0.03113661697768747], ['Arts & Humanities', 'Architecture', 0.030135689494894084], ['Life Sciences & Biomedicine', 'Medical Ethics', 0.029121469619398332], ['Physical Sciences', 'Mathematics', 0.028383935104822577], ['Arts & Humanities', 'Music', 0.028189677626440424], ['Arts & Humanities', 'Art', 0.025780935895786686], ['Life Sciences & Biomedicine', 'Nursing', 0.025636558571363308], ['Life Sciences & Biomedicine', 'General & Internal Medicine', 0.02526546105875684], ['Life Sciences & Biomedicine', 'Cell Biology', 0.019849620547920038], ['Arts & Humanities', 'Dance', 0.018855388655458348], ['Arts & Humanities', 'Literature', 0.018574774555639155], ['Life Sciences & Biomedicine', 'Virology', 0.01613832225260425]]


