import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.filedialog import askopenfilename
import sqlite3
import random
import os
import textwrap
import subprocess
from PIL import Image, ImageTk
from queue import Queue

conn = sqlite3.connect("MathsPlatformStorage.db") #Connect to db and configure cursor
cursor = conn.cursor()
question_table_query = """CREATE TABLE IF NOT EXISTS tblQuestion (qNo INT, qText TEXT, qImage TEXT,
                       qRating TEXT, qMarks INT, qTopic TEXT, qType TEXT, mSteps TEXT,
                       mAns TEXT, PRIMARY KEY (qNo))""" #Create question table

topic_table_query = """CREATE TABLE IF NOT EXISTS tblTopic (topicNo INT, topicName TEXT, correctQs INT, wrongQs INT, score INT, PRIMARY KEY(topicNo))""" #Create topic table

cursor.execute(question_table_query)
cursor.execute(topic_table_query)

conn.commit() #Commit changes to db
conn.close() #Close db connection

def add_question():
    #Assign appropriate variables for each input of question details
    qText = entries[0].get()
    qImage = entries[2].get()
    qRating = entries[1].get()
    qMarks = entries[3].get()
    qTopic = entries[4].get()
    qType = entries[5].get()
    mSteps = entries[6].get()
    mAns = entries[7].get()

    if mSteps == "":
        mSteps = "No working steps provided."
    
    if "" in [qText, qRating, qType, qTopic, mAns]:
        question_added_label.config(text="Please enter full valid inputs.")
    else:
        conn = sqlite3.connect("MathsPlatformStorage.db")
        cursor = conn.cursor()

        count_query = "SELECT COUNT(*) FROM tblQuestion" #Get number of questions
        cursor.execute(count_query)
        result = cursor.fetchone()
        totalQs = result[0]
        qNo = totalQs + 1 #Adds new question as next question number

        data_insert_query = """INSERT INTO tblQuestion (qNo, qText, qImage,
        qRating, qMarks, qTopic, qType, mSteps, mAns) VALUES (?,?,?,?,?,?,?,?,?)"""
        data_insert_tuple = (
            qNo,
            qText,
            qImage,
            qRating,
            qMarks,
            qTopic,
            qType,
            mSteps,
            mAns,
        )

        cursor.execute(data_insert_query, data_insert_tuple) #Inserts each associated value into the question record
        conn.commit()

        conn.close()
        question_added_label.config(text="Question added.")



