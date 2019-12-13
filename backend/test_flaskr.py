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
      
        self.new_question_1 = { 'question': 'Q1?', 'answer': 'A1', 'difficulty': 1, 'category': 1 }
        self.new_question_2 = { 'question': 'Q2?', 'answer': 'A2', 'difficulty': 2, 'category': 2 }
        self.new_question_3 = { 'question': 'Q3?', 'answer': 'A3', 'difficulty': 3, 'category': 3 }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        # self.db.session.delete(Question.query.all())
        # self.db.session.commit()
        # self.db.session.add(Question(question=self.new_question_1['question'], answer=self.new_question_1['answer'], difficulty=self.new_question_1['difficulty'], category=self.new_question_1['category']))
        # self.db.session.add(Question(question=self.new_question_2['question'], answer=self.new_question_2['answer'], difficulty=self.new_question_2['difficulty'], category=self.new_question_2['category']))
        # self.db.session.add(Question(question=self.new_question_3['question'], answer=self.new_question_3['answer'], difficulty=self.new_question_3['difficulty'], category=self.new_question_3['category']))
        # self.db.session.commit()

    
    def tearDown(self):
        """Executed after reach test"""
        questions = Question.query.all()
        for question in questions:
            question.delete()
            
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # ////////////////////////////////////////////////////////////////////////////////
    # Tests for successful and un-successful GET requests for all categories
    # ////////////////////////////////////////////////////////////////////////////////
    def test_get_categories_success(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)
    
    def test_post_categories_fail(self):
        res = self.client().post('/categories', json={'type': 3})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')
    
    # ////////////////////////////////////////////////////////////////////////////////
    # Tests for successful and un-successful GET requests for all questions
    # ////////////////////////////////////////////////////////////////////////////////
    def test_get_all_questions_success(self):
        question = Question(question=self.new_question_1['question'], answer=self.new_question_1['answer'], difficulty=self.new_question_1['difficulty'], category=self.new_question_1['category'])
        question.insert()

        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['categories']), 6)
        self.assertTrue(data['current_category'])

        question.delete()

    def test_get_all_questions_fail(self):
        question = Question(question=self.new_question_1['question'], answer=self.new_question_1['answer'], difficulty=self.new_question_1['difficulty'], category=self.new_question_1['category'])
        question.insert()

        res = self.client().get('/questions', json={'type': 3})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

        question.delete()

    # ////////////////////////////////////////////////////////////////////////////////
    # Tests for successful and un-successful GET requests for questions
    # ////////////////////////////////////////////////////////////////////////////////
    def test_get_questions_paginated_success(self):
        question = Question(question=self.new_question_1['question'], answer=self.new_question_1['answer'], difficulty=self.new_question_1['difficulty'], category=self.new_question_1['category'])
        question.insert()

        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']), 6)
        self.assertEqual(data['current_category'][0], question.category)

        question.delete()
    
    def test_get_questions_paginated_fail(self):
        question = Question(question=self.new_question_1['question'], answer=self.new_question_1['answer'], difficulty=self.new_question_1['difficulty'], category=self.new_question_1['category'])
        question.insert()

        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

        question.delete()

    # ////////////////////////////////////////////////////////////////////////////////
    # Tests for the successful and un-successful for DELETE requests for questions
    # ////////////////////////////////////////////////////////////////////////////////
    def test_delete_question_success(self):
        question = Question(question=self.new_question_1['question'], answer=self.new_question_1['answer'], difficulty=self.new_question_1['difficulty'], category=self.new_question_1['category'])
        question.insert()

        res = self.client().delete('/questions/' + str(question.id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'question deleted')
    
    def test_delete_question_fail(self):
        res = self.client().delete('/questions/1000000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # ////////////////////////////////////////////////////////////////////////////////
    # Tests for the successful and un-successful GET requests for getting questions by category
    # ////////////////////////////////////////////////////////////////////////////////
    def test_get_questions_by_category_success(self):
        question = Question(question=self.new_question_1['question'], answer=self.new_question_1['answer'], difficulty=self.new_question_1['difficulty'], category=2)
        question.insert()

        res = self.client().get('/categories/' + question.category + '/questions')   
        data = json.loads(res.data)
        
        question.delete()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], 1)
        self.assertTrue(data['categories'])
        self.assertTrue(data['current_category'])

    def test_get_questions_by_category_fail(self):
        res = self.client().get('/categories/1245/questions')   
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # ////////////////////////////////////////////////////////////////////////////////
    # Tests for the successful and un-successful POST requests for generating quizes by category
    # ////////////////////////////////////////////////////////////////////////////////
    def test_generate_quiz_success(self):
        question_1 = Question(question='Q1?', answer='A1', difficulty=1, category=1)
        question_2 = Question(question='Q2?', answer='A2', difficulty=2, category=1)
        question_1.insert()
        question_2.insert()

        res = self.client().post('/quizzes', json={
            'previous_questions':[], 
            'quiz_category':{
                'type': "Science", 
                'id': '0'
            }})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['previous_questions'], [])
        self.assertTrue(data['current_question'])
    
    def test_generate_quiz_fail(self):
        question_1 = Question(question='Q1?', answer='A1', difficulty=1, category=1)
        question_2 = Question(question='Q2?', answer='A2', difficulty=2, category=1)
        question_1.insert()
        question_2.insert()

        res = self.client().get('/quizzes', json={
            'previous_questions':[], 
            'quiz_category':{
                'type': "Science", 
                'id': '0'
            }})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')



    # ////////////////////////////////////////////////////////////////////////////////
    # Tests for the successful and un-successful POST requests for getting questions
    # usring a search term
    # ////////////////////////////////////////////////////////////////////////////////
    def test_search_questions_success(self):
        question = Question(question='Q4?', answer=self.new_question_3['answer'], difficulty=self.new_question_3['difficulty'], category=self.new_question_3['category'])
        question.insert()

        res = self.client().post('/questions', json={'searchTerm': 'Q4?'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['questions'][0]['question'], 'Q4?')
        self.assertEqual(data['total_questions'], 1)
        self.assertEqual(data['current_category'], ['3'])

        question.delete()
    
    def test_search_questions_fail(self):
        question = Question(question=self.new_question_3['question'], answer=self.new_question_3['answer'], difficulty=self.new_question_3['difficulty'], category=4)
        question.insert()

        res = self.client().post('/questions', json={'searchTerm': None})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()