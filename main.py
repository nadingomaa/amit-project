#Import Liberaries
import numpy as np
from flask import Flask, request,  render_template
from werkzeug.utils import secure_filename
import os
from nltk.stem import PorterStemmer
import re
import nltk
nltk.download('stopwords')
import nltk
nltk.download('punkt')
from nltk.corpus import stopwords

stop_words=stopwords.words('arabic')

from ArabicOcr import arabicocr

from text_classification import *

flask_app_=Flask(__name__ , template_folder='templates')




upload_folder = os.path.join('static', 'uploads')

flask_app_.config['UPLOAD'] = upload_folder


@flask_app_.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['img']
        filename = 'exam.jpg'
        file.save(os.path.join(flask_app_.config['UPLOAD'], filename))
        img = os.path.join(flask_app_.config['UPLOAD'], filename)
        return render_template('home.html', img=img)
    return render_template('home.html')

def clean_text(text):
    #clean text
    text=re.sub('(#|@)\w*',"",text)# \w [a-z|A_Z|0-9|_] #remoce hashtage ,username
    text=re.sub("https?:\/\/\S+","",text) #remove hyperlink
    text=re.sub("'(\?|!)+"," ",text) #remve (?!)
    text=re.sub("\s\d+\s","",text) # 33
    text=re.sub("(\.|\,)+","",text) #remove . ,
    text=re.sub("^\s+","",text) #remove space ^ >> start of string
    text=re.sub("\s+$","",text)#remove space  $ >> at the end of the string
    text=re.sub(":","",text)
    text=re.sub("[_:()\\\]","",text)
    text=re.sub("/'/g","",text)

    return text



def process_sentence(words):
    clean_words=[]
    for text in words:
        text=clean_text(text)
        text=nltk.word_tokenize(text) #sequncing
        c_text=[word.lower() for word in text if word.lower() not in stop_words] #remove stop wodrs & convert to lower case
        #stemming
        ps=PorterStemmer()
        clean_word=[ps.stem(word) for word in c_text]#convert word to  base
        clean_words.append(text)

    return clean_words


@flask_app_.route('/sendImage', methods=['GET', 'POST'])
def sendImage():
    image_path = './static/uploads/exam.jpg'

    out_image = 'out.jpg'
    results = arabicocr.arabic_ocr(image_path, out_image)

    words = []
    for i in range(len(results)):
        word = results[i][1]
        words.append(word)

    data = process_sentence(words)

    #print(data)
    if request.method == 'POST':
        correct_answers= request.form.get('correct_answers')
        answers_arr = correct_answers.split('/')

    student_answers=[]
    for word in data:
        for answer in answers_arr:
          if (('رموش') in word) :
             student_answers.append(answer)



    count=0
    try:
        print(student_answers[0]==answers_arr[0])
        count= count+1
    except IndexError:
        print('sorry, no 0')

    try:
        print(student_answers[1]==answers_arr[1])
        count = count + 1
    except IndexError:
        print('sorry, no 1')

    try:
        print(student_answers[2]==answers_arr[2])
        count = count + 1
    except IndexError:
        print('sorry, no 2')

    result = str(count) + '/' + str(len(answers_arr))
    success = count >= len(answers_arr)/2

    return render_template('final_result.html', result=result,success=success)


@flask_app_.route('/getMessage', methods=['POST'])
def getMessage():

    user_message=request.form.get('msg')
    print(user_message)

    clean_message =process_sentence([user_message])
    pred = Naive_Bayes_inference(clean_message,prop_dict)
    print(pred)

    if pred[0] > 0:
        message="Happy to serve you"
        pos=True
    elif pred[0] == 0:
        message="We couldn't decide what you think"
        pos=False
    else:
        message="Sorry, we will work to improve the service"
        pos=False


    return render_template('final_result.html',message=message,pos=pos)


if __name__ == '__main__':
    flask_app_.run(debug=True)


