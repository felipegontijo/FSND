# Full Stack API Final Project

## Full Stack Trivia

This trivia application is a full stack web app which leverages best practices of software development and documentation to deliver a fully-functional game on the web. Users can test their knowledge on a question-per-question basis, or challenge their skills on a fully fledged game under the `Play` tab.

App functionality:

1) Display questions - both all questions and by category. Questions show the question, category and difficulty rating by default and can show/hide the answer. 
2) Delete questions.
3) Add questions, specifying question and answer text.
4) Search for questions based on a text query string.
5) Play the quiz game, randomizing either all questions or within a specific category. 

## About the Stack

The full stack application is desiged with some key functional areas:

### Backend & API

The `./backend` directory contains a complete Flask and SQLAlchemy server. The API resides in `app.py`, and Database and SQLAlchemy are set up in `models.py`.

[View the README.md within ./backend for more details, running the application and working with its API.](./backend/README.md)

### Frontend

The `./frontend` directory contains a complete React frontend to consume the data from the Flask server.

[View the README.md within ./frontend for more details.](./frontend/README.md)