def add_question_menu():
    global entries, question_added_label
    conn = sqlite3.connect('MathsPlatformStorage.db')
    cursor = conn.cursor()
    cursor.row_factory = lambda cursor, row: row[0]
    topics = cursor.execute('SELECT topicName FROM tblTopic').fetchall() #Gets all the topic names
    
    window2 = tk.Toplevel()
    window2.focus()

    window2.geometry("700x500")
    window2.title("Maths Revision Tool")

    frame = tk.Frame(window2) #Configure user interface elements
    frame.pack()

    question_details_frame = tk.LabelFrame(frame, text="Question Details")
    question_details_frame.grid(row=0, column=0, pady=30)

    buttons_frame = tk.LabelFrame(frame, text="Buttons")
    buttons_frame.grid(row=2, column=0)

    question_added_label = tk.Label(frame, text="")
    question_added_label.grid(row=3, column=0)

    qText_label = tk.Label(question_details_frame, text="qText:")
    qText_label.grid(row=0, column=0)

    qText_entry = tk.Entry(question_details_frame)
    qText_entry.grid(row=0, column=1)

    qImage_label = tk.Label(question_details_frame, text="qImage:")
    qImage_label.grid(row=1, column=0)

    qImage_entry = tk.Entry(question_details_frame)
    qImage_entry.grid(row=1, column=1)

    qRating_label = tk.Label(question_details_frame, text="qRating:")
    qRating_label.grid(row=2, column=0)

    qRating_entry = ttk.Combobox(
        question_details_frame,
        values=[
            "",
            "1 - Very Easy",
            "2 - Easy",
            "3 - Medium",
            "4 - Hard",
            "5 - Challenge",
        ],
    )
    qRating_entry.grid(row=2, column=1)

    qMarks_label = tk.Label(question_details_frame, text="qMarks:")
    qMarks_label.grid(row=0, column=2)

    qMarks_entry = tk.Spinbox(question_details_frame, from_=1, to=100)
    qMarks_entry.grid(row=0, column=3)

    qTopic_label = tk.Label(question_details_frame, text="qTopic:")
    qTopic_label.grid(row=1, column=2)

    qTopic_entry = ttk.Combobox(question_details_frame, values=topics)
    qTopic_entry.grid(row=1, column=3)

    qType_label = tk.Label(question_details_frame, text="qType:")
    qType_label.grid(row=2, column=2)

    qType_entry = ttk.Combobox(
        question_details_frame,
        values=["", "Automark - num answer", "Manual - string answer"],
    )
    qType_entry.grid(row=2, column=3)

    mSteps_label = tk.Label(question_details_frame, text="mSteps:")
    mSteps_label.grid(row=3, column=0)

    mSteps_entry = tk.Entry(question_details_frame)
    mSteps_entry.grid(row=3, column=1)

    mAns_label = tk.Label(question_details_frame, text="mAns:")
    mAns_label.grid(row=3, column=2)

    mAns_entry = tk.Entry(question_details_frame)
    mAns_entry.grid(row=3, column=3)

    submit_button = tk.Button(buttons_frame, text="Submit", command=add_question)
    submit_button.grid(row=0, column=1, ipadx=30, ipady=10)

    for widget in question_details_frame.winfo_children():
        widget.grid_configure(padx=20, pady=14, ipadx=15, ipady=8) #Add spacing between elements in question frame

    for widget in buttons_frame.winfo_children():
        widget.grid_configure(padx=20, pady=14) #Add spacing between elements in button frame
    
    entries = [qText_entry, qRating_entry, qImage_entry, qMarks_entry, qTopic_entry, qType_entry, mSteps_entry, mAns_entry]


def answer_question_menu():
    global questionFrame, first_q, enterAnswer, label_img

    first_q = True
    recent_questions = Queue(maxsize = 5) #Queue for 5 most recently answered questions

    window = tk.Toplevel()
    window.focus()
    window.geometry("1200x700")
    window.title("Maths Revision Tool")

    frame = tk.Frame(window)
    frame.pack()

    conn = sqlite3.connect("MathsPlatformStorage.db")
    cursor = conn.cursor()

    count_query = "SELECT COUNT(*) FROM tblQuestion" #Get number of questions
    cursor.execute(count_query)
    result = cursor.fetchone()
    totalQs = result[0]
    currentQ = random.randint(1, totalQs) #Get random question for first question

    currentQ = 5

    search_query = (
        "SELECT qText, qRating, qImage, qMarks, qTopic, qType, mSteps, mAns FROM tblQuestion WHERE qNo="
        + str(currentQ)
    )
    cursor.execute(search_query)
    question_info = cursor.fetchone() #Get question details

    questionFrame = tk.LabelFrame(frame, text="Question")
    questionFrame.grid(row=0, column=0)

    questionNoText = str(currentQ) + "."

    questionNo = tk.Label(questionFrame, text=questionNoText, font=30)
    questionNo.pack()

    questionText = question_info[0] + " [" + str(question_info[3]) + "]"

    questionTextLabel = tk.Label(questionFrame, text=questionText, font=30)
    questionTextLabel.pack()

    if question_info[2] != "":
        shown_image_path = "images/" + question_info[2]
    else:
        shown_image_path = "images/filler.png"

    image = Image.open(shown_image_path)
    resize_image = image.resize((400,400))
    image_obj = ImageTk.PhotoImage(resize_image)
    label_img = tk.Label(questionFrame, image=image_obj)
    label_img.image = image_obj
    label_img.pack()

    answerFrame = tk.LabelFrame(frame, text="Answer")
    answerFrame.grid(row=1, column=0, ipadx=40, ipady=5)
    recentQuestionFrame = tk.LabelFrame(frame, text="Recent Questions")
    recentQuestionFrame.grid(row=1, column=1, ipadx=40, ipady=5)
    recentQuestionsLabel = tk.Label(recentQuestionFrame, text=recent_questions.queue, font=("Arial", 12), wraplength=200)
    recentQuestionsLabel.grid(row=0, column=0)

    if question_info[5] == 'Automark - num answer':

        enterLabel = tk.Label(answerFrame, text="Enter:", font=25)
        enterLabel.grid(row=0, column=0)

        enterAnswer = tk.Entry(answerFrame, font=20)
        enterAnswer.grid(row=0, column=1)

    stepsFrame = tk.LabelFrame(frame, text="Steps")
    stepsFrame.grid(row=0, column=1)
    steps = tk.Label(stepsFrame, font=30, wraplength=250)
    steps.grid(row=0, column=0, pady=50, padx=50)

    def show_answer(question_info):
        global resultCheck, answer, choiceBox, choiceButton, enterLabel, enterAnswer
        submitAnswerButton.config(text="Next Question", command=lambda: next_question(question_info))
        steps.config(text=question_info[6])
        conn = sqlite3.connect("MathsPlatformStorage.db")
        cursor = conn.cursor()
        if question_info[5] == 'Automark - num answer':
            answerText = "Answer: " + str(question_info[7])
            userAnswer = enterAnswer.get() #Get user input for answer
        else:
            answerText = ''
        answer = tk.Label(answerFrame, text=answerText, font=30)
        answer.grid(row=1, column=1)

        resultFrame = tk.LabelFrame(frame, text="Result")
        resultFrame.grid(row=2, column=0)
        resultCheck = tk.Label(resultFrame, font=40)
        resultCheck.grid(row=0, column=0, padx=20, pady=20)
    
        if question_info[5] == 'Automark - num answer': #Automark question case
            if userAnswer == str(question_info[7]): #If the answer is correct, increase correctQs by 1
                cursor.execute(
                    "UPDATE tblTopic SET correctQs = correctQs + 1 WHERE tblTopic.topicName = '"
                    + str(question_info[4])
                    + "'"
                )
                cursor.execute( #Increase score by the question marks
                    "UPDATE tblTopic SET score = score + "
                    + str(question_info[3])
                    + " WHERE tblTopic.topicName = '"
                    + str(question_info[4])
                    + "'"
                )
                resultText = 'Correct!'
            else: #If wrong, increase wrongQs by 1
                cursor.execute(
                    "UPDATE tblTopic SET wrongQs = wrongQs + 1 WHERE tblTopic.topicName = '"
                    + str(question_info[4])
                    + "'"
                )
                resultText = 'Wrong!'
            resultCheck.config(text=resultText)
            if recent_questions.full(): #If queue is full, remove the front question
                recent_questions.get()
            recent_questions.put([question_info[0], resultText]) #Add current question to the rear
            recentQuestionsLabel.config(text=recent_questions.queue)
        
        if question_info[5] == 'Manual - string answer': #If question is manually marked, run alternate marking function
            choiceBox = ttk.Combobox(answerFrame, values=['correct','wrong'])
            choiceBox.grid(row=1, column=2)
            choiceButton = tk.Button(answerFrame, text='Submit Choice', command=check_choice)
            submitAnswerButton.config(command=wait_for_choice)
            choiceButton.grid(row=1, column=1)

        resultCheck.grid(row=2, column=0)
        conn.commit()
        conn.close()

    def next_question(question_info):
        global first_q, enterLabel, enterAnswer, label_img
        label_img.destroy()

        if question_info[5] == 'Manual - string answer' and first_q == True:
            choiceBox.destroy()
            choiceButton.destroy()

        submitAnswerButton.config(
            text="Mark / Show Answer", command=lambda: show_answer(question_info)
        )
        conn = sqlite3.connect("MathsPlatformStorage.db")
        cursor = conn.cursor()

        resultCheck.config(text="")
        answer.config(text="")
        steps.config(text="")

        topic_query = "SELECT topicName, correctQs, wrongQs FROM tblTopic" #Get all topic names
        cursor.execute(topic_query)
        topic_info = cursor.fetchall()
        topic_dict = {}
        ratio_sum = 0
        for x in topic_info:
            ratio = round((1/(x[1] / (x[1] + x[2]))),2)
            ratio_sum += ratio
        for x in topic_info:
            topic_name = x[0]
            ratio = round((1/(x[1] / (x[1] + x[2]))),2)
            topic_dict[topic_name] = ratio / ratio_sum #calculate weighted ratios for each topic based on performance in the topic
        topic = (random.choices(list(topic_dict.keys()), weights=topic_dict.values(), k=1))[0]
        #Select a topic for next question using weighted keys in random choice
        search_query = ("SELECT qText, qRating, qImage, qMarks, qTopic, qType, mSteps, mAns, qNo FROM tblQuestion WHERE qTopic=" + "'" + topic + "' ORDER BY RANDOM() LIMIT 1")
        cursor.execute(search_query) #Get next question details
        question_info = cursor.fetchone()
        if question_info[5] == 'Automark - num answer':

            enterLabel = tk.Label(answerFrame, text="Enter:", font=25)
            enterLabel.grid(row=0, column=0)

            enterAnswer = tk.Entry(answerFrame, font=20)
            enterAnswer.grid(row=0, column=1)
            
        questionNoText = str(question_info[8]) + "."
        questionText = question_info[0] + " [" + str(question_info[3]) + "]"

        questionTextLabel.config(text=questionText)
        questionNo.config(text=questionNoText)

        print(question_info[2])
        if question_info[2] != "":
            shown_image_path = "images/" + question_info[2]
        else:
            shown_image_path = "images/filler.png"

        image = Image.open(shown_image_path)
        resize_image = image.resize((400,400))
        image_obj = ImageTk.PhotoImage(resize_image)
        label_img = tk.Label(questionFrame, image=image_obj)
        label_img.image = image_obj
        label_img.pack()

    def wait_for_choice():
        resultCheck.config(text="Select your answer result first and confirm the choice.")

    def check_choice():
        conn = sqlite3.connect('MathsPlatformStorage.db')
        cursor = conn.cursor()
        correctChoice = choiceBox.get()
        if correctChoice == 'correct': #if user selects correct, increase correctQs by 1 and score by marks
            cursor.execute(
                "UPDATE tblTopic SET correctQs = correctQs + 1 WHERE tblTopic.topicName = '"
                + str(question_info[4])
                + "'"
            )
            cursor.execute(
                "UPDATE tblTopic SET score = score + "
                + str(question_info[3])
                + " WHERE tblTopic.topicName = '"
                + str(question_info[4])
                + "'"
            )
            resultText = 'Correct!'
        else: #if user selects wrong, increase wrongQs by 1
            cursor.execute(
                "UPDATE tblTopic SET wrongQs = wrongQs + 1 WHERE tblTopic.topicName = '"
                + str(question_info[4])
                + "'"
            )
            resultText = 'Wrong'
        resultCheck.config(text=resultText)
        if recent_questions.full(): #if queue full, remove front question
            recent_questions.get()
        recent_questions.put([question_info[0], resultText]) #Add current question to rear of queue
        recentQuestionsLabel.config(text=recent_questions.queue)

        conn.commit()
        conn.close()
        submitAnswerButton.config(command=lambda: next_question(question_info))
    
    submitAnswerButton = tk.Button(
        answerFrame,
        text="Mark / Show Answer",
        command=lambda: show_answer(question_info),
    )
    submitAnswerButton.grid(row=1, column=0, pady=20, padx=50, ipadx=20, ipady=20)


    


def add_image():
    global file_question_no, choose_file_image_text, image_frame
    window = tk.Toplevel()
    window.geometry("700x500")
    window.focus()
    image_frame = tk.Frame(window)
    image_frame.pack()

    file_question_label = tk.Label(image_frame, text="qNo", font=30)
    file_question_label.grid(row=0, column=0, padx=20, pady=20)

    file_question_no = tk.Spinbox(image_frame)
    file_question_no.grid(row=0, column=1, padx=20, pady=20)

    choose_file_image_text = tk.Label(image_frame, text="File: ", font=30)
    choose_file_image_text.grid(row=1, column=0, padx=20, pady=20)

    choose_file_image_button = tk.Button(
        image_frame, text="Choose File", command=get_file_path_image
    )
    choose_file_image_button.grid(row=1, column=1, padx=20, pady=20, ipady=15, ipadx=15)

    submit_image_button = tk.Button(
        image_frame, text="Submit", command=submit_add_image
    )
    submit_image_button.grid(row=2, column=0, padx=20, pady=20, ipady=15, ipadx=15)


def get_file_path_image():
    global questionNo, original_image_filepath, new_image_filepath
    original_image_filepath = askopenfilename() #Get filepath for image and display name
    questionNo = file_question_no.get()
    newText = "File: " + original_image_filepath
    choose_file_image_text.config(text=newText)
    new_image_filepath = (
        "images/" + questionNo + ".png"
    )


def submit_add_image():
    os.rename(original_image_filepath, new_image_filepath) #Change name and location of image file to local images folder
    choose_file_image_text.config(text="File: ")
    file_question_no.delete(0, END)
    submitted_text = "Received qImg for Q" + questionNo
    submitted = tk.Label(image_frame, text=submitted_text)
    submitted.grid(row=2, column=1)


def add_note():
    global choose_file_note_text, file_note_name, note_frame, submitted
    window = tk.Toplevel()
    window.geometry("700x500")
    window.focus()
    note_frame = tk.Frame(window)
    note_frame.pack()

    file_note_label = tk.Label(note_frame, text="New name:", font=30)
    file_note_label.grid(row=0, column=0, padx=20, pady=20)

    file_note_name = tk.Entry(note_frame)
    file_note_name.grid(row=0, column=1, padx=20, pady=20)

    choose_file_note_text = tk.Label(note_frame, text="File: ", font=30)
    choose_file_note_text.grid(row=1, column=0, padx=20, pady=20)

    choose_file_note_button = tk.Button(
        note_frame, text="Choose File", command=get_file_path_note
    )
    choose_file_note_button.grid(row=1, column=1, padx=20, pady=20, ipady=15, ipadx=15)

    submit_note_button = tk.Button(note_frame, text="Submit", command=submit_add_note)
    submit_note_button.grid(row=2, column=0, padx=20, pady=20, ipady=15, ipadx=15)

    submitted = tk.Label(note_frame, text='')
    submitted.grid(row=2, column=1)


def get_file_path_note():
    global original_note_filepath, new_note_filepath
    original_note_filepath = askopenfilename(defaultextension=".txt") #get filepath for text file and display it
    if original_note_filepath == "":
        pass
    elif original_note_filepath[original_note_filepath.index('.'):] != ".txt":
        submitted.config(text="Error: invalid file type, use a .txt file.")
        original_note_filepath = ""
    else:
        submitted.config(text="")
        text_file_name = file_note_name.get()
        newText = "File: " + original_note_filepath
        choose_file_note_text.config(text=newText)
        new_note_filepath = (
            "notes/" + text_file_name + ".txt"
        )


def submit_add_note():
    global original_note_filepath
    if file_note_name.get() == "":
        new_note_filepath = "notes/" + os.path.basename(original_note_filepath)
    os.rename(original_note_filepath, new_note_filepath) #Change name and location of text file to local notes folder
    choose_file_note_text.config(text="File: ")
    file_note_name.delete(0, END)
    submitted.config(text="Received notes.")
    original_note_filepath = ""



