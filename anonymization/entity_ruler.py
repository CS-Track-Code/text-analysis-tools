# Import the requisite library
import spacy
from spacy.pipeline import EntityRuler
from os import path


class SpacyEntity:
    def __init__(self, lang, spacy_trained_model_path=""):
        self.spacy_model = ""
        self.spacy_model = lang + "_core_web_sm"
        try:
            if path.exists(spacy_trained_model_path + self.spacy_model):
                self.nlp = spacy.load(spacy_trained_model_path + self.spacy_model)
            else:
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


        # Sample text
        # text = "This is a sample number (555) 555-5555 and this too +1(467)-287-8367 +49 203 524536. abc.test@test.de"


        # create the ruler with the ability to overwrite entities
        self.ruler = EntityRuler(self.nlp, overwrite_ents=True)

    def add_pattern(self, patterns):
        # add patterns to ruler
        self.ruler.add_patterns(patterns)

        # add the pipe
        self.nlp.add_pipe(self.ruler, before="ner")

    def classify(self, text):
        # create the doc
        doc = self.nlp(text)
        return doc

    def safe(self):
        self.spacy_model

# extract entities
# for ent in doc.ents:
#     print (ent.text, ent.label_)