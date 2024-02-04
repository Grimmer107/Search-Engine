import json
import re
import os
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from datetime import datetime
import zlib
nltk.download('stopwords')


# This parses json files and creates lexicon and forward index
def generate_forward_index(path_to_data: str) -> None:

    try:
        start = datetime.now()
        # we create a set of stop words
        stop_words = set(stopwords.words('english'))
        snow_stemmer = SnowballStemmer(language='english')

        # check the directory for files of json format
        file_names = [pos_json for pos_json in os.listdir(
            path_to_data) if pos_json.endswith('.json')]

        # if lexicon file is present we load it to memory
        if os.path.isfile('lexicon.txt'):
            prev_lexicon = open('lexicon.txt', "r")
            lexicon = json.load(prev_lexicon)
            prev_lexicon.close()
        else:
            lexicon = {"word_count": [0, 0]}

        # create a temporary document index to store record of document being indexed
        document_indices = {}
        doc_count = 0
        word_count = lexicon["word_count"][0]

        # load the document indices, if the file exists open in read mode and load the data then open in write mode
        if os.path.isfile('./document_index.txt'):
            with open('./document_index.txt') as doc_idx:
                document_indices = json.load(doc_idx)

        document_index = open('./document_index.txt', 'w')

        # create a list of forward barrels and we use 300 barrels
        forward_barrels = []
        for barrel_count in range(1, 301):
            forward_barrels.append(
                open('./ForwardBarrels/forward_barrel_{}.txt'.format(barrel_count), 'w'))

        for file_name in file_names:
            # created a list of 300 forward dictionaries
            forward_dicts = []
            for barrelCount in range(1, 301):
                forward_dicts.append({})

            # open file and load data to be processed
            file = open("{}/{}".format(path_to_data, file_name))
            loaded_data = json.load(file)
            file.close()

            # read articles in loaded data
            for article in loaded_data:

                # hash the doc id
                doc_id = bytes(article['id'], 'utf-8')
                hashed_id = zlib.crc32(doc_id)

                # If the article is already indexed then continue else add doc id to document index
                if str(hashed_id) in document_indices:
                    continue
                else:
                    document_indices[str(hashed_id)] = article['url']
                    doc_count += 1

                # parse the content through regex, split it and lowercase it and then stem words in content
                content = (re.sub('[^a-zA-Z]', ' ',
                                  article['content'])).lower().split()
                stemmed_words = ([snow_stemmer.stem(word)
                                  for word in content if not word in stop_words])

                # parse the title through regex, split it and lowercase it and then stem words in title
                title = (re.sub('[^a-zA-Z]', ' ',
                                article['title'])).lower().split()
                stemmed_title = ([snow_stemmer.stem(word)
                                  for word in title if not word in stop_words])

                position = 1  # position of word in the title
                # store the title words in the hit list
                for word in stemmed_title:

                    # add word to lexicon if not in lexicon
                    if word not in lexicon:
                        lexicon[word] = [word_count, 0]
                        word_count += 1

                    # through word_id calculate which barrel it belongs to and then add hitlist for title
                    barrel_location = int(lexicon[word][0] / 533)
                    if (hashed_id, lexicon[word][0]) not in forward_dicts[barrel_location]:
                        # here hitlist consist of two sub lists, first list for title and second for content
                        # in title hitlist, first element is always 1 and second element is hit count
                        forward_dicts[barrel_location][(
                            hashed_id, lexicon[word][0])] = []
                        forward_dicts[barrel_location][(
                            hashed_id, lexicon[word][0])].insert(0, [1, 1])
                        forward_dicts[barrel_location][(
                            hashed_id, lexicon[word][0])].insert(1, [0, 0])
                    else:
                        # if hit list is present we just increase hit count for title hits
                        forward_dicts[barrel_location][(
                            hashed_id, lexicon[word][0])][0][1] += 1
                    position += 1

                position = 1  # position of word in the document

                for word in stemmed_words:

                    if word not in lexicon:
                        lexicon[word] = [word_count, 0]
                        word_count += 1

                    barrel_location = int(lexicon[word][0] / 533)
                    if (hashed_id, lexicon[word][0]) not in forward_dicts[barrel_location]:
                        # in content hitlist, first element is always 0 and second element is hit count
                        # and then hit position are appended
                        forward_dicts[barrel_location][(
                            hashed_id, lexicon[word][0])] = []
                        forward_dicts[barrel_location][(
                            hashed_id, lexicon[word][0])].insert(0, [1, 0])
                        forward_dicts[barrel_location][(hashed_id, lexicon[word][0])].insert(
                            1, [0, 1, position])
                    else:
                        # if hit list is present we just increase hit count for content hits
                        forward_dicts[barrel_location][(
                            hashed_id, lexicon[word][0])][1][1] += 1
                        forward_dicts[barrel_location][(
                            hashed_id, lexicon[word][0])][1].append(position)
                    position += 1

            id = 0
            while id < 300:  # here 300 is barrel count
                # write content of forward dictionary to corresponding forward barrels
                for object in forward_dicts[id].items():
                    forward_barrels[id].write(json.dumps(object))
                    forward_barrels[id].write("\n")
                id += 1

        # dump lexicon program which updates previous lexicon to create new lexicon
        lexicon["word_count"][0] = word_count
        new_lexicon = open('lexicon.txt', "w")
        new_lexicon.write(json.dumps(lexicon))
        new_lexicon.close()

        # document indices is written to document index file
        document_index.write(json.dumps(document_indices))
        document_index.close()

        end = datetime.now()
        time_taken = str(end - start)
        print("The time of execution to create forward index and lexicon is:", time_taken)
        print('doc_count = ', doc_count)
        print('word_count = ', word_count)

        if doc_count:  # if it is more than 0
            return [1, doc_count, time_taken]
        else:
            return [0, doc_count, time_taken]
    except Exception as error:
        print(error)
