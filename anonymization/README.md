# Anonymization (Documentation)

Anonymization is implemented using the Entity Ruler (and NER) by spacy as such the same spacy models are needed.
The default patterns used in this implementation are for several different formats of phone numbers as well as 
email address, user specific urls and citations.
With phone numbers, email address and user specific urls being classified as sensible data.

The prepared entity ruler is then added to a nlp pipeline to be carried out before named entity recognition.
A text that is meant to be anonymized first gets processed using this nlp pipeline. The result of this contains a list 
of all found entities including results from the entity ruler and ner.

Additionally we use DBpedia to find matching Wikipedia articles for the text. 

We then iterate through the result list of the nlp pipeline to create a more condensed list of all those entities 
that need to be anonymized.
* Entity Type belongs to sensible data
    * remember entity for anonymization
    * check sentence for entites with type "PERSON" and add those to anonymization list
* Entity Type is "PERSON"
    * check in DBpedia results if person has Wikipedia article
        * if not: add to anonymization list

Next we work through the list of entities that need to be anonymized. 
Each of these is anonymized using sha256 and a predetermined secret key. 
The entity is then replaced by it's anonymization. 
Additionally we supplement this by adding the type of the entity in the resulting text in the format 
`<label>hash</label>`.

This will be used to rule if a mentioned person is publicly known enough to not anonymize their name.