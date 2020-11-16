# Full Stack Trivia API Backend

## Introduction

This API bridges user interaction with the database, making the game possible. The requests are performed by the frontend, upon interaction by the user, and handled by this API to ensure correct behavior of the website, the game, and to ensure database validity.

## Getting Started

- Base URL: `http://localhost:5000/`
- API keys: currently this API does not require keys neither does it enforce authentication. It is currently restricted to local usage.

## Errors

The API works with regular HTTP errors. Additionally, it returns custom JSON responses for the following HTTP errors:

- 400 Bad Request
```
{
    'error': 400,
    'message: 'bad request'
}
```
- 404 Not Found
```
{
    'error': 404,
    'message': 'resource not found'
}
```
- 422 Unprocessable
```
{
    'error': 422,
    'message': 'unprocessable'
}
```
- 500 Internal Server Error
```
{
    'error': 500,
    'message': 'internal server error'
}
```

## Endpoints

#### GET /categories
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding type of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 
```
{'1' : "Science",
'2' : "Art",
'3' : "Geography",
'4' : "History",
'5' : "Entertainment",
'6' : "Sports"}
```
- Test on the terminal:
```bash
curl http://127.0.0.1:5000/categories
```

#### GET /questions
- Fetches a list of all the questions in the database, paginated
- Request Arguments: None
- Returns: A dictionary containing a list of `questions` for the current page, the number of `total_questions` in the database, a dictionary of `categories` in the database, and the `current_category`. With the following structure:
```
{
    'categories': {
        '1': 'Science',
        '2': 'Art',
        ...
    },
    'current_category': null,
    'questions': [
        {
            'answer': 'Apollo 13',
            'category': 5,
            'difficulty': 4,
            'id': 2,
            'question': 'What movie earned Tom Hanks his third straight Oscar nomination, in 1996?'
        },
        {
            ...
        },
        ...
    ],
    'total_questions': 19
}
```
- Test on the terminal:
```bash
curl http://127.0.0.1:5000/questions
```

#### DELETE /questions/<int:question_id>
- Deletes a question from the database by its ID
- Request Arguments: the to-be-deleted question's ID directly in the URI
- Returns: A success message:
```
{
    'success': True
}
```
- Test on the terminal:
```bash
curl -X DELETE http://127.0.0.1/questions/2
```

#### POST /questions
- Adds a new question to the database. Will reject if the question already exists!
- Request Arguments:
```
{
    'question': 'string: The question to be added',
    'answer': 'string: The answer to the question',
    'difficulty': int: How difficult is this question, from 1 to 5,
    'category': int: ID of the category of this question
}
```
- Returns: A success message:
```
{
    'success': True
}
```
- Test on the terminal:
```bash
curl -X POST -H "Content-Type: application/json" \
    -d '{"question":"Who came up with the Theory of Relativity?","answer":"Albert Einstein", "difficulty": 2, "category": 1}' \
    http://127.0.0.1/questions
```

#### POST /questions/search
- Searches for questions that match the string provided, even partially
- Request Arguments:
```
{
    'searchTerm': 'string: The term to match questions against'
}
```
- Returns: Paginated questions matched, along with relevant info for the frontend:
```
{
    'success': True,
    'questions': [a list of the questions that matched the searchTerm],
    'total_questions': int: How many questions were matched, for pagination purposes,
    'current_category': None
}
```
- Test on the terminal:
```bash
curl -X POST -H "Content-Type: application/json" \
    -d '{"searchTerm": "who"}' \
    http://127.0.0.1/questions/search
```

#### GET /categories/<int:category_id>/questions
- Fetches all questions in a category
- Request Arguments: the desired category's ID to fetch questions from, in the request URI
- Returns: Paginated questions of the requested category, along with relevant info for the frontend:
```
{
    'success': True,
    'questions': [a list of questions of the requested category],
    'total_questions': int: the number of questions in the requested category,
    'current_category': {category.id: category.type}
}
```
- Test on the terminal:
```bash
curl http://127.0.0.1/categories/1/questions
```

#### POST /quizzes
- Fetches a new, random question of the specified category for the ongoing quiz
- Request Arguments: Use id of 0 for ALL categories:
```
{
    'previous_questions': [a list of the previous questions played in the current quiz],
    'quiz_category': {'category.id': 'category.type'} --> ID and Type of the current quiz's category
}
```
- Returns:
```
{
    'success': True,
    'question': {a random question}
}
```
- Test on the terminal:
```bash
curl -X POST -H "Content-Type: application/json" \
    -d '{"previous_questions": [], "quiz_category": {"1": "Science"}}' \
    http://127.0.0.1/quizzes
```