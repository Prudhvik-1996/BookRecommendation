from flask import Flask, request, session, redirect, url_for, abort, render_template, flash
import json
import requests
import io
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, DateTime, desc
import datetime
import random

app = Flask(__name__)

app.config['SECRET_KEY'] = 'PRUDHVIK'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///BookRecommendation.db'

db = SQLAlchemy(app)

print ('initiating Flask app')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'BOOK-RECOMMENDER'

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

print ('importing libraries app')

# Input data files are available in the "./data/" directory.
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def getCsvFromUrl(url):
    s=requests.get(url).content
    c=pd.read_csv(io.StringIO(s.decode('utf-8')))
    return c

# books = getCsvFromUrl("https://raw.githubusercontent.com/Prudhvik-1996/BookRecommendation/master/books.csv")
books = pd.read_csv('./data/books.csv', encoding = "ISO-8859-1")
# print(books.head())
# print(books.shape)
# print(books.columns)

# ratings = getCsvFromUrl("https://raw.githubusercontent.com/Prudhvik-1996/BookRecommendation/master/ratings.csv")
ratings = pd.read_csv('./data/ratings.csv', encoding = "ISO-8859-1")
# print(ratings.head())
# print(ratings.shape)
# print(ratings.columns)

# book_tags = getCsvFromUrl("https://raw.githubusercontent.com/Prudhvik-1996/BookRecommendation/master/book_tags.csv")
book_tags = pd.read_csv('./data/book_tags.csv', encoding = "ISO-8859-1")
# print(book_tags.head())
# print(book_tags.shape)
# print(book_tags.columns)

# tags = getCsvFromUrl("https://raw.githubusercontent.com/Prudhvik-1996/BookRecommendation/master/tags.csv")
tags = pd.read_csv('./data/tags.csv', encoding = "ISO-8859-1")
# print(tags.head())
# print(tags.shape)
# print(tags.columns)

tags_join_DF = pd.merge(book_tags, tags, left_on='tag_id', right_on='tag_id', how='inner')
# print(tags_join_DF.head())
# print(tags_join_DF.shape)
# print(tags_join_DF.columns)

tf_authors = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
tfidf_matrix_authors = tf_authors.fit_transform(books['authors'])
cosine_sim_authors = linear_kernel(tfidf_matrix_authors, tfidf_matrix_authors)
# print(cosine_sim_authors)

# Build a 1-dimensional array with book titles
titles = books['title']
indices = pd.Series(books.index, index=books['title'])

# Function that get book recommendations based on the cosine similarity score of book authors
def authors_recommendations(title):
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim_authors[idx]))
    # sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    random.shuffle(sim_scores)
    sim_scores = sim_scores[1:21]
    book_indices = [i[0] for i in sim_scores]
    return titles.loc[book_indices]

# print(authors_recommendations('The Hobbit'))

books_with_genres = pd.merge(books, tags_join_DF, left_on='book_id', right_on='book_id', how='inner')
# print(books_with_genres.head())
# print(books_with_genres.shape)

tf_genres = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
tfidf_matrix_genres = tf_genres.fit_transform(books_with_genres['tag_name'].head(10000))
cosine_sim_genres = linear_kernel(tfidf_matrix_genres, tfidf_matrix_genres)

# Function that get book recommendations based on the cosine similarity score of books tags
def genres_recommendations(title):
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim_genres[idx]))
    # sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    random.shuffle(sim_scores)
    sim_scores = sim_scores[1:21]
    book_indices = [i[0] for i in sim_scores]
    return titles.loc[book_indices]
# print(genres_recommendations('The Hobbit'))

# related to database
class LoginDetails(db.Model):
    email = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(200))
    password = db.Column(db.String(240))
    phone = db.Column(db.String(20))
    createdAt = db.Column(DateTime(), default=datetime.datetime.now)
    lastSignIn = db.Column(DateTime(),  nullable=True)

    def __init__(self, name, email, phone, password):
        self.email = email
        self.name = name
        self.password = password
        self.phone = phone

    def __repr__(self):
        return '<Entry\nEmail Id: %r\nName: %r\nPassword: %r\nPhone number: %r\n>' % (self.email, self.name, self.password, self.phone)

