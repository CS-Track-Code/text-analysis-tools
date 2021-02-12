import spacy
from ner.spacy_ner import SpacyNer


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
