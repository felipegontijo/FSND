import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, query):
  """Return questions paginated"""
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  current_questions = query[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resources={r'/api/*': {'origins': '*'}})

  @app.after_request
  def after_request(response):
    """Define CORS acceptances and behavior"""
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE')
    return response

  @app.route('/categories')
  def get_categories():
    """GET /categories endpoint"""
    categories = Category.query.all()
    formatted_categories = {category.id: category.type for category in categories}

    return jsonify({
      'categories': formatted_categories
    })

  @app.route('/questions')
  def get_paginated_questions():
    """GET /questions endpoint according to page number in args"""
    questions = Question.query.all()
    formatted_questions = [question.format() for question in questions]
    current_questions = paginate_questions(request, formatted_questions)

    categories = {category.id: category.type for category in Category.query.all()}

    if len(current_questions) == 0:
      abort(404)
    
    return jsonify({
      'questions': current_questions,
      'total_questions': len(questions),
      'categories': categories,
      'current_category': None
    })

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    """DELETE /question by its ID from the database"""
    question = Question.query.filter(Question.id == question_id).first_or_404()
    try:
      question.delete()
    except:
      abort(500)
    finally:
      return jsonify({
        'success': True
      })

  @app.route('/questions', methods=['POST'])
  def add_question():
    """POST new question to the database"""
    request_data = request.get_json()

    question = request_data['question']
    answer = request_data['answer']
    difficulty = request_data['difficulty']
    category = request_data['category']

    try:
      new_question = Question(
        question=question,
        answer=answer,
        difficulty=difficulty,
        category=category
      )
      new_question.insert()
    except:
      abort(500)
    finally:
      return jsonify({
        'success': True
      })

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    """Search question in database with partial string matching"""
    search_term = request.get_json()['searchTerm']
    formatted_search_term = f'%{search_term}%'

    try:
      questions = Question.query.filter(Question.question.ilike(formatted_search_term)).all()
      formatted_questions = [question.format() for question in questions]

      total_questions = len(formatted_questions)
    except:
      abort(500)
    finally:
      return jsonify({
        'success': True,
        'questions': formatted_questions,
        'total_questions': total_questions,
        'current_category': None
      })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.errorhandler(400)
  def not_found(error):
    return jsonify({
      'error': 400,
      'message': 'bad request'
    }), 400
  
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'error': 404,
      'message': 'resource not found'
    }), 404
  
  @app.errorhandler(422)
  def not_found(error):
    return jsonify({
      'error': 422,
      'message': 'unprocessable'
    }), 422
  
  return app

    