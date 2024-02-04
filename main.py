import re
import json
import webbrowser
from datetime import datetime
from tkinter import *
from tkinter.font import ITALIC, Font
from nltk import stem
from searcher import search_words
from tkinter import filedialog
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from tkHyperLinkManager import HyperlinkManager
from functools import partial
from indexer import generate_forward_index
from sorter import inverted_index_generator

stop_words = set(stopwords.words('english'))
snow_stemmer = SnowballStemmer(language='english')


def click_search_button(event: Event, result: Text, search_text: Entry, window: Tk) -> None:
    start = datetime.now()

    search_text = search_text.get()

    search_query = (re.sub('[^a-zA-Z]', ' ', search_text)).lower().split()
    # if the user didnt enter anything then return
    if len(search_text) == 0:
        result.delete(0.0, END)
        result.insert(END, "You didn't enter anything")
        return
        # stem the input words
    stemmed_words = [snow_stemmer.stem(
        word) for word in search_query if not word in stop_words]

    # the file containing the URLs of each indexed document
    url_file = open('document_index.txt', 'r')
    doc_index = json.load(url_file)

    # the result of the search
    ranked_documents = search_words(stemmed_words)

    end = datetime.now()
    time_taken = str(end - start)

    # Convert to hyperLinks
    hyperLink = HyperlinkManager(result)

    frame3 = Frame(window, background="black")

    frame3.pack()

    time_taken_msg = Label(frame3, text="Time taken for search in seconds = ", font=("Helvetica", 12, ITALIC),
                           background="black", foreground="#00FFC0")
    time_taken_msg.pack(side=LEFT)

    time_taken_secs = Label(frame3, text=time_taken, font=("Helvetica", 12, ITALIC), foreground="white",
                            background="black")
    time_taken_secs.pack(side=RIGHT)

    frame3.place(relx=0.5, rely=0.7, anchor=CENTER)

    result.delete(0.0, END)

    # this displays the result
    if len(ranked_documents):
        for document in ranked_documents:
            url = doc_index[document[0]]
            result.insert(END, url, hyperLink.add(
                partial(webbrowser.open, url)))
            result.insert(END, "\n")
    else:
        result.insert(END, "Sorry, no result found")


def click_insert_data_button(result: Text) -> None:
    # gets the path of the folder containing the data
    folder_selected = filedialog.askdirectory()
    try:
        # if the IndexInfo[0] contains a flag if it is 1 that means more documents were added to the forward index else they werent
        index_info = generate_forward_index(folder_selected)
        if index_info[0]:
            index_info.append(inverted_index_generator())
    except:
        result.delete(0.0, END)
        result.insert(
            END, "There was an error in generating the forward and inverted indices")
        return

    result.delete(0.0, END)
    if index_info[0]:
        result.insert(
            END, "Forward and Inverted index generation successful for json files in " + folder_selected)
        result.insert(END, "\n")
        result.insert(
            END, "The number of docs scanned were: " + str(index_info[1]))
        result.insert(END, "\n")
        result.insert(
            END, "Time it took for forward index generation is: " + index_info[2])
        result.insert(END, "\n")
        result.insert(
            END, "Time it took for inverted index generation is: " + index_info[3])
    else:
        result.insert(END,
                      "There were either no json files in the input directory or those json files have already been indexed")


def create_search_window() -> None:
    """Setting up search window"""

    window = Tk()
    window.title('Talash')
    window.configure(background="black")
    window.geometry("1920x1080")

    window.bind('<Return>', click_search_button)

    logo = PhotoImage(file="./assets/talash_png_2.png")
    Label(window, image=logo, background="black").place(
        relx=0.5, rely=0.25, anchor=CENTER)

    frame = Frame(window)
    frame.pack()

    search_text = Entry(frame, width=50, font=("Helvetica", 14), bg="white")
    search_text.pack(side=LEFT)

    search_button = Button(frame, text="Search",
                           font=("Helvetica", 10), width=6)
    search_button.pack(side=RIGHT)
    search_button.bind(
        "<Button-1>", lambda event: click_search_button(event, result, search_text, window))

    frame.place(relx=0.5, rely=0.33, anchor=CENTER)

    scroll = Scrollbar(window)
    scroll.pack(side=RIGHT, fill=Y)

    result = Text(window, width=100, height=10, foreground="black", background="#00FFC0", font=("Helvetica", 14),
                  yscrollcommand=scroll.set)
    result.place(relx=0.5, rely=0.52, anchor=CENTER)

    scroll.config(command=result.yview)

    add_button = Button(window, text="Add Data", font=(
        "Helvetica", 10), width=11, command=partial(click_insert_data_button, result))

    add_button.place(relx=0.5, rely=0.77, anchor=CENTER)

    window.mainloop()


if __name__ == "__main__":
    create_search_window()
