import spacy
from anonymization.entity_ruler import SpacyEntity


class SpacyNer:
    def __init__(self, lang, anonymized_texts=False):
        self.lab_desc = {
            "PERSON": "People, including fictional.",
            "NORP": "Nationalities or religious or political groups.",
            "FAC": "Buildings, airports, highways, bridges, etc.",
            "ORG": "Companies, agencies, institutions, etc.",
            "GPE": "Countries, cities, states.",
            "LOC": "Non-GPE locations, mountain ranges, bodies of water.",
            "PRODUCT": "Objects, vehicles, foods, etc. (Not services.)",
            "EVENT": "Named hurricanes, battles, wars, sports events, etc.",
            "WORK_OF_ART": "Titles of books, songs, etc.",
            "LAW": "Named documents made into laws.",
            "LANGUAGE": "Any named language.",
            "DATE": "Absolute or relative dates or periods.",
            "TIME": "Times smaller than a day.",
            "PERCENT": "Percentage, including ”%“.",
            "MONEY": "Monetary values, including unit.",
            "QUANTITY": "Measurements, as of weight or distance.",
            "ORDINAL": "“first”, “second”, etc.",
            "CARDINAL": "Numerals that do not fall under another type.",
            "PER": "Named person or family.",
            "MISC": "Miscellaneous entities, e.g. events, nationalities, products or works of art."
        }

        if anonymized_texts:
            sp_ent = SpacyEntity(lang)

            pattern = [
                {"label": "PER", "pattern": [{"ORTH": "<"},
                                             {"TEXT": {"REGEX": "PER>.{64}</PER"}},
                                             {"ORTH": ">"}]},
                {"label": "PER", "pattern": [{"ORTH": "<"},
                                             {"TEXT": {"REGEX": "PER"}},
                                             {"ORTH": ">"},
                                             {"TEXT": {"REGEX": ".{64}</PER>"}}]},
                {"label": "PERSON", "pattern": [{"ORTH": "<"},
                                                {"TEXT": {"REGEX": "PERSON>.{64}</PERSON"}},
                                                {"ORTH": ">"}]},
                {"label": "PERSON", "pattern": [{"ORTH": "<"},
                                                {"TEXT": {"REGEX": "PERSON"}},
                                                {"ORTH": ">"},
                                                {"TEXT": {"REGEX": ".{64}</PERSON>"}}]},
                {"label": "EMAIL", "pattern": [{"ORTH": "<"},
                                               {"TEXT": {"REGEX": "EMAIL>.{64}</EMAIL"}},
                                               {"ORTH": ">"}]},
                {"label": "EMAIL", "pattern": [{"ORTH": "<"},
                                               {"TEXT": {"REGEX": "EMAIL"}},
                                               {"ORTH": ">"},
                                               {"TEXT": {"REGEX": ".{64}</EMAIL>"}}]},
                {"label": "PERSONAL_ACCOUNT", "pattern": [{"ORTH": "<"},
                                                          {"TEXT": {"REGEX": "PERSONAL_ACCOUNT>.{64}</PERSONAL_ACCOUNT"}},
                                                          {"ORTH": ">"}]},
                {"label": "PERSONAL_ACCOUNT", "pattern": [{"ORTH": "<"},
                                                          {"TEXT": {"REGEX": "PERSONAL_ACCOUNT"}},
                                                          {"ORTH": ">"},
                                                          {"TEXT": {"REGEX": ".{64}</PERSONAL_ACCOUNT>"}}]},
                {"label": "PHONE_NUMBER", "pattern": [{"ORTH": "<"},
                                                      {"TEXT": {"REGEX": "PHONE_NUMBER"}},
                                                      {"ORTH": ">"},
                                                      {"TEXT": {"REGEX": ".{64}</PHONE_NUMBER>"}}]},
                {"label": "PHONE_NUMBER", "pattern": [{"ORTH": "<"},
                                                      {"TEXT": {"REGEX": "PHONE_NUMBER>.{64}</PHONE_NUMBER"}},
                                                      {"ORTH": ">"}]}
            ]

            sp_ent.add_pattern(pattern)

            self.nlp = sp_ent.get_nlp()

            self.lab_desc["EMAIL"] = "Former email address of a person, organization or institution"
            self.lab_desc["PERSONAL_ACCOUNT"] = "Former link to a personal account e.g. on zooniverse"
            self.lab_desc["PHONE_NUMBER"] = "Former phone number"
        else:
            if lang in ["zh", "en"]:
                self.spacy_model = lang + "_core_web_sm"
            elif lang in ["ca", "da", "nl", "fr", "de", "el", "it", "ja", "lt", "mk", "nb", "pl", "pt", "ro", "ru", "es"]:
                self.spacy_model = lang + "_core_news_sm"
            else:
                self.spacy_model = "xx_ent_wiki_sm"
                print("No language specific spacy model available. Using default model. "
                      "Check on https://spacy.io/models how to get a model for this language.")
            try:
                try:
                    self.nlp = spacy.load(self.spacy_model)
                except OSError:
                    spacy.cli.download(self.spacy_model)
                    self.nlp = spacy.load(self.spacy_model)
            except OSError:
                print("Couldn't load spacy model")

    def get_descriptors(self):
        return self.lab_desc

    def get_labels(self, text):
        labels = []
        doc = self.nlp(text)

        for d in doc.ents:
            labels.append((d.text, d.label_, d.start_char, d.end_char))

        return labels

    def process_text(self, text):
        labels_and_descriptions = []
        labels = self.get_labels(text)

        for lab in labels:
            if lab[1] in self.lab_desc:
                labels_and_descriptions.append((lab[0], lab[1], self.lab_desc[lab[1]]))
            else:
                labels_and_descriptions.append((lab[0], lab[1], ""))
        return labels_and_descriptions

    def process_text_get_filtered_results(self, text):
        results = self.process_text(text)
        shortlist = []
        for res in results:
            if not res in shortlist:
                shortlist.append(res)
        return shortlist

    def process_text_get_filtered_1d_resultlist(self, text):
        results = self.process_text_get_filtered_results(text)
        resultlist = []
        for res in results:
            res_line = res[0] + ", " + res[1] + " (" + res[2] + ")"
            resultlist.append(res_line)
        return resultlist

    def process_text_get_dicts(self, text):
        dict_list = []
        labels = self.get_labels(text)

        for lab in labels:
            if lab[1] in self.lab_desc:
                dict = {
                    "text": lab[0],
                    "label": lab[1],
                    "description": self.lab_desc[lab[1]]
                }
            else:
                dict = {
                    "text": lab[0],
                    "label": lab[1],
                    "description": ""
                }
            dict_list.append(dict)
        return dict_list