def add_topic_menu():
    global topic_name_entry, submitted_label
    window = tk.Toplevel()
    window.geometry("700x500")
    window.focus()
    topic_frame = tk.Frame(window)
    topic_frame.pack()

    topic_details_frame = tk.LabelFrame(topic_frame, text="Topic Details")
    topic_details_frame.grid(row=0, column=0, ipady=10, ipadx=10)

    topic_name_label = tk.Label(topic_details_frame, text="topicName")
    topic_name_label.grid(row=0, column=0, pady=10, padx=10)

    topic_name_entry = tk.Entry(topic_details_frame)
    topic_name_entry.grid(row=0, column=1, pady=10, padx=10)

    submit_frame = tk.LabelFrame(topic_frame, text="Submit")
    submit_frame.grid(row=1, column=0)

    topic_submit_button = tk.Button(
        submit_frame, text="Submit Topic", command=add_topic
    )
    topic_submit_button.grid(row=0, column=0, pady=10, padx=10)
    submitted_label = tk.Label(submit_frame, text='Submitted Topic: ')
    submitted_label.grid(row=0, column=1, pady=10, padx=10)


def add_topic():
    topicName = topic_name_entry.get()  
    if len(topicName) < 4 or len(topicName) > 40: #Make sure topic name is between 4 and 40 characters (inclusive)
        submitted_label.config(text="Topic Name must be between 4 and 40 characters (inclusive)")
    else:
        submitted_text = 'Submitted Topic: ' + topicName
        submitted_label.config(text=submitted_text)
        conn = sqlite3.connect("MathsPlatformStorage.db")
        cursor = conn.cursor()

        count_query = "SELECT COUNT(*) FROM tblTopic"
        cursor.execute(count_query)
        result = cursor.fetchone()
        totalTopics = result[0] #Get the number of topics in tblTopic
        topicNo = totalTopics + 1

        insert_topic_query = """INSERT INTO tblTopic(topicNo, topicName, correctQs, wrongQs, score)
        VALUES (?, ?, ?, ?, ?)"""
        insert_topic_tuple = (topicNo, topicName, 1, 1, 1) 
        cursor.execute(insert_topic_query, insert_topic_tuple) #Insert new topic with performance values into tblTopic
        conn.commit()
        conn.close()


def view_progress_menu():
    global topic_options, correct_label, topic_label, wrong_label, score_label, topics
    conn = sqlite3.connect('MathsPlatformStorage.db')
    cursor = conn.cursor()
    cursor.row_factory = lambda cursor, row: row[0]
    topics = cursor.execute('SELECT topicName FROM tblTopic').fetchall() #get topics list
    conn.close()

    window = tk.Toplevel()
    window.geometry("700x500")
    window.focus()
    progress_frame = tk.Frame(window)
    progress_frame.pack()

    choose_topic_frame = tk.LabelFrame(progress_frame)
    choose_topic_frame.grid(row=0, column=0)

    topic_progress_frame = tk.LabelFrame(progress_frame)
    topic_progress_frame.grid(row=1, column=0)

    topic_options = ttk.Combobox(choose_topic_frame, values=topics)
    topic_options.grid(row=0, column=0, padx=10, pady=10)

    view_button = tk.Button(choose_topic_frame, text='View Progress', command=get_progress)
    view_button.grid(row=1, column=0, padx=10, pady=10)

    topic_label = tk.Label(topic_progress_frame, text='Topic: ',font=16)
    topic_label.grid(row=0, column=0, padx=10, pady=10)
    correct_label = tk.Label(topic_progress_frame, text='Correct answers: ',font=16)
    correct_label.grid(row=1, column=0, padx=10, pady=10)
    wrong_label = tk.Label(topic_progress_frame, text='Wrong answers: ',font=16)
    wrong_label.grid(row=2, column=0, padx=10, pady=10)
    score_label = tk.Label(topic_progress_frame, text='Total score: ',font=16)
    score_label.grid(row=3, column=0, padx=10, pady=10)
    


def get_progress():
    topic = topic_options.get()
    topic_label.config(text=('Topic: '+topic))
    if topic == "": #Account for the blank input
        correct_label.config(text="Enter a valid topic.")
    elif topic not in topics: #Make sure topic inputted exists
        correct_label.config(text="Topic doesn't exist.")
        wrong_label.config(text="You can add it with the Add Topic menu")
        score_label.config(text="Go to the File submenu in the navigation bar")

    else:
        conn = sqlite3.connect('MathsPlatformStorage.db')
        cursor = conn.cursor()
        topic_scores_statement = 'SELECT correctQs, wrongQs, score FROM tblTopic WHERE topicName = "' + topic + '"' #Get performance stats for the topic inputted
        cursor.execute(topic_scores_statement)
        topic_scores = cursor.fetchone()
        conn.close()

        correct_label.config(text=('Correct answers: '+str(topic_scores[0])))
        wrong_label.config(text=('Wrong answers: '+str(topic_scores[1])))
        score_label.config(text=('Total score: '+str(topic_scores[2])))

def view_notes_menu():
    global notes_list, note_textbox, notes, note_info
    window = tk.Toplevel()
    window.geometry("900x600")
    window.focus()

    notes_list = tk.Listbox(window, selectmode=SINGLE, font=20)
    notes = os.listdir('notes') #Get all the text file names from notes folder
    for x in notes:
        notes_list.insert(END, x)
    notes_list.pack(side = RIGHT, fill=BOTH)

    scrollbar = tk.Scrollbar(window)
    scrollbar.pack(side=RIGHT, fill=BOTH)
    notes_list.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=notes_list.yview)

    view = tk.Button(window, text='Load Note', command=view_note)
    view.pack(pady=15)
    note_textbox = tk.Text(window)
    note_textbox.pack()
    save = tk.Button(window, text='Save Note', command=save_note)
    save.pack(pady=15)
    note_info = tk.Label(window, text='', font=20)
    note_info.pack()

def view_note():
    global directory, note_textbox
    if notes_list.curselection() == ():
        note_info.config(text="Error: no file input.") #Make sure a file is selected when loading a note
    else:
        index_selected = int((notes_list.curselection())[0])
        note_selected = notes[index_selected]
        if note_selected[note_selected.index('.'):] != '.txt':
            note_info.config(text="Error: file type not valid.")
        else:
            directory = "notes/" + note_selected
            x = open(directory, "r") #Open the text file

            text = x.read() #Get the file contents
            x.close()
            text = textwrap.fill(text,80)
            note_textbox.delete(1.0, END)
            note_textbox.insert(END, text) #Write the text to the input box
            note_info_text = "Note loaded: " + note_selected
            note_info.config(text=note_info_text)

def save_note():
    new_text = note_textbox.get("1.0", "end-1c")
    x = open(directory, "w")
    try:
        x.write(new_text) #Write inputted text to the file and save it
        x.close()
        note_info_text = "Note saved: " + directory[6:]
        note_info.config(text=note_info_text)
    except:
        note_info.config(text="Error: enter valid characters.") #Account for invalid character inputs

def delete_question_menu():
    global question_number_entry, deleted_label, questions_list
    window = tk.Toplevel()
    window.geometry("900x600")
    window.focus()
    
    conn = sqlite3.connect('MathsPlatformStorage.db')
    cursor = conn.cursor()

    questions_list = tk.Listbox(window, selectmode=SINGLE, font=20)
    cursor.execute('SELECT qNo, qText FROM tblQuestion')
    questions = cursor.fetchall()
    for x in range(len(questions)):
        questions_list.insert(END, str(questions[x][0]) + ". " + questions[x][1])
    questions_list.pack(side=RIGHT, fill=BOTH, ipadx=100)

    conn.close()

    scrollbar = tk.Scrollbar(window)
    scrollbar.pack(side=RIGHT, fill=BOTH)
    questions_list.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=questions_list.yview)

    question_frame = tk.Frame(window)
    question_frame.pack()

    question_delete_frame = tk.LabelFrame(question_frame, text="Delete Question")
    question_delete_frame.grid(row=0, column=0, ipady=10, ipadx=10)

    question_number_label = tk.Label(question_delete_frame, text="Question Number")
    question_number_label.grid(row=0, column=0, pady=10, padx=10)

    question_number_entry = tk.Entry(question_delete_frame)
    question_number_entry.grid(row=0, column=1, pady=10, padx=10)

    delete_frame = tk.LabelFrame(question_frame, text="Confirm")
    delete_frame.grid(row=1, column=0)

    question_delete_button = tk.Button(
        delete_frame, text="Delete", command=delete_question
    )
    question_delete_button.grid(row=0, column=0, pady=10, padx=10)
    deleted_label = tk.Label(delete_frame, text='Deleted Question: ')
    deleted_label.grid(row=0, column=1, pady=10, padx=10)