class Interests(db.Model):
    """docstring for Interests"""
    email = db.Column(db.String(100), primary_key=True)
    genre1 = db.Column(db.String(50))
    genre2 = db.Column(db.String(50))
    genre3 = db.Column(db.String(50))
    genre4 = db.Column(db.String(50))
    genre5 = db.Column(db.String(50))

    def __init__(self, email, genre1, genre2, genre3, genre4, genre5):
        self.email = email
        self.genre1 = genre1
        self.genre2 = genre2
        self.genre3 = genre3
        self.genre4 = genre4
        self.genre5 = genre5
        
    def __repr__(self):
        return '<Entry\nEmail Id: %r\nGenre-1:%r\nGenre-2:%r\nGenre-3:%r\nGenre-4:%r\nGenre-5:%r' % (self.email, self.genre1, self.genre2, self.genre3, self.genre4, self.genre5)

db.create_all()

def authenticate(e, p):
    details=LoginDetails.query.filter_by(email=e).all()
    if(len(details)>0):
        if details[0].password==p:
            return ""
        else: return "Incorrect Password"
    return "No Email exists"

def authenticateEmail(e):
    details=LoginDetails.query.filter_by(email=e).all()
    if(len(details)>0):
        return False
    return True

def updateLastLoggedIn(email):
    
    # details=LoginDetails.query.filter_by(email=e).all()
    # if details[0].lastSignIn 
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = (authenticate(email, password))
        if error=="":
            session['logged_in'] = True
            session['log_email'] = request.form['email']
            updateLastLoggedIn(email)
            flash("You are logged in")
            return redirect(url_for('homepage'))
        return render_template('login.html', error=error)
    try:
        if session['logged_in']==True:
            return redirect('/')
    except:
        return render_template('login.html', error="")
    return render_template('login.html', error="")

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('homepage'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        email=request.form['email']
        name=request.form['name']
        phone=request.form['phone']
        password=request.form['password']
        confirm_password=request.form['confirm_password']

        interestedGenres1=request.form['interestedGenres1']
        interestedGenres2=request.form['interestedGenres2']
        interestedGenres3=request.form['interestedGenres3']
        interestedGenres4=request.form['interestedGenres4']
        interestedGenres5=request.form['interestedGenres5']

        if(authenticateEmail(request.form['email'])):
            if request.form['password'] != request.form['confirm_password']:
                error = 'Passwords mismatch'
            else:
                newUser = LoginDetails(name,email,phone,password)
                newUserInterests = Interests(email,interestedGenres1,interestedGenres2,interestedGenres3,interestedGenres4,interestedGenres5)
                db.session.add(newUser)
                db.session.add(newUserInterests)
                print(newUser)
                print(newUserInterests)
                db.session.commit()
                return redirect(url_for('login'))
            return render_template('signup.html', error=error)
        else:
            error = 'The Email Id entered is already registered!!'
            return render_template('signup.html', error=error)
    try:
        if session['logged_in']==True:
            return redirect('/')
    except:
        return render_template('signup.html', error="")
    return render_template('signup.html', error="")
    
@app.route('/yourdetails')
def yourdetails():
    try:
        if session['logged_in']==True:
            customer = LoginDetails.query.filter_by(email=session['log_email']).one()
            return render_template('yourdetails.html',customer=customer)
        return redirect(url_for('login'))
    except:
        return redirect(url_for('login'))

# @app.route('/getAllBooks', methods=['GET', 'POST'])
def getAllBooks():
    for book in json.loads(books.to_json(orient='table'))['data']:
        if str(name).strip().lower() in str(book["title"]).strip().lower():
            return json.dumps(book)
    return name

@app.route('/test/<string:bookName>', methods=['GET'])
def test(bookName):
    return bookName

# @app.route('/recommend/author/<string:bookName>/', methods=['GET'])
def getBooksWithAuthor(bookName, start = 0, end = 10):
    return json.dumps(json.loads(authors_recommendations(bookName).to_json(orient='table'))['data'][start:end])

# @app.route('/recommend/genre/<string:bookName>/', methods=['GET'])
def getBooksWithGenre(bookName, start = 0, end = 10):
    return json.dumps(json.loads(genres_recommendations(bookName).to_json(orient='table'))['data'][start:end])

# @app.route('/getBooksByGenre/<string:genre>/start/<int:start>/end/<int:end>', methods=['GET'])
def getBooksByGenre(genre, start = 0, end = 10):
    isGenre = books_with_genres['tag_name'] == genre
    return json.dumps(json.loads(books_with_genres[isGenre].to_json(orient='table'))['data'][start:end])

# @app.route('/getBookByTitle/<string:name>', methods=['GET'])
def getBookByName(name):
    for book in json.loads(books.to_json(orient='table'))['data']:
        if str(name).strip().lower() in str(book["title"]).strip().lower():
            return json.dumps(book)
    return "{\"title\": \""+ name +"\"}"

@app.route('/book/<string:bookName>', methods=['GET'])
def getBookDetailsByName(bookName):
    try:
        if session['logged_in']==True:
            bookDetails = json.loads(getBookByName(bookName))
            print(bookDetails)
            recommendations = []

            genreRecommendations = []
            booksBasedOnGenre = json.loads(getBooksWithGenre(bookDetails["title"]))
            for eachBook in booksBasedOnGenre:
                book = json.loads(getBookByName(eachBook["title"]))
                if book:
                    genreRecommendations.append(book)


            basedOnGenre = json.loads("{\"category\": \"Recommendations based on genres\", \"list\": "+ json.dumps(genreRecommendations) + "}")


            authorRecommendations = []
            booksBasedOnAuthors = json.loads(getBooksWithAuthor(bookDetails["title"]))
            for eachBook in booksBasedOnAuthors:
                book = json.loads(getBookByName(eachBook["title"]))
                if book:
                    authorRecommendations.append(book)

            basedOnAuthors = json.loads("{\"category\": \"Recommendations based on authors\", \"list\": "+ json.dumps(authorRecommendations) + "}")

            recommendations.append(basedOnGenre)
            recommendations.append(basedOnAuthors)

            print(recommendations)

            return render_template('book.html', bookDetails = bookDetails, recommendations = json.loads(json.dumps(recommendations)))
    except:
        return render_template('book.html', bookDetails = json.loads("{\"title\": \""+ bookName +"\"}"), recommendations = json.loads("{}"))
    return bookName

@app.route('/', methods=['GET', 'POST'])
def homepage():
    try:
        if request.method == 'GET':
            if session['logged_in']==True:
                recommendationData = []
                interestedGenres = Interests.query.filter_by(email=session['log_email']).all()[0]
                
                
                genre1Recommendation = json.loads("{\"category\": \"" + interestedGenres.genre1 + "\", \"list\": "+getBooksByGenre(interestedGenres.genre1.lower()) + "}")
                # print("genre1 = " + interestedGenres.genre1 + "\n\ngenre1Recommendation: " + genre1Recommendation + "\n\n")
                
                genre2Recommendation = json.loads("{\"category\": \"" + interestedGenres.genre2 + "\", \"list\": "+getBooksByGenre(interestedGenres.genre2.lower()) + "}")
                # print("genre2 = " + interestedGenres.genre2 + "\n\ngenre2Recommendation: " + genre2Recommendation + "\n\n")
                
                genre3Recommendation = json.loads("{\"category\": \"" + interestedGenres.genre3 + "\", \"list\": "+getBooksByGenre(interestedGenres.genre3.lower()) + "}")
                # print("genre3 = " + interestedGenres.genre3 + "\n\ngenre3Recommendation: " + genre3Recommendation + "\n\n")
                
                genre4Recommendation = json.loads("{\"category\": \"" + interestedGenres.genre4 + "\", \"list\": "+getBooksByGenre(interestedGenres.genre4.lower()) + "}")
                # print("genre4 = " + interestedGenres.genre4 + "\n\ngenre4Recommendation: " + genre4Recommendation + "\n\n")
                
                genre5Recommendation = json.loads("{\"category\": \"" + interestedGenres.genre5 + "\", \"list\": "+getBooksByGenre(interestedGenres.genre5.lower()) + "}")
                # print("genre5 = " + interestedGenres.genre5 + "\n\ngenre5Recommendation: " + genre5Recommendation + "\n\n")
                

                recommendationData.append(genre1Recommendation)
                recommendationData.append(genre2Recommendation)
                recommendationData.append(genre3Recommendation)
                recommendationData.append(genre4Recommendation)
                recommendationData.append(genre5Recommendation)

                return render_template('homepage.html', recommendationData = recommendationData)
    except:
        return render_template('homepage.html', recommendationData=[])
    return render_template('homepage.html', recommendationData=[])

# if __name__ == '__main__':
# app.run(debug=True, threaded=True)
host = "localhost"
# host = "10.1.134.4"
# host = "192.168.43.202"
# host = "10.10.8.106"
port = 5000
# socketio.bind((host, port)) 
app.run(debug=True, host=host, port=port, threaded=True)
# socketio.run(app, debug=True, host=host, port=port)