# Talaash
It is a search engine in Python. It uses json files as corpus of data. It is created after studying the Google research paper. It works in a similar manner. During indexing stage, it creates forward index, lexicon, and document index. It then converts forward index into inverted index for searching. During searching, it also takes relevance of document into consideration. To calculate relevance, IR Score is calculated which takes proximity into consideration. 

## Tools used
- Python
- Tkinter

## Modules used
- re
- json
- nltk

## Working of Search Engine
### Indexing 
Initially we have to select the directory which contains the dataset of articles in json format. 
The search engine has "indexer" which reads and parses the json files. It removes the stopwords and stems the words using "SnowBall Stemmer". 
The indexer creates forward index partitioned into forward barrels in directory ForwardBarrels. 
Then we have "sorter" which reads the forward barrels which contains records sorted
by docID and resorts them by wordID thus creating inverted index which are partitioned into inverted barrels in 
directory InvertedBarrels. During this process, we store the wordID along with metadata in file named "lexicon". The details of document
indexed are stored in file "DocumentIndex".

### Searching
When user enters a search query in search bar, the search engine removes the stopwords and stems the words in the search query. 
Afterwards it searches for the words in the lexicon and retrieves the location of the words in the inverted barrels. The search engine 
loads only the specific barrel into the memory and retreives the hitlist i.e. the documents in which this word occured along with their 
position. The hits in the hitlist are ranked by their position in document and whether they occur in title or content and assigned a score.
After narrowing documents which contains the search word and summing up scores based on type of hits, we get IR Score of the document.
For multi-word search string, the search engine also carries out proximity analysis of search words in a document and assigns a score based
on proximity which gets added to IR Score. The documents are sorted by their IR Score and then displayed in form of links to user.


> **Note:** The project folder must contain the directories named "ForwardBarrels" and "InvertedBarrels". A portion of the dataset is given in folder "data"
which contains files in json format.
