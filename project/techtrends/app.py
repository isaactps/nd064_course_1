import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import os
import sys
import logging
from logging import handlers

db_conn_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    global db_conn_count

    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    db_conn_count += 1
    if post != None:
        app.logger.info('%s is retrieved', post['title'])
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('PROJECT_SECRET_KEY')

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.error('Post not existent. 404 status returned')
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About Page is accessed')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    global db_conn_count

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
            connection.commit()
            connection.close()
            db_conn_count += 1
            app.logger.info('%s created', title)
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def healthcheck():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    app.logger.info('Health status request successfull')
    return response

@app.route('/metrics')
def metrics():

    global db_conn_count

    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    post_count = len(posts)
    connection.close()

    db_conn_count += 1

    response = app.response_class(
            response=json.dumps({"status":"success","data":{"db_connection_count": db_conn_count,"Number of Posts": post_count}}),
            status=200,
            mimetype='application/json'
    )

    app.logger.info('Metrics request successfull')
    return response

# start the application on port 3111
if __name__ == "__main__":

    ## stream logs to a file
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
        ]
    )
    
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    
    app.run(host='0.0.0.0', port='3111')
