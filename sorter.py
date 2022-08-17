import os, json
from datetime import datetime

# performs sorting on forward barrel content
def sort(input_list):
    # creates a list of 533 lists corresponding to the number of words in one fwd index file
    sorted_list = [[] for i in range(533)]

    # Uses counting sort to sort in O(n) time
    for value in input_list:
        sorted_list[value[0][1] % 533].append(value)

    return sorted_list


def inverted_index_generator():

    start = datetime.now()

    # we find forward barrels present in directory
    barrels = [forward_barrel for forward_barrel in os.listdir("./forwardBarrels") if forward_barrel.startswith('forward_barrel_')]
    # opening lexicon to update the offset values into inverted barrels
    lexicon_file = open("lexicon.txt", "r")
    lexicon = json.load(lexicon_file)
    lexicon_keys = list(lexicon.keys())
    lexicon_file.close()

    for barrel in barrels:
        # at a time we open one forward barrel
        forward_file = open('./forwardBarrels/{}'.format(barrel))
        inverted_list = []
        # get the barrel number corresponding to the forward index file because they are not sorted
        if barrel[17].isnumeric() and barrel[16].isnumeric():
            barrel_num = barrel[15] + barrel[16] + barrel[17]
        elif barrel[16].isnumeric():
            barrel_num = barrel[15] + barrel[16]
        else:
            barrel_num = barrel[15]

        # if inverted barrel is present we load its content to a list
        if os.path.isfile("./InvertedBarrels/inverted_barrel_" + barrel_num + ".txt"):
            with open("./InvertedBarrels/inverted_barrel_" + barrel_num + ".txt", 'r') as inverted_index:
                for line in inverted_index:
                    inverted_list.append(json.loads(line))

        # we append content of forward barrel to inverted list
        for line in forward_file:
            inverted_list.append(json.loads(line))
        forward_file.close()

        # re sort the inverted list and write to the inverted barrel
        inverted_file = open("./InvertedBarrels/inverted_barrel_" + barrel_num + ".txt", 'w')
        sorted_list = sort(inverted_list)
        for i in range(len(sorted_list)):
            for j in range(len(sorted_list[i])):
                if j == 0: lexicon[lexicon_keys[sorted_list[i][0][0][1]+1]][1] = inverted_file.tell()
                inverted_file.write(json.dumps(sorted_list[i][j]))
                inverted_file.write('\n')
        inverted_file.close()

    lexicon_file = open("lexicon.txt", "w")
    lexicon_file.write(json.dumps(lexicon))
    lexicon_file.close()

    end = datetime.now()
    timeTaken = str(end - start)
    print("The time of execution to create inverted index is:", timeTaken)
    return timeTaken

