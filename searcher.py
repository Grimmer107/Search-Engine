import json, os

# searches the word in the lexicon and returns its offset
def search_lexicon(word):
    file = open('lexicon.txt', "r")
    lexicon = json.load(file)
    if word not in lexicon:
        print("Word not found in lexicon\n")
        return None
    else:
        return lexicon[word]


# receives a list of words to search
def searchWords(wordsList):
    # get the wordIDs
    word_ids = []
    for word in wordsList:
        word_id = search_lexicon(word)
        if word_id is not None:
            word_ids.append(word_id)

    # a dictionary containing information about the documents, is used to calculate the Rank of the documents
    documents = {}

    for word_id in word_ids:
        barrel_num = int(word_id[0] / 533) + 1
        inverted_index = open("./InvertedBarrels/inverted_barrel_" + str(barrel_num) + ".txt", 'r')

        result_count = 1
        # jump to the location of the corresponding word
        inverted_index.seek(word_id[1])
        line = json.loads(inverted_index.readline())
        # load the results of the corresponding word
        while line[0][1] == word_id[0]:  # and result_count < 31:
            # destructuring the data
            docID = str(line[0][0])
            titleHitList = line[1][0]
            titleHits = titleHitList[1] * 5  # title hits are scaled by 5 to increase relevance
            contentHitList = line[1][1]
            contentHits = contentHitList[1]
            # if the document has already been added before then calculate the proximity between the words
            if docID in documents:
                # add the new hits to the score
                documents[docID][0] = documents[docID][0] + titleHits + contentHits
                # calculate proximity and add weight
                if contentHits > 0:
                    if documents[docID][1] is not None:
                        for docIdx in range(1, len(documents[docID])):  # calculate proximity of each occurance
                            prevWordHitList = documents[docID][docIdx]
                            idxRange = min(len(prevWordHitList), len(contentHitList))
                            for locationIdx in range(2, idxRange):
                                proximity = abs(prevWordHitList[locationIdx] - contentHitList[locationIdx])
                                if proximity <= 1:
                                    documents[docID][0] += 10
                                elif proximity <= 10:
                                    documents[docID][0] += 8
                                elif proximity <= 100:
                                    documents[docID][0] += 4
                                else:
                                    documents[docID][0] += 2
                    # add the hitlist of the current word for next word's proximity calculation
                    documents[docID].append(contentHitList)
                    # if it hasnt been added then add the data
            else:
                # if there are no content hits (means the word only occured in the title) then just add None
                if contentHits > 0:
                    documents[docID] = [titleHits + contentHits,
                                        contentHitList]  # add hits in both title and content and store the hit list for proximity check
                else:
                    documents[docID] = [titleHits + contentHits, None]
            line = json.loads(inverted_index.readline())
            result_count += 1

        inverted_index.close()

    # convert the documents dictionary into a list and sort in descending order based on the score | higher the score the higher the rank of the document

    rankedDocuments = sorted(list(documents.items()), key=lambda x: x[1][0], reverse=True)
    for x in rankedDocuments:
        print(x)

    return rankedDocuments


