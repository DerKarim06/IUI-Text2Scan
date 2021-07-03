from datetime import datetime

import nltk
import numpy as np
import pandas as pd

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

f = open('glove.6B.100d.txt', encoding='utf-8')

# Extract word vectors
word_embeddings = {}
for line in f:
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    word_embeddings[word] = coefs

@app.route('/summarizeone', methods=['GET', 'POST'])
def summarizeOne():
    if (request.method == 'GET'):
        print("GETTTTT!")
        return jsonify({'you sent': 'a request!'}), 201
    if (request.method == 'POST'):
        some_json = request.get_json()
        print("-------------------------------------------------")
        print(some_json)
        print(some_json[0])
        print("-------------------------------------------------")
        sentence_count = 5

        resultArray = {}

        # function to remove stopwords
        def remove_stopwords(sen):
            sen_new = " ".join([i for i in sen if i not in stop_words])
            return sen_new

        prevTime = datetime.now()

        par = some_json[0]
        print(type(par))

        print(par)

        sentences = []
        sentences.append(nltk.sent_tokenize(par))

        sentences = [y for x in sentences for y in x]  # flatten list

        ls = [type(item) for item in sentences]
        print(ls)

        # remove punctuations, numbers and special characters
        clean_sentences = pd.Series(sentences).str.replace("[^a-zA-Z]", " ")

        # make alphabets lowercase
        clean_sentences = [s.lower() for s in clean_sentences]

        from nltk.corpus import stopwords
        stop_words = stopwords.words('english')

        # remove stopwords from the sentences
        clean_sentences = [remove_stopwords(r.split()) for r in clean_sentences]

        sentence_vectors = []
        for i in clean_sentences:
            if len(i) != 0:
                v = sum([word_embeddings.get(w, np.zeros((100,))) for w in i.split()]) / (
                        len(i.split()) + 0.001)
            else:
                v = np.zeros((100,))
            sentence_vectors.append(v)

        # similarity matrix
        sim_mat = np.zeros([len(sentences), len(sentences)])

        from sklearn.metrics.pairwise import cosine_similarity

        for i in range(len(sentences)):
            for j in range(len(sentences)):
                if i != j:
                    sim_mat[i][j] = \
                        cosine_similarity(sentence_vectors[i].reshape(1, 100),
                                          sentence_vectors[j].reshape(1, 100))[
                            0, 0]

        print(sim_mat)

        import networkx as nx

        nx_graph = nx.from_numpy_array(sim_mat)
        scores = nx.pagerank(nx_graph)

        ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)

        for i in range(1):
            print(ranked_sentences[i][1])

        print("+", ranked_sentences)
        print("-", ranked_sentences[0][1])
        final_par = ""
        if (sentence_count <= len(ranked_sentences)):
            for i in range(sentence_count):
                final_par += ranked_sentences[i][1] + " "
        else:
            for i in range(len(ranked_sentences)):
                final_par += ranked_sentences[i][1] + " "
        resultArray[par] = final_par

        print("Duration:", datetime.now() - prevTime)
        print(resultArray)
        return jsonify({'you sent': format(some_json)}, {'highFrequencies': []}, {'result': final_par}), 201

if __name__ == '__main__':
    app.run(debug=True)

f.close()