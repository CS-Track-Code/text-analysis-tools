# Text Analysis Tools

Please install modules from requirements.txt with

`pip install -r requirements.txt`

Some parts use polyglot, which can be hard to install depending on your operating system.
This usually stems from problems installing pyicu (and then also pycld).
If that is the case for you on a windows system, you can try installing that by downloading the appropriate whl file(s) for your system from:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyicu (& https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycld2)
(for example for 64bit Windows Python3.6 that's PyICU‑2.6‑cp36‑cp36m‑win_amd64.whl and pycld2‑0.41‑cp36‑cp36m‑win_amd64.whl)
and installing it with

`python -m pip install *path*/*filename*`

after that installing polyglot should work by either running

`pip install -r requirements.txt` again oder specifically installing polyglot with

`pip install polyglot`


Some tools need further preparation like downloads or installation as indicated below.

main.py shows example code on how to use the tools.
main.py will ONLY run without error after installing and downloading all necessary things
detailed in the following sections, even if individual parts are independent from each other
(i.e. if you only really want to use NER, you can install the required models and copy
the corresponding code from the examples and it will work fine)

## Named Entity Recognition
NER is implemented using spacy and pretrained spacy models which must be downloaded manually via console.
The commando line depends on the language for the model you need.

- English: `python -m spacy download en_core_web_sm`
- Spanish: `python -m spacy download es_core_news_sm`
- French: `python -m spacy download fr_core_news_sm`
- German: `python -m spacy download de_core_news_sm`

for other languages please refer to https://spacy.io/models


## Translator
The current translator uses the translate module which per default uses the free translation service 
[MyMemory](https://mymemory.translated.net/doc/usagelimits.php). 
This brings the caveat of a limited number of translations available per day (1000 word as an anonymous user). 
For a higher volume with the current setup it is necessary to either use a valid email address (10000 words per day) 
at MyMemory or switch it to the paid translation service from 
[Microsoft](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/translator/).



## Text Extraction (needed for the setup of ESA) <a name="text_extraction"></a>
The text extraction is facilitated using the Mercury Web Parser. 
For this you need to run a local server with Node.js

You need to have node.js installed on your machine (https://nodejs.org/en/).
Next you will have to install the required modules via the console. For this you navigate to this projects folder
`/web_text_extraction/mercury_web_parser` and run `npm i`. 
As soon as this is done you can run the server by running `node app.js` in the same directory.


## ESA
ESA requires esa.db to be placed in `/esa/esa_data/` which you can download from https://cloud.innowise.de/index.php/s/DERr2BiWZWACJWz
and if you want to prefilter the used terms with tfidf you need to download the 
[tfidf model](https://cloud.innowise.de/index.php/s/cJFGSijPEGXZqJn) as well which is to be placed in `/concept_extraction/data/`.
Additionally you will need a running mysql service. The host of which you need to enter in the `/esa/config.py` 
file in addition to the user and password which the esa module should use.

### Setup ESA
To set up ESA (for usage of assigning research areas to texts) previous to the first application it is necessary to run `/esa/prep/prepare_research_areas.py`, 
which in turn needs the [text extraction](#text_extraction) to run. In the setup the program will need to have a 
database "esa_research_areas", which it will try to create if there isn't one. Thus the given user should either be 
given the right to create a database or it should be created manually. 
The setup will take a few hours depending on the machine you are using. During this time the text vectors for all 
research areas are pre calculated using the table in `/esa/esa_data/research_areas.csv` this table maps the 
research areas of [web of science](https://images.webofknowledge.com/images/help/WOS/hp_research_areas_easca.html) to 
wikipedia articles. If you wanted to use a different taxonomy. You could do that by changing the table. 
Be advised though that the current code is not equipped to switch between taxonomies and you would have to facilitate 
that manually.


### Usage
For the usage of ESA to assign research areas to multiple descriptions it is advisable to initiate one instance of 
ResearchAreasESA and reuse it for all descriptions as it takes about 30 minutes to load the research area vectors which 
means it would take unnecessary long if you load them for each analysis individually.

#### Standalone to analyse a list of projects
To analyse a list of projects (in an excel sheet with the columns #, project name, status, link, about) with english 
descriptions (as translation is not currently a part of this) you can run
`/esa/analyse_project_list_esa.py`. This will prompt you to enter the path of the excel sheet. It will then run and 
continuously save the results of each project as they are calculated (in a new csv file with the addendum "_results"). 
While you may check on the results during runtime please be advised, that saving in the file is not possible while it 
is opened which will prompt the program to stop.

#### Implemented in a program
For examples on individual calls please refer to the examples in main.py

  


