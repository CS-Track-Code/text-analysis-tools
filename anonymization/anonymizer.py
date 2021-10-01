from anonymization.entity_ruler import SpacyEntity
import hashlib

from concept_extraction.dbpedia import keyword_extraction_dbpedia


class Anonymizer:
    def __init__(self, lang="en", patterns=None, sensible_data_labels=None):
        self.lang = lang
        if patterns is None:
            patterns = default_patterns
        if sensible_data_labels is None:
            sensible_data_labels = ["PHONE_NUMBER", "EMAIL", "PERSONAL_ACCOUNT"]

        self.patterns = patterns
        self.sensible_data_labels = sensible_data_labels

        self.entity_ruler = SpacyEntity(lang)
        self.entity_ruler.add_pattern(patterns)
        self.saved_patterns = []

    def get_saved_patterns(self):
        return self.saved_patterns

    def anonymize_text(self, text, salt, library_list=None, project_name=None):
        anonymize = []
        # project_name = project_name.split(" ") if project_name is not None else []
        if project_name is not None:
            normal = []
            lower = []
            upper = []
            for word in self.entity_ruler.nlp(project_name):
                normal.append({"ORTH": word.text})
                lower.append({"ORTH": word.text.lower()})
                upper.append({"ORTH": word.text.upper()})
            pattern = [{"label": "PROJECT_NAME", "pattern": normal},
                       {"label": "PROJECT_NAME", "pattern": lower},
                       {"label": "PROJECT_NAME", "pattern": upper}]
            self.entity_ruler.add_pattern(pattern)

            for p in pattern:
                if p not in self.saved_patterns:
                    self.saved_patterns.append(p)

        dbpedia = keyword_extraction_dbpedia(text, "en")

        more_patterns = []
        new_patterns = []
        for dbpedia_result in dbpedia:
            for schema, label in [("Place", "GPE"), ("Organization", "ORG"), ("Event", "EVENT")]:
                if schema in dbpedia_result[3]:
                    pattern = []
                    for word in self.entity_ruler.nlp(dbpedia_result[2]):
                        pattern.append({"ORTH": word.text})
                    new_pattern_line = {"label": "NOT_A_PERSON", "pattern": pattern}
                    if new_pattern_line not in more_patterns:
                        more_patterns.append(new_pattern_line)
                        new_patterns.append({"label": label, "pattern": new_pattern_line["pattern"]})

                    pattern = []
                    for word in self.entity_ruler.nlp(dbpedia_result[0].replace("_", " ")):
                        pattern.append({"ORTH": word.text})
                    new_pattern_line = {"label": "NOT_A_PERSON", "pattern": pattern}
                    if new_pattern_line not in more_patterns:
                        more_patterns.append(new_pattern_line)
                        new_patterns.append({"label": label, "pattern": new_pattern_line["pattern"]})

                    if "&" in dbpedia_result[0]:
                        pattern = []
                        for word in self.entity_ruler.nlp(dbpedia_result[0].replace("_", " ").replace("&", "and")):
                            pattern.append({"ORTH": word.text})
                        new_pattern_line = {"label": "NOT_A_PERSON", "pattern": pattern}
                        if new_pattern_line not in more_patterns:
                            more_patterns.append(new_pattern_line)
                            new_patterns.append({"label": label, "pattern": new_pattern_line["pattern"]})
        if len(more_patterns) > 0:
            self.entity_ruler.add_pattern(more_patterns)
            for p in new_patterns:
                if p not in self.saved_patterns:
                    self.saved_patterns.append(p)

        dbpedia_in_text = [w[2] for w in dbpedia]
        dbpedia_wiki_words = [w[0] for w in dbpedia]

        result_doc = self.entity_ruler.classify(text)
        if self.entity_ruler.ruler.matcher.__contains__("PROJECT_NAME"):
            self.entity_ruler.ruler.matcher.remove("PROJECT_NAME")
        if self.entity_ruler.ruler.matcher.__contains__("NOT_A_PERSON"):
            self.entity_ruler.ruler.matcher.remove("NOT_A_PERSON")

        for i in range(len(result_doc.ents)):
            if result_doc.ents[i].label_ in self.sensible_data_labels:
                anon_item = result_doc.ents[i]
                if anon_item not in anonymize:
                    anonymize.append(anon_item)
                sentence = result_doc.ents[i].sent
                j = 1
                while i-j >= 0:
                    if result_doc.ents[i-j].sent == sentence and result_doc.ents[i-1].label_ == "PERSON":
                        anon_item = result_doc.ents[i-j]
                        if anon_item not in anonymize:
                            anonymize.append(anon_item)
                    elif result_doc.ents[i-j].sent != sentence:
                        j = i+1
                    j += 1

                j = 1
                while i+j < len(result_doc.ents):
                    if result_doc.ents[i+j].sent == sentence and result_doc.ents[i+1].label_ == "PERSON":
                        anon_item = result_doc.ents[i+j]
                        if anon_item not in anonymize:
                            anonymize.append(anon_item)
                    elif result_doc.ents[i+j].sent != sentence:
                        j = len(result_doc.ents) +2
                    j += 1
            elif result_doc.ents[i].label_ == "PERSON" or result_doc.ents[i].label_ == "PER":
                if not (result_doc.ents[i].text in dbpedia_in_text or result_doc.ents[i].text in dbpedia_wiki_words)\
                        and result_doc.ents[i] not in anonymize:
                    anonymize.append(result_doc.ents[i])

        annotated_text = ""
        last = 0
        for ent in result_doc.ents:
            end = ent.end_char
            annotated_text += text[last:end] + " (" + ent.label_ + ")"
            last = end
        annotated_text += text[last:]

        anonymized_text = ""
        last = 0
        anonymize.sort(key=lambda x: x.start_char, reverse=False)
        for ent in anonymize:
            start = ent.start_char
            end = ent.end_char
            if library_list is not None:
                if ent.text in library_list:
                    anonymization = library_list[ent.text]
                else:
                    anonymization = self.anonymize_entity(ent.text, salt)
                    library_list[ent.text] = anonymization
            else:
                anonymization = self.anonymize_entity(ent.text, salt)
            anonymized_text += text[last:start] + "<" + ent.label_ + ">" + anonymization + "</" + ent.label_ + ">"
            last = end
        anonymized_text += text[last:]

        if library_list is not None:
            return annotated_text, anonymized_text, library_list
        else:
            return annotated_text, anonymized_text

    def anonymize_entity(self, ent_text, salt):
        dk = hashlib.pbkdf2_hmac('sha256', ent_text.encode("utf-8"), salt.encode("utf-8"), 1000)
        anonymization = dk.hex()
        return anonymization


