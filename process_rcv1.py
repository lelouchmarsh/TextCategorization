import os
import html
import pickle
import xml.etree.ElementTree as ET

import numpy as np


def save_data(data_counter, documents, labels):
    """
    Pickles the documents and labels array before deletion (to save memory).
    """
    global pkl_counter
    pickle.dump(documents, open(out_dir + "/documents-{}-{}.pkl".format(pkl_counter, data_counter), "wb"))
    pickle.dump(labels, open(out_dir + "/labels-{}-{}.pkl".format(pkl_counter, data_counter), "wb"))
    pkl_counter += 1

# Counter for pickled files
pkl_counter = 0

# Make directories for pickles
out_dir = os.path.abspath(os.path.join(os.path.curdir, "data", "RCV1", "pickles", "RCV1-v1"))
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

# Get list of categories
categories = list(open("./data/RCV1/RCV1_Uncompressed/appendices/rcv1.topics.txt", "r", encoding="utf-8")
                  .read().splitlines())
pickle.dump(categories, open(out_dir + "/class_names.pkl", "wb"))

# Get list of directories in uncompressed dataset
uncompressed = os.listdir("./data/RCV1/RCV1_Uncompressed")
dirs = list(filter(lambda x: x.startswith("1"), uncompressed))
dirs.sort()

data_counter = 0
documents = []
labels = []
for d in dirs:
    files = os.listdir("./data/RCV1/RCV1_Uncompressed/" + d)
    files.sort()

    for f in files:
        tree = ET.parse("./data/RCV1/RCV1_Uncompressed/" + d + "/" + f)
        root = tree.getroot()

        # Get headline of news item
        headline = root.findall("headline")
        assert len(headline) == 1
        headline = headline[0].text
        if headline is None:
            headline = ""

        # Get content of news item
        content = root.findall("text")
        assert len(content) == 1
        content = content[0]
        text = ""
        for p in content.findall("p"):
            text += " " + html.unescape(p.text)

        # Concatenate headline + " " + content to form document
        document = headline + text

        # Get categories of news item
        codes = root.findall("./metadata/codes[@class='bip:topics:1.0']")
        if len(codes) == 0:
            continue
        assert len(codes) == 1
        codes = codes[0]
        _labels = [0] * len(categories)
        for code in codes.findall("code"):
            _labels[categories.index(code.attrib["code"])] = 1

        documents.append(document)  # append document to documents array
        labels.append(_labels)  # append extracted categories to labels array

        data_counter += 1
        print("{} {}".format(data_counter, f))
        if data_counter % 100000 == 0:
            save_data(data_counter, documents, labels)
            del documents, labels
            documents = []
            labels = []

save_data(data_counter, documents, labels)
