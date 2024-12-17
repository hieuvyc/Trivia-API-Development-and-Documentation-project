import os
import unittest

from flaskr import create_app
from models import db, Question, Category
from sqlalchemy import text


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "trivia_test"
        self.database_user = "mac"
        self.database_password = "postgres"
        self.database_host = "localhost:5432"
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"

        # Create app with the test configuration
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        self.new_question = {
            "question": "What is the capital of France?",
            "answer": "Paris",
            "category": "3",
            "difficulty": 1
        }

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()
            with db.engine.connect() as connection:
                connection.execute(text("DROP TABLE IF EXISTS questions CASCADE;"))
                connection.execute(text("DROP TABLE IF EXISTS categories CASCADE;"))
            db.session.commit()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        """Test GET /categories"""
        res = self.client.get('/categories')
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['categories']) > 0)

    def test_get_questions_paginated(self):
        """Test GET /questions with pagination"""
        res = self.client.get('/questions')
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['total_questions'] > 0)

    def test_404_sent_requesting_invalid_page(self):
        """Test GET /questions with invalid page"""
        res = self.client.get('/questions?page=1000')
        data = res.get_json()

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Resource not found')

    def test_delete_question(self):
        """Test DELETE /questions/<id>"""
        with self.app.app_context():
            question = Question(
                question="Will be deleted?",
                answer="Yes",
                category="3",
                difficulty=1
            )
            question.insert()
            question_id = question.id

        res = self.client.delete(f'/questions/{question_id}')
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], question_id)

        # Verify question is deleted
        with self.app.app_context():
            deleted_question = db.session.get(Question, question_id)  # Updated here
            self.assertIsNone(deleted_question)

    def test_404_delete_nonexistent_question(self):
        """Test DELETE /questions/<id> with invalid id"""
        res = self.client.delete('/questions/9999')
        data = res.get_json()

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Resource not found')

    def test_create_new_question(self):
        """Test POST /questions to create a new question"""
        res = self.client.post('/questions', json=self.new_question)
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['created'])

    def test_422_if_question_creation_fails(self):
        """Test POST /questions with incomplete data"""
        incomplete_question = {
            "question": "Incomplete question"
        }
        res = self.client.post('/questions', json=incomplete_question)
        data = res.get_json()

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_search_questions(self):
        """Test POST /questions/search to search questions"""
        search_term = {"searchTerm": "capital"}
        res = self.client.post('/questions/search', json=search_term)
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)

    def test_get_questions_by_category(self):
        """Test GET /categories/<id>/questions"""
        res = self.client.get('/categories/3/questions')
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)

    def test_404_get_questions_invalid_category(self):
        """Test GET /categories/<id>/questions with invalid id"""
        res = self.client.get('/categories/999/questions')
        data = res.get_json()

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Resource not found')

    def test_play_quiz(self):
        """Test POST /quizzes to play quiz"""
        quiz_data = {
            "previous_questions": [],
            "quiz_category": {"id": 3}
        }
        res = self.client.post('/quizzes', json=quiz_data)
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue('question' in data)

    def test_422_play_quiz_with_invalid_data(self):
        """Test POST /quizzes with invalid data"""
        res = self.client.post('/quizzes', json={})
        data = res.get_json()

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Unprocessable entity')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
