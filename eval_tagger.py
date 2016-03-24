"""
eval_tagger.py: measure accuracy of POS tagger
gbakie - 2016
"""

import sys
import numpy as np


def read_file(filename):
    tags = []

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()

            if len(line) != 0:
                tag = line.split(" ")[1]
                tags.append(tag)
    

    return np.array(tags)


if __name__ == "__main__":

    if len(sys.argv)!=3:
        print "%s: <pred_file> <true_label_file>" % sys.argv[0]
        sys.exit(1)

    pred = read_file(sys.argv[1])
    label = read_file(sys.argv[2])

    n_pred = pred.shape[0]
    n_label = label.shape[0]
    if n_pred != n_label:
        print "Number of prediction is different than number of labels"
        sys.exit(1)

    count = (pred == label).sum()
    acc = float(count) / n_pred

    print "Accuracy: %s" % acc

