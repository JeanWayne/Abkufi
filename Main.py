import codecs
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords


lemmatizer = nltk.WordNetLemmatizer()

textfile = codecs.open("paper.txt", "r", "utf-8")
text = textfile.read()
textfile.close()


sentences = nltk.sent_tokenize(text,language='english')

for sentence in sentences:
    tokenized_sent = nltk.tokenize.word_tokenize(sentence,language='english')
    tagged_sent=nltk.pos_tag(tokenized_sent)
    lemmata = [(lemmatizer.lemmatize(term),tag) for (term,tag) in tagged_sent]
    for lemma,tag in lemmata:
        if lemma.lower() in stopwords.words('english') or tag in ['.',',',':','CD']  or lemma.lower() in ['(',')','-']:
            continue
        synsets = wn.synsets(lemma)
        if len(synsets) == 0:
            if lemma.lower() not in ['et','al.']:
                print(lemma + '\t' + tag)
