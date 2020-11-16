# Full Stack API Final Project

## Full Stack Trivia

This trivia application is the second project of Udacity's Full Stack Nanodegree program. It is a full stack web app which leverages best practices of software development and documentation to deliver a fully-functional game on the web. Users can test their knowledge on a question-per-question basis, or challenge their skills on a fully fledged game under the `Play` tab.

App functionality:

1) Display questions - both all questions and by category. Questions show the question, category and difficulty rating by default and can show/hide the answer. 
2) Delete questions.
3) Add questions, specifying question and answer text.
4) Search for questions based on a text query string.
5) Play the quiz game, randomizing either all questions or within a specific category.

The backend code follows [PEP8 style guidelines](https://www.python.org/dev/peps/pep-0008/)

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

### Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

### Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

### Running Tests

To run the tests, run

```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

## About the Stack

The full stack application is desiged with some key functional areas:

### Backend & API

The `./backend` directory contains a complete Flask and SQLAlchemy server. The API resides in `app.py`, and Database and SQLAlchemy are set up in `models.py`.

[View the README.md within ./backend for more details and API Reference.](./backend/README.md)

### Frontend

The `./frontend` directory contains a complete React frontend to consume the data from the Flask server.

[View the README.md within ./frontend for more details.](./frontend/README.md)

## Authors

[Udacity](http://udacity.com) and myself, [Felipe Gontijo](http://github.com/felipegontijo)