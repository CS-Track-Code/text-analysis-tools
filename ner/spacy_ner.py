import spacy


class SpacyNer:
    def __init__(self, lang):
        self.spacy_model = ""
        self.spacy_model = lang + "_core_web_sm"
        try:
            self.nlp = spacy.load(self.spacy_model)
        except OSError:
            self.spacy_model = lang + "_core_news_sm"
            try:
                self.nlp = spacy.load(self.spacy_model)
            except OSError:
                self.spacy_model = "xx_ent_wiki_sm"
                try:
                    self.nlp = spacy.load(self.spacy_model)
                    print("No language specific spacy model available. Using default model. "
                          "Check on https://spacy.io/models how to get a model for this language.")
                except OSError:
                    self.nlp = spacy.blank(lang)
                    print("Couldn't load spacy model")

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

