import spacy
from os import path


class SpacyEntity:
    def __init__(self, lang, spacy_trained_model_path=""):
        if lang in ["zh", "en"]:
            self.spacy_model = lang + "_core_web_sm"
        elif lang in ["ca", "da", "nl", "fr", "de", "el", "it", "ja", "lt", "mk", "nb", "pl", "pt", "ro", "ru", "es"]:
            self.spacy_model = lang + "_core_news_sm"
        else:
            self.spacy_model = "xx_ent_wiki_sm"
            print("No language specific spacy model available. Using default model. "
                  "Check on https://spacy.io/models how to get a model for this language.")
        try:
            if path.exists(spacy_trained_model_path + self.spacy_model):
                self.nlp = spacy.load(spacy_trained_model_path + self.spacy_model)
            else:
                try:
                    self.nlp = spacy.load(self.spacy_model)
                except OSError:
                    spacy.cli.download(self.spacy_model)
                    self.nlp = spacy.load(self.spacy_model)
        except OSError:
            print("Couldn't load spacy model")

        # Sample text
        # text = "This is a sample number (555) 555-5555 and this too +5(555)-555-5555 +55 555 55555. abc.test@test.de"

        # add the entity ruler pipe
        self.ruler = self.nlp.add_pipe("entity_ruler", before="ner")

    def add_pattern(self, patterns):
        # add patterns to ruler
        self.ruler.add_patterns(patterns)

    def classify(self, text):
        # create the doc
        doc = self.nlp(text)
        return doc

    def get_nlp(self):
        return self.nlp

# extract entities
# for ent in doc.ents:
#     print (ent.text, ent.label_)