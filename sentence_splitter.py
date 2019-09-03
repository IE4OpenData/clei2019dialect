import sys
import spacy

def main():
    nlp = spacy.load('es_core_news_sm')

    current = ""
    for line in sys.stdin:
        line = line.strip()
        if line == "":
            if current.strip() != "":
                doc = nlp(current)
                start = True
                before = ""
                for sent in doc.sents:
                    if start:
                        if len(sent) < 5:
                            before = str(sent) + " "
                            start = False
                        else:
                            print(sent)
                    else:
                        if before:
                            print(before + str(sent))
                            before = None
                        else:
                            print(sent)
            current = ""
        else:
            current = current + " " + line
    if current.strip() != "":
        doc = nlp(current)
        for sent in doc.sents:
            print(sent)

if __name__ == '__main__':
    main()
