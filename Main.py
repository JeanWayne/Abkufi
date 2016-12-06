import codecs
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from pymongo import MongoClient
import pymongo

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

client = MongoClient('localhost', 27017)
db = client['Papers']
minlength =0
collection = db['hindawi_1480672900295']
tonkenz = db['Tokenz_1480672900295']
#tonkenz.create_index([("Token", pymongo.ASCENDING)],unique=True)
#cursor = collection.find({"Title":"Selected Papers from TimeNav 2007"})

############################################
###  SEARCH FOR A DOI
############################################
#uid="10.1155/2008/425412"
#cursor = collection.find({"DOI": ""+uid+""}).limit(1)


############################################
###  SEARCH FOR A Author
############################################
# str="Jean"
# cursor = collection.find({"Authors.firstName": ""+str+""}).limit(500)

############################################
###  SEARCH FOR a Year
############################################
str="2010"
cursor = collection.find({"Year": ""+str+""}).limit(500)



lemmatizer = nltk.WordNetLemmatizer()

# textfile = codecs.open("paper.txt", "r", "utf-8")
wwp = codecs.open("wordsWithPunctuation", "w", "utf-8")
winuanl = codecs.open("wordIsNotUpperAndNotLower", "w", "utf-8")
iuc =codecs.open("isUpperCase", "w", "utf-8")
iucnn =codecs.open("isUpperCaseNoNumbers", "w", "utf-8")

# text = textfile.read()
# textfile.close()

#Token = CAPZ, LOWER, MIXED, NUMBERS, PUNCTUATION, LENG

# ” this char can not be read
punct = [line.rstrip('\n') for line in open('punctuation')]
namendE = [line.rstrip('\n') for line in open('namedEntities')]

for document in cursor:
    text =document['Body']

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

                Capz=""
                containsNumbers="true"
                containsPunctuation="false"
                if lemma.lower() in punct:
                    containsPunctuation=""

                ### Schreibe Sonderzeichenwörter (wie z-buffering)
                if lemma.lower() not in punct and lemma.lower() not in namendE:
                    for token in punct:
                        if token in lemma.lower() and len(lemma)>minlength:
                            wwp.write(lemma+'\n')  # + '\t' + tag) # Alles mit einem Sonderzeichen.

                ### Schreibt Wörter die CAPZ sind
                if lemma.isupper() and len(lemma)>minlength:
                    iuc.write(lemma+'\n')
                    Capz="upper"
                    if not hasNumbers(lemma):
                        iucnn.write(lemma + '\n')

                if lemma.islower() and len(lemma)>minlength:
                    Capz="lower"


                ### Schreibt wörter die Mixed sind
                if not lemma.isupper() and not lemma.islower() and len(lemma)>minlength:
                    Capz="mixed"
                    winuanl.write(lemma+'\n')
                if not hasNumbers(lemma):
                    containsNumbers="false"
                for token in punct:
                    if token in lemma and len(lemma) > minlength:
                        containsPunctuation="true"

                #isAlreadyIn = tonkenz.find_one({"Token":""+lemma+""})
                #if isAlreadyIn is None:
                tonkenz.insert_one({"Token": "" + lemma + "", "Capz": "" + Capz + "",
                                    "containsNumbers": "" + containsNumbers + "",
                                    "containsPunctuation": "" + containsPunctuation + "",
                                     "length":  + len(lemma) })

                        #print(lemma.lower())

 # def findIfItsAnAuthorName(collection, str ):
 #     cursor = collection.find({"Authors.firstName": ""+str+""}).limit(1)
 #     if len(cursor) == 0:
 #         return "false"
 #     return "true"

