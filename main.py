import re, json
import webbrowser
from datetime import datetime
from tkinter import *
from tkinter.font import ITALIC, Font
from nltk import stem
from searcher import searchWords
from tkinter import filedialog
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from tkHyperLinkManager import HyperlinkManager
from functools import partial
from indexer import generate_forward_index
from sorter import inverted_index_generator

stop_words = set(stopwords.words('english'))
snow_stemmer = SnowballStemmer(language='english')


def clickSearchButton(event):
    start = datetime.now()

    search_text = searchText.get()

    search_words = (re.sub('[^a-zA-Z]', ' ', search_text)).lower().split()
    # if the user didnt enter anything then return
    if len(search_text) == 0:
        result.delete(0.0, END)
        result.insert(END, "You didn't enter anything")
        return
        # stem the input words
    stemmed_words = [snow_stemmer.stem(word) for word in search_words if not word in stop_words]

    # the file containing the URLs of each indexed document
    UrlFile = open('document_index.txt', 'r')
    docIndex = json.load(UrlFile)

    # the result of the search
    rankedDocuments = searchWords(stemmed_words)

    end = datetime.now()
    timeTaken = str(end - start)

    # Convert to hyperLinks
    hyperLink = HyperlinkManager(result)

    frame3 = Frame(window, background="black")

    frame3.pack()

    timeTaken_msg = Label(frame3, text="Time taken for search in seconds = ", font=("Helvetica", 12, ITALIC),
                          background="black", foreground="#00FFC0")
    timeTaken_msg.pack(side=LEFT)

    timeTaken_secs = Label(frame3, text=timeTaken, font=("Helvetica", 12, ITALIC), foreground="white",
                           background="black")
    timeTaken_secs.pack(side=RIGHT)

    frame3.place(relx=0.5, rely=0.7, anchor=CENTER)

    result.delete(0.0, END)

    # this displays the result 
    if len(rankedDocuments):
        for document in rankedDocuments:
            url = docIndex[document[0]]
            result.insert(END, url, hyperLink.add(partial(webbrowser.open, url)))
            result.insert(END, "\n")
    else:
        result.insert(END, "Sorry, no result found")


def clickInsertDataButton():
    # gets the path of the folder containing the data
    folderSelected = filedialog.askdirectory()
    try:
        # if the IndexInfo[0] contains a flag if it is 1 that means more documents were added to the forward index else they werent
        indexInfo = generate_forward_index(folderSelected)
        if indexInfo[0]:
            indexInfo.append(inverted_index_generator())
    except:
        result.delete(0.0, END)
        result.insert(END, "There was an error in generating the forward and inverted indices")
        return

    result.delete(0.0, END)
    if indexInfo[0]:
        result.insert(END, "Forward and inverted index generation successful for json files in " + folderSelected)
        result.insert(END, "\n")
        result.insert(END, "The number of docs scanned were: " + str(indexInfo[1]))
        result.insert(END, "\n")
        result.insert(END, "Time it took for forward index generation is: " + indexInfo[2])
        result.insert(END, "\n")
        result.insert(END, "Time it took for inverted index generation is: " + indexInfo[3])
    else:
        result.insert(END,
                      "There were either no Json files in the input directory or those Json files have already been indexed")


window = Tk()
window.title('Search')
window.configure(background="black")
window.geometry("1920x1080")

window.bind('<Return>', clickSearchButton)

logo = PhotoImage(file="talash_png_2.png")
Label(window, image=logo, background="black").place(relx=0.5, rely=0.25, anchor=CENTER)

frame = Frame(window)
frame.pack()

searchText = Entry(frame, width=50, font=("Helvetica", 14), bg="white")
searchText.pack(side=LEFT)

searchButton = Button(frame, text="Search", font=("Helvetica", 10), width=6)
searchButton.pack(side=RIGHT)
searchButton.bind("<Button-1>", lambda event: clickSearchButton(event))

frame.place(relx=0.5, rely=0.33, anchor=CENTER)

scroll = Scrollbar(window)
scroll.pack(side=RIGHT, fill=Y)

result = Text(window, width=100, height=10, foreground="black", background="#00FFC0", font=("Helvetica", 14),
              yscrollcommand=scroll.set)
result.place(relx=0.5, rely=0.52, anchor=CENTER)

scroll.config(command=result.yview)

addButton = Button(window, text="Insert Data", font=("Helvetica", 10), width=11, command=clickInsertDataButton)
addButton.place(relx=0.5, rely=0.77, anchor=CENTER)

window.mainloop()