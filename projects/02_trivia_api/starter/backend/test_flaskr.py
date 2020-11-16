import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Who invented the telegraph?',
            'answer': 'Samuel Morse',
            'difficulty': 3,
            'category': 1
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    '''
        GET /categories
    '''
    def test_get_categories(self):
        """Test correct retrieval of all categories from database"""
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])
    
    def test_404_get_categories(self):
        """Test correct error handling for bad request"""
        res = self.client().get('/category')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'resource not found')
    
    '''
        GET /questions
    '''
    def test_get_paginated_questions(self):
        """Test correct retrieval of questions upon request"""
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))
        self.assertIsNone(data['current_category'])
    
    def test_404_get_paginated_questions(self):
        """Test correct error handling for route"""
        res = self.client().get('/question')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'resource not found')

    '''
        DELETE /questions/<question_id>
    '''
    def test_delete_question(self):
        """Test correct deletion of question from the db"""
        question = Question.query.first()
        res = self.client().delete(f'/questions/{question.id}')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
    
    def test_404_delete_question(self):
        """Test handling of deleting a non-existent question"""
        res = self.client().delete('/questions/200')

        self.assertEqual(res.status_code, 404)

    '''
        POST /questions
    '''
    # def test_add_question(self):
    #     """Test adding new question to the db"""
    #     res = self.client().post('/questions', json=self.new_question)
    #     data = json.loads(res.data)
        
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)

    # """
    #     Run the above first, then comment it out and run the one below
    #     to test correct handling of repeated question addition
    # """
    # def test_422_add_question(self):
    #     """Test handling of adding a repeated question"""
    #     res = self.client().post('/questions', json=self.new_question)
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 422)
    #     self.assertEqual(data['message'], 'unprocessable')

    '''
        Search questions
    '''
    def test_search_question(self):
        """Test searching for questions in the db"""
        res = self.client().post('/questions/search', json={'searchTerm': 'a'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertIsNone(data['current_category'])
    
    def test_search_question_none_found(self):
        """Test for search term matching no questions in db"""
        res = self.client().post('/questions/search', json={'searchTerm': '$'})
        data = json.loads(res.data)
        
        self.assertEqual(data['total_questions'], 0)
    
    '''
        GET questions by category
    '''
    def test_get_categorized_questions(self):
        """Test getting questions by certain category"""
        category = Category.query.first()
        res = self.client().get(f'/categories/{category.id}/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], {f'{category.id}': category.type})
    
    def test_404_category_not_found(self):
        """Test category not found"""
        res = self.client().get(f'/categories/10000/questions')
        
        self.assertEqual(res.status_code, 404)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()