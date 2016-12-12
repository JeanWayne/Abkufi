import codecs
import time as t
import timeit

import nltk
import numpy as np
from envs.py35.Lib.datetime import time
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from pymongo import MongoClient
import re
import pymongo
import multiprocessing


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

#####################################################



client = MongoClient('localhost', 27017)
db = client['Papers']
minlength = 0
collection = db['hindawi_1480672900295']
tonkenz = db['Tokenz_1480672900295_4']
num_cores = multiprocessing.cpu_count()


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
# name="Jean"
# cursor = collection.find({"Authors.firstName": ""+name+""}).limit(500)

############################################
###  SEARCH FOR a Year
############################################
year="2010"

count = collection.find({"Year": ""+year+""}).count()
print("size " + str(count))
#cursor.add_option(no_cursor_timeout=True)
#cursor.batch_size(3)


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
i=0


start =  t.process_time()
time_delta =  t.process_time()
for z in range(0,int(count/10)):
    cursor = collection.find({"Year": ""+year+""}).skip(z*10).limit(10)
    for document in cursor:
        text =document['Body']

        sentences = nltk.sent_tokenize(text,language='english')
        bulk = tonkenz.initialize_unordered_bulk_op()
        bulkSize=0
        for sentence in sentences:
            tokenized_sent = nltk.tokenize.word_tokenize(sentence,language='english')
            # tagged_sent=nltk.pos_tag(tokenized_sent)
            # lemmata = [(lemmatizer.lemmatize(term),tag) for (term,tag) in tagged_sent]
            # for lemma,tag in lemmata:
            #     if lemma.lower() in stopwords.words('english') or tag in ['.',',',':','CD']  or lemma.lower() in ['(',')','-']:
            #         continue
            #     synsets = wn.synsets(lemma)
            #     if len(synsets) == 0:
            for token in tokenized_sent:
                token = token.lower()
                if token in stopwords.words('english') or token in ['(', ')', '-', '.', ',', ';', ':'] or re.match(
                        '^[0-9\.,]*[0-9]$', token):
                    continue
                if wn.morphy(token) == None:
                    delta_lemma = re.sub(r'[^\w\s]','',token)
                    Capz=""
                    isAuthor="false"
                    containsNumbers="true"
                    containsPunctuation="false"
                    if token.lower() in punct:
                        containsPunctuation=""

                    ### Schreibe Sonderzeichenwörter (wie z-buffering)
                    # if lemma.lower() not in punct and lemma.lower() not in namendE:
                    #     for token in punct:
                    #         if token in lemma.lower() and len(lemma)>minlength:
                    #             wwp.write(lemma+'\n')  # + '\t' + tag) # Alles mit einem Sonderzeichen.

                    ### Schreibt Wörter die CAPZ sind
                    if token.isupper() and len(token)>minlength:
                        #iuc.write(lemma+'\n')
                        Capz="upper"
                        # if not hasNumbers(lemma):
                        #     iucnn.write(lemma + '\n')

                    if token.islower() and len(token)>minlength:
                        Capz="lower"

                    cursor_f = collection.find({"Authors.firstName": ""+token+""})
                    cursor_l = collection.find({"Authors.lastName": ""+token+""})

                    if cursor_f.retrieved>0 or cursor_l.retrieved>0:
                        isAuthor="true"


                    ### Schreibt wörter die Mixed sind
                    if not token.isupper() and not token.islower() and len(token)>minlength:
                        Capz="mixed"
                        # winuanl.write(lemma+'\n')
                    if not hasNumbers(token):
                        containsNumbers="false"
                    for token in punct:
                        if token in token and len(token) > minlength:
                            containsPunctuation="true"
                        if not len(token) == len(delta_lemma):
                            containsPunctuation = "true"

                    isAlreadyIn = tonkenz.find_one({"Token":""+token+"","document":document['_id']})
                    if isAlreadyIn is None:
                        bulk.insert({"Token": "" + token + "", "Capz": "" + Capz + "",
                                           "containsNumbers": "" + containsNumbers + "",
                                           "containsPunctuation": "" + containsPunctuation + "",
                                           "isAuthor": ""+ isAuthor +"",
                                            "length":  + len(token), "document":document['_id']})
                        bulkSize=bulkSize+1

                            #print(lemma.lower())
        if bulkSize>0:
            bulk.execute()
        s = str(i)
        stop =  t.process_time()

        time_delta=stop - time_delta
        print("Document:\t\t\t#"+s +"\t\t\t\tDOI:  "+document['DOI'])
        print("ExecutionTime:\t"+"{:10.7f}".format(time_delta)+"\t\t\t  Size of Batch:"+str(bulkSize))
        i=i+1
        bulkSize=0

 # def findIfItsAnAuthorName(collection, str ):
 #     cursor = collection.find({"Authors.firstName": ""+str+""}).limit(1)
 #     if len(cursor) == 0:
 #         return "false"
 #     return "true"