def delete_question():
    question_num_delete = int(question_number_entry.get())
    conn = sqlite3.connect('MathsPlatformStorage.db')
    cursor = conn.cursor()

    count_query = "SELECT MAX(qNo) FROM tblQuestion"
    cursor.execute(count_query)
    result = cursor.fetchone()
    largest_qNo = result[0]

    if question_num_delete > 0 and question_num_delete <= largest_qNo:
        cursor.execute('DELETE FROM tblQuestion WHERE qNo='+str(question_num_delete))
        deleted_label_text = "Deleted Question: " + str(question_num_delete)
        deleted_label.config(text=deleted_label_text)
        questions_list.delete(0, tk.END)
        conn.commit()

        if question_num_delete != largest_qNo:
            for x in range(question_num_delete+1, largest_qNo+1):
                cursor.execute('UPDATE tblQuestion SET qNo='+str(x-1)+' WHERE qNo='+str(x))
        conn.commit()

        cursor.execute('SELECT qNo, qText FROM tblQuestion')
        questions = cursor.fetchall()
        for x in range(len(questions)):
            questions_list.insert(END, str(questions[x][0]) + ". " + questions[x][1])

    else:
        deleted_label.config(text='Deleted Question: Invalid qNo')
    conn.close()
    question_number_entry.delete(0, tk.END)
    


def play_game():
    pass
    #exe_path = 'jimmy.exe'
    #subprocess.run([exe_path])

window = tk.Tk()
window.geometry("700x500")
window.title("Maths Revision Tool")

menubar = tk.Menu(window)
window.config(menu=menubar)
operationMenu = tk.Menu(menubar, tearoff="off")
gameMenu = tk.Menu(menubar, tearoff="off")

menubar.add_cascade(label="File", menu=operationMenu)
menubar.add_cascade(label="Game", menu=gameMenu)

operationMenu.add_command(label="Add Question", command=add_question_menu)
operationMenu.add_separator()
operationMenu.add_command(label="Add Notes (.txt)", command=add_note)
operationMenu.add_separator()
operationMenu.add_command(label="Add Image (.jpeg/.png)", command=add_image)
operationMenu.add_separator()
operationMenu.add_command(label="Add Topic", command=add_topic_menu)
operationMenu.add_separator()
operationMenu.add_command(label="Delete Question", command=delete_question_menu)

gameMenu.add_command(label="Play Game", command=play_game)

main_frame = tk.Frame(window)
main_frame.pack()

title = tk.Label(main_frame, text="Maths Revision Platform", font=40)
title.grid(row=0, column=0)

info_label = tk.Label(
    main_frame,
    text="View the File dropdown menu in the top left for additional features",
    font=25,
)
info_label.grid(row=4, column=0)

answer_question_button = tk.Button(
    main_frame, text="Answer Question", command=answer_question_menu
)
answer_question_button.grid(row=1, column=0)

view_progress_button = tk.Button(main_frame, text="View Topic Progress", command=view_progress_menu)
view_progress_button.grid(row=2, column=0)

view_notes_button = tk.Button(main_frame, text="View/Edit Notes", command=view_notes_menu)
view_notes_button.grid(row=3, column=0)

for widget in main_frame.winfo_children():
    widget.grid_configure(padx=20, pady=14, ipadx=15, ipady=15)

window.mainloop()