import pandas as pd
from transformers import pipeline
# from unidecode import unidecode
from tqdm import tqdm
import numpy as np

INPUT = ".//callejeros//comunidad-de-madrid_madrid.csv"
OUTPUT = "bert_naive_madrid.csv"

df = pd.read_csv(INPUT, header=None, encoding="cp1252")
print(df)

# Create PIPELINE
# The model model="bert-base-multilingual-uncased" needs training
classifier = pipeline("zero-shot-classification")
candidate_labels = ["colonialismo", "religión", "fruta"]

# Show EXAMPLE
print("For example, try to classify Colon and Mayor:")
res = classifier(["Colón", "Mayor"], candidate_labels)
print(res[0]["scores"])
print(res[1]["scores"])


def normalize_string(string):
    '''
    Normalizes any string by lowering all cases and
    possibly removing all accents from any letter.
    '''
    words = [w for w in string.split(' ')]
    words = [w.lower() for w in words]
    # words = [ unidecode(w) for w in words ]
    return ' '.join(words)


def strip_string(string, ignore_list):
    '''
    Strips a given string of any word present in the ignore_list
    '''
    words = [w for w in string.split(' ') if w not in ignore_list]
    return ' '.join(words)


DETERMINANTES = set(["la", "el", "lo", "de", "del", "las", "los"])
TIPOS_VIAS = set(["avenida", "calle", "bulevar", "callejon", "camino",
                 "carretera", "circunvalación", "cordel", "paseo", "plaza",
                  "ronda", "travesía", "túnel", "venta", "vereda", "rotonda"])
IGNORE_LIST = list(DETERMINANTES | TIPOS_VIAS)
IGNORE_LIST = [normalize_string(w) for w in IGNORE_LIST]


streets = df[0].to_list()
streets_norm = [strip_string(normalize_string(w), IGNORE_LIST)
                for w in df[0].to_list()]


# On CPU it takes about 26mins to complete the 494 streets

scores = []
with open(OUTPUT, 'w+', encoding="utf-8") as file:
    pass

for jj in tqdm(range(len(streets_norm))):
    res = classifier(streets_norm[jj], candidate_labels, num_workers=5)

    # Sort scores according to original candidate_labels
    sc = [res["scores"][np.argwhere(
        [_ == REFWORD for _ in res["labels"]]
        )[0][0]] for REFWORD in candidate_labels]
    scores.append(sc)

    with open(OUTPUT, 'a', encoding="utf-8") as file:
        file.write(f"{streets[jj]},{streets_norm[jj]},{sc}\n")