default_patterns = [
    {"label": "PHONE_NUMBER", "pattern": [{"ORTH": "("}, {"SHAPE": "ddd"}, {"ORTH": ")"}, {"SHAPE": "ddd"},
                                          {"ORTH": "-", "OP": "?"}, {"SHAPE": "dddd"}]},
    {"label": "PHONE_NUMBER", "pattern": [{"SHAPE": "ddd"}, {"ORTH": "-", "OP": "?"}, {"SHAPE": "ddd"},
                                          {"ORTH": "-", "OP": "?"}, {"SHAPE": "dddd"}]},
    {"label": "PHONE_NUMBER", "pattern": [{"SHAPE": "ddd"}, {"ORTH": "-", "OP": "?"}, {"TEXT": {"REGEX": "[A-Z][A-Z][A-Z]+"}},
                                          {"ORTH": "-", "OP": "?"}, {"TEXT": {"REGEX": "[A-Z][A-Z][A-Z]+"}}]},
    {"label": "PHONE_NUMBER", "pattern": [{"TEXT": {"REGEX": "^[0-9][0-9][0-9]+[-][A-Z][A-Z][A-Z]+"}},
                                          {"ORTH": "-", "OP": "?"}, {"TEXT": {"REGEX": "[A-Z][A-Z][A-Z]+"}}]},
    {"label": "PHONE_NUMBER", "pattern": [{"SHAPE": "ddd"}, {"SHAPE": "ddd"}, {"SHAPE": "dddd"}]},

    # +5(555)-555-5555
    {"label": "PHONE_NUMBER", "pattern": [{"TEXT": {"REGEX": "^[+][0-9][0-9]?[0-9]?[(]?[0-9][0-9][0-9]?[)]?[/]?[-]?"
                                                             "[0-9][0-9][0-9]*"}},
                                          {"ORTH": "-", "OP": "?"},
                                          {"TEXT": {"REGEX": "[0-9]+"}}]},
    # +55(555)55555
    {"label": "PHONE_NUMBER", "pattern": [{"TEXT": {"REGEX": "^[+][0-9][0-9]?[0-9]?[(]?[0-9][0-9][0-9]?[)]?[/]?"
                                                             "[0-9][0-9][0-9]+"}}]},
    # +55 (555) 55555
    {"label": "PHONE_NUMBER", "pattern": [{"TEXT": {"REGEX": "^[+][0-9][0-9]?[0-9]?$"}},
                                          {"ORTH": "(", "OP": "?"},
                                          {"TEXT": {"REGEX": "^[0-9][0-9][0-9]?$"}},
                                          {"ORTH": ")", "OP": "?"},
                                          {"TEXT": {"REGEX": "[/]?[0-9][0-9][0-9]+$"}}]},

    # +55 555 55 55 55
    {"label": "PHONE_NUMBER", "pattern": [{"TEXT": {"REGEX": "^[+][0-9][0-9]?[0-9]?$"}},
                                          {"TEXT": {"REGEX": "^[0-9][0-9][0-9]?$"}},
                                          {"TEXT": {"REGEX": "[/]?[0-9][0-9]+$"}},
                                          {"TEXT": {"REGEX": "[/]?[0-9][0-9]+$"}},
                                          {"TEXT": {"REGEX": "[/]?[0-9][0-9]+$"}}]},

    # tel:+55 5 5555 55 555
    {"label": "PHONE_NUMBER", "pattern": [{"TEXT": {"REGEX": "[+][0-9][0-9]?[0-9]?$"}},
                                          {"ORTH": "(", "OP": "?"},
                                          {"TEXT": {"REGEX": "^[(]?[0-9][0-9]?[)]?$"}},
                                          {"ORTH": ")", "OP": "?"},
                                          {"ORTH": "(", "OP": "?"},
                                          {"TEXT": {"REGEX": "^[(]?[0-9][0-9][0-9][0-9]?[)]?$"}},
                                          {"ORTH": ")", "OP": "?"},
                                          {"TEXT": {"REGEX": "^[/]?[0-9][0-9]*$"}},
                                          {"TEXT": {"REGEX": "^[/]?[0-9][0-9][0-9]*$"}}]},

    # (5555)55555
    {"label": "PHONE_NUMBER", "pattern": [{"TEXT": {"REGEX": "^[(]?0[0-9][0-9][0-9]?[)]?[/]?[0-9][0-9][0-9]+"}}]},
    # (5555) 55555
    {"label": "PHONE_NUMBER", "pattern": [{"ORTH": ")", "OP": "?"},
                                          {"TEXT": {"REGEX": "^[(]?[0-9][0-9][0-9][0-9]*[)]?"}},
                                          {"ORTH": ")", "OP": "?"},
                                          {"TEXT": {"REGEX": "[/]?[0-9][0-9][0-9]+"}}]},

    # 0055(555)55555
    {"label": "PHONE_NUMBER", "pattern": [{"TEXT": {"REGEX": "^00[0-9][0-9]?[0-9]?[(]?[0-9][0-9][0-9]?[)]?[/]?"
                                                             "[0-9][0-9][0-9]+"}}]},
    # 0055 (555) 55555
    {"label": "PHONE_NUMBER", "pattern": [{"TEXT": {"REGEX": "^00[0-9][0-9]?[0-9]?"}},
                                          {"ORTH": "(", "OP": "?"},
                                          {"TEXT": {"REGEX": "[(]?[0-9][0-9][0-9]?[)]?"}},
                                          {"ORTH": ")", "OP": "?"},
                                          {"TEXT": {"REGEX": "[/]?[0-9][0-9][0-9]+"}}]},
    {"label": "EMAIL", "pattern": [{"LIKE_EMAIL": True}]},
    {"label": "PERSONAL_ACCOUNT", "pattern": [{"LIKE_URL": True, "TEXT": {"REGEX": ".*zooniverse.*[/]users.*"}}]},
    {"label": "LITERATURE_AUTHOR", "pattern": [{"TEXT": {"REGEX": "[A-ZÀ-ž\u0370-\u03FF\u0400-\u04FF][']?[a-zÀ-ž\u0370-\u03FF\u0400-\u04FF]*"}},
                                               {"ORTH": "-", "OP": "?"},
                                               {"TEXT": {"REGEX": "[A-ZÀ-ž\u0370-\u03FF\u0400-\u04FF][']?[a-zÀ-ž\u0370-\u03FF\u0400-\u04FF]*", "OP": "?"}},
                                               {"ORTH": ","},
                                               {"TEXT": {"REGEX": "[A-ZÀ-ž\u0370-\u03FF\u0400-\u04FF][.]"}, "OP": "+"}]},
    {"label": "LITERATURE_AUTHOR", "pattern": [{"TEXT": {"REGEX": "[A-ZÀ-ž\u0370-\u03FF\u0400-\u04FF][']?[a-zÀ-ž\u0370-\u03FF\u0400-\u04FF]*"}},
                                               {"ORTH": ","},
                                               {"TEXT": {"REGEX": "[A-ZÀ-ž\u0370-\u03FF\u0400-\u04FF][.]"}, "OP": "+"}]}
]
