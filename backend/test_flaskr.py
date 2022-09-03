import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_user = "postgres"
        self.database_password = '7y8a1h64'
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name,self.database_user,self.database_password)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass
    def test_get_categories(self):
        response = self.client().get("/categories")
        data = response.get_json()

        All_categories = Category.query.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["All_categories"])
        self.assertEqual(data["total_categories"], len(categories))

    def test_405_post_categories(self):
        response = self.client().post("/categories", json={"type": "agriculture"})
        data = response.get_json()

        self.assertEqual(response.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")

    def test_get_questions_by_category(self):
        All_categories = Category.query.all()
        randomCategory = random.choice(All_categories)

        response = self.client().get(
            "/categories/{}/questions".format(randomCategory.id)
        )

        data = response.get_json()
        request = response.request

        totalQuestions = Question.query.filter_by(
            category = randomCategory.id
        ).all()

        questions = paginate(request, totalQuestions)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["questions"]), len(questions))
        self.assertEqual(data["total_questions"], len(totalQuestions))

    def test_404_get_questions_by_invalid_category(self):
        response = self.client().get("/categories/7/questions")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_404_get_questions_by_categories_invalid_page_limit(self):
        All_categories = Category.query.all()
        randomCategory = random.choice(All_categories)

        response = self.client().get(
            "/categories/{}/questions?page=5".format(randomCategory.id)
        )

        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_questions(self):
        response = self.client().get("/questions")

        data = response.get_json()
        request = response.request

        All_questions = Question.query.all()
        questions = paginate(request,  All_questions)

        All_categories = Category.query.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["questions"]), len(questions))
        self.assertEqual(len(data["categories"]), len(All_categories))
        self.assertEqual(data["total_questions"], len(All_questions))

    def test_404_get_questions_invalid_page_limit(self):
        response = self.client().get("/questions?page=0")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_create_questions(self):
        question = Question(
            question="what's the capital of?",
            answer="Yaounde",
            category=4,
            difficulty=2
        )

        response = self.client().post("/questions", json = question.format())
        data = response.get_json()

        createdQuestion = Question.query.get(data["created"])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertNotEqual(createdQuestion, None)
        self.assertEqual(data["created"], createdQuestion.id)

    def test_400_create_question_invalid(self):
        response = self.client().post("/questions", json = {})
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")

    def test_get_search_questions(self):
        requestData = {"search_term": "Oscar"}
        response = self.client().post("/questions/search", json=requestData)

        responseData = response.get_json()
        request = response.request

        total_questions = Question.query.filter(
            Question.question.ilike("%{}%".format(requestData["search_term"]))
        ).all()

        questions = paginate(request, total_questions)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(responseData["success"], True)
        self.assertEqual(len(responseData["questions"]), len(questions))
        self.assertEqual(responseData["total_questions"], len(total_questions))

    def test_404_search_questions_invalid_page_limit(self):
        requestData = {"search_term": "title"}
        response = self.client().post("/questions/search?page=0", json=requestData)
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_delete_question(self):
        total_questions = Question.query.all()
        randomQuestion = random.choice(total_questions)

        response = self.client().delete('/questions/{}'.format(randomQuestion.id))
        data = response.get_json()

        deletedQuestion = Question.query.filter(id == randomQuestion.id).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], randomQuestion.id)
        self.assertEqual(deletedQuestion, None)

    def test_404_delete_question_invalid(self):
        response = self.client().delete("/questions/0")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_quiz_question_by_all_categories(self):
        requestData = {
            "previous_questions": [],
            "quiz_category": { "id": 0 }
        }
        response = self.client().post("/quizzes", json=requestData)
        responseData = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(responseData["success"], True)
        self.assertTrue(responseData["question"])

    def test_400_get_quiz_question_by_invalid_request_data(self):
        requestData = {}
        response = self.client().post("/quizzes", json=requestData)
        responseData = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(responseData["success"], False)
        self.assertEqual(responseData["message"], "bad request")



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()