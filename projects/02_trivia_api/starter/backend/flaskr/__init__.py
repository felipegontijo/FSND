import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, query):
  """Return paginated questions"""
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  current_questions = query[start:end]

  return current_questions

def create_app(test_config=None):
  """Create and set up the Flask app"""
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resources={r'/api/*': {'origins': '*'}})

  @app.after_request
  def after_request(response):
    """Define CORS headers"""
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE')
    return response

  @app.route('/categories')
  def get_categories():
    """GET all categories"""
    categories = Category.query.all()
    formatted_categories = {category.id: category.type for category in categories}

    return jsonify({
      'success': True
      'categories': formatted_categories
    })

  @app.route('/questions')
  def get_paginated_questions():
    """GET a list of paginated questions"""
    questions = Question.query.all()
    formatted_questions = [question.format() for question in questions]
    current_questions = paginate_questions(request, formatted_questions)

    categories = {category.id: category.type for category in Category.query.all()}

    if len(current_questions) == 0:
      abort(404)
    
    return jsonify({
      'success': True
      'questions': current_questions,
      'total_questions': len(questions),
      'categories': categories,
      'current_category': None
    })

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    """DELETE a question from the database"""
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

    repeated_question = Question.query.filter(Question.question == question).one_or_none()

    if repeated_question is None:
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
    else:
      abort(422)

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    """Search questions in database with partial string matching"""
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

  @app.route('/categories/<int:category_id>/questions')
  def get_categorized_questions(category_id):
    """GET questions of a certain category"""
    category = Category.query.get(category_id)
    
    if category is None:
      abort(404)
    else:
      try:
        questions = Question.query.filter(Question.category == category.id)
        formatted_questions = [question.format() for question in questions]

        total_questions = len(formatted_questions)
      except:
        abort(500)
      finally:
        return jsonify({
          'success': True,
          'questions': formatted_questions,
          'total_questions': total_questions,
          'current_category': {category.id: category.type}
        })

  @app.route('/quizzes', methods=['POST'])
  def get_quiz_question():
    """Retrieve a brand new quiz question within a category"""
    
    previous_questions = request.get_json()['previous_questions']
    quiz_category = request.get_json()['quiz_category']

    try:

      if quiz_category['id'] != 0:
        new_questions = Question.query.filter(Question.category == quiz_category['id']).filter(~Question.id.in_(previous_questions))
      else:
        new_questions = Question.query.filter(~Question.id.in_(previous_questions))
      
      formatted_questions = [question.format() for question in new_questions]

      if (len(formatted_questions) > 0):
        random_question = random.choice(formatted_questions)
        return jsonify({
          'success': True,
          'question': random_question
        })
      else:
        return jsonify({
          'success': True
        })
    except:
      abort(500)

  @app.errorhandler(400)
  def bad_request(error):
    """Handle a bad request"""
    return jsonify({
      'error': 400,
      'message': 'bad request'
    }), 400
  
  @app.errorhandler(404)
  def not_found(error):
    """Handle resource not found"""
    return jsonify({
      'error': 404,
      'message': 'resource not found'
    }), 404
  
  @app.errorhandler(422)
  def unprocessable(error):
    """Handle unprocessable request"""
    return jsonify({
      'error': 422,
      'message': 'unprocessable'
    }), 422
  
  @app.errorhandler(500)
  def internal_error(error):
    """Handle internal server error"""
    return jsonify({
      'error': 500,
      'message': 'internal server error'
    }), 500
  
  return app

    