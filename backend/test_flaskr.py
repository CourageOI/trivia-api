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
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'postgres', 'localhost:5433', self.database_name)
        setup_db(self.app, self.database_path)
        self.new_question = {"question": "Whose are you?", "answer": "Neil Gaimans", "category": 2, 'difficulty': 3}
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

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_404_sent_request_beyond_valid_page(self):
        res = self.client().get('/questions?page=200000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    # def test_delete_a_questions(self):
    #     res = self.client().delete('/questions/13')
    #     data = json.loads(res.data)
    #     question = Question.query.filter(Question.id == 13).one_or_none()

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertEqual(data['deleted_id'], 13)
    
    def test_create_new_questions(self):
        res = self.client().post('/questions/add', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        

    def test_search_questions(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'what'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_search_questions'])

    def test_questions_by_category(self):
        res = self.client().get('/categories/5/questions')
        data = json.loads(res.data)
        category = Category.query.filter(Category.id==16).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data.get('success'), True)
        self.assertEqual(data['category'], category)

    def test_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        category = Category.query.filter(Category.id==1).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data.get('success'), True)
        self.assertEqual(data['category'], 1)
        self.assertTrue(data['questions'])

    def test_quiz_with_category_and_privious_question(self):
        res = self.client().post('/quizzes', json={"previous_questions": [13], "quiz_category": {"id": "1", "type": "Science"}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data.get('success'), True)
        self.assertTrue(data['question'])

    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()