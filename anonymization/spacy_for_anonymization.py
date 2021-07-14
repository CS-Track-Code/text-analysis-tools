import pandas as pd
from os import path
from anonymization.anonymizer import Anonymizer

"""
texts = ["“References: Mann, D. A., O'Shea, T. J., and Nowacek, D. P. (2006). Nonlinear Dynamics in Manatee Vocalizations. Marine Mammal Science, 22(3), 548-555.” (MANATEE CHAT) “See Davis B. L., Graham A. W., Cameron E., 2019, ApJ, 873, 85 for details.” (SPIRAL GRAPH)",
         "“tel:+43 1 4277 49 307” (YAPES) “843-349-4007” (Waccamaw River Volunteer Water Quality Monitoring)",
         "problematic: “Description information example : ”To sign up to become a River Keeper and to attend the training session contact John Gremmer (920-582-7802) or Rick Fahrenkrug (920-725-0255).” not problematic: ”On September 14th 2015, a century after Einstein predicted the existence of ripples in spacetime known”"]
"""

anonymizer = Anonymizer()

# analysis of zooniverse project; input as excel table including ProjectName and About text
origin_filepath = input("Enter filepath for excel (press 'enter' to show example, enter 'X' to stop programm): ")
example_path = "../ner/ner_data/example.xls"

if origin_filepath == "":
    origin_filepath = example_path

while not origin_filepath == "" and not origin_filepath == 'X':
    text_list = pd.read_excel(origin_filepath, usecols=['Description']).values.tolist()

    addendum = "results"
    result_filepath = origin_filepath.rsplit(".", 1)[0] + "_" + addendum + ".csv"
    if path.exists(result_filepath):
        results = pd.read_csv(result_filepath, usecols=["Text", "Annotated Text", "Anonymized Text"]).values.tolist()
    else:
        results = []

    done = len(results)

    counter = 1
    all_z = len(text_list)

    for text_line in text_list:
        print("\n\n## " + str(counter) + "/" + str(all_z) + " ## ")

        text = text_line[0]
        text = text.replace("”", '"').replace("â€", '"').replace("â€™", "'").replace("’", "'").replace("Ã¡", "á").replace("", "").replace("", "")
        if counter > done and isinstance(text, str):
            res = []
            res.append(text)

            annotated_text, anonymized_text = anonymizer.anonymize_text(text, "sdzoi9gbREHJHtud589753w462UZKF")

            res.append(annotated_text)
            res.append(anonymized_text)

            results.append(res)

            # save result #
            sim_pd = pd.DataFrame(results,
                                  columns=["Text", "Annotated Text", "Anonymized Text"])
            sim_pd.to_csv(result_filepath, encoding="utf-8")
        counter += 1

    print("\n## DONE ##\n")
    print("Saved result in: " + result_filepath)
    origin_filepath = input("Enter filepath for excel (press 'enter' to show example, enter 'X' to stop programm): ")
    if origin_filepath == "":
        origin_filepath = example_path
