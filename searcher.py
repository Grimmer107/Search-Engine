import json
import os
from typing import List, Tuple


# searches the word in the lexicon and returns its offset
def search_lexicon(word: str) -> str | None:
    file = open('lexicon.txt', "r")
    lexicon = json.load(file)
    if word not in lexicon:
        print("Word not found in lexicon\n")
        return None
    else:
        return lexicon[word]


# receives a list of words to search
def search_words(words_list: List[str]) -> List[Tuple]:
    # get the wordIDs
    word_ids = []
    for word in words_list:
        word_id = search_lexicon(word)
        if word_id is not None:
            word_ids.append(word_id)

    # a dictionary containing information about the documents, is used to calculate the Rank of the documents
    documents = {}

    for word_id in word_ids:
        barrel_num = int(word_id[0] / 533) + 1
        inverted_index = open(
            "./InvertedBarrels/inverted_barrel_" + str(barrel_num) + ".txt", 'r')

        result_count = 1
        # jump to the location of the corresponding word
        inverted_index.seek(word_id[1])
        line = json.loads(inverted_index.readline())
        # load the results of the corresponding word
        while line[0][1] == word_id[0]:  # and result_count < 31:
            # destructuring the data
            doc_id = str(line[0][0])
            title_hit_list = line[1][0]
            # title hits are scaled by 5 to increase relevance
            title_hits = title_hit_list[1] * 5
            content_hit_list = line[1][1]
            content_hits = content_hit_list[1]
            # if the document has already been added before then calculate the proximity between the words
            if doc_id in documents:
                # add the new hits to the score
                documents[doc_id][0] = documents[doc_id][0] + \
                    title_hits + content_hits
                # calculate proximity and add weight
                if content_hits > 0:
                    if documents[doc_id][1] is not None:
                        # calculate proximity of each occurance
                        for doc_idx in range(1, len(documents[doc_id])):
                            prev_word_hit_list = documents[doc_id][doc_idx]
                            idx_range = min(len(prev_word_hit_list),
                                            len(content_hit_list))
                            for location_idx in range(2, idx_range):
                                proximity = abs(
                                    prev_word_hit_list[location_idx] - content_hit_list[location_idx])
                                if proximity <= 1:
                                    documents[doc_id][0] += 10
                                elif proximity <= 10:
                                    documents[doc_id][0] += 8
                                elif proximity <= 100:
                                    documents[doc_id][0] += 4
                                else:
                                    documents[doc_id][0] += 2
                    # add the hitlist of the current word for next word's proximity calculation
                    documents[doc_id].append(content_hit_list)
                    # if it hasnt been added then add the data
            else:
                # if there are no content hits (means the word only occured in the title) then just add None
                if content_hits > 0:
                    documents[doc_id] = [title_hits + content_hits,
                                         content_hit_list]  # add hits in both title and content and store the hit list for proximity check
                else:
                    documents[doc_id] = [title_hits + content_hits, None]
            line = json.loads(inverted_index.readline())
            result_count += 1

        inverted_index.close()

    # convert the documents dictionary into a list and sort in descending order based on the score | higher the score the higher the rank of the document

    ranked_documents = sorted(list(documents.items()),
                              key=lambda x: x[1][0], reverse=True)
    for x in ranked_documents:
        print(x)

    return ranked_documents
