import os
from flask import Flask, request, abort, jsonify
import json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

# This is importing the setup_db, Question, and Category classes from the models.py file.
from models import setup_db, Question, Category


# Set up pagination function
def paginate_questions(request,selection):
    # QUESTIONS_PER_PAGE is a constant variable that is used to set the number of questions to be
    # displayed per page.
    QUESTIONS_PER_PAGE = 10
    page =request.args.get('page',1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    current_questions = selection[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    # CORS is a Python decorator which allows cross-origin HTTP requests.
    CORS(app,resources={r"/*": {"origins": "*"}})
    


    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, true")
        response.headers.add("Access-Control-Allow-Methods", "GET, PATCH, POST, DELETE, OPTIONS")
        return response
       

# GET requests for all available categories
    @app.route('/categories',methods=['GET'])
    def getCategories():
        All_categories = Category.query.order_by(Category.id).all()
        if len(All_categories)==0:
          abort(404)
        return jsonify({
            "success":True,
            "categories":{category.id:category.type for category in All_categories},
            "total_categories": len(All_categories)

        })

#  Create an endpoint to handle GET requests for questions
#  including pagination (every 10 questions)

    @app.route('/questions', methods = ['GET'])
    def getAllQuestions():
        All_questions = Question.query.order_by(Question.id).all()
        piginated_questions = paginate_questions(request, All_questions)
        All_categories = Category.query.order_by(Category.id).all()
        if len(All_questions)== 0:
          abort(404)
        return jsonify({
            "success":True,
            "questions":[question.format() for question in piginated_questions],
            "total_questions": len(All_questions),
            "categories":{category.id:category.type for category in All_categories},
            "current_category":None
        })
    
 # Create an endpoint to DELETE question using a question ID.
    @app.route('/questions/<int:question_id>',methods=['DELETE'])
    def deleteQuestion(question_id):
       question = Question.query.get_or_404(question_id)
       result = question.delete()
       if result:
        return jsonify({
            "sucess": result,
            "deleted":question_id
        })
       else:
        abort(422)

#  Create an endpoint to POST a new question
    @app.route("/questions", methods=["POST"])
    def addQuestion():
        body = request.get_json()

        question = body.get("question", None)
        answer = body.get("answer", None)
        category = body.get("category", None)
        difficulty = body.get("difficulty", None)

        if question is None:
            abort(400)

        question = Question(question, answer, category, difficulty)
        result = question.insert()

        if result["status"]:
            return jsonify({
                "success": result["status"],
                "created": result["id"]
            })
        else:
            abort(422)

#Create a POST endpoint to get questions based on a search term.
    @app.route("/questions/search", methods=["POST"])
    def searchQuestion():
        body = request.get_json()

        search_term = body.get("search_term", None)

        All_questions = Question.query.filter(
            Question.question.ilike("%{}%".format(search_term))).order_by( Question.id).all()

        questions = paginate_questions(request, All_questions)

        if len(questions) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "questions": [question.format() for question in questions],
            "total_questions": len(All_questions),
            "current_category": None
        })




#Create a GET endpoint to get questions based on category.
    @app.route("/categories/<int:id>/questions", methods=["GET"])
    def questionsByCategory(id):
        category = Category.query.get_or_404(id)
        All_questions = Question.query.filter_by(category = id).order_by(Question.id).all()
        questions = paginate_questions(request, All_questions)

        if len(questions) == 0:
            abort(404)
        return jsonify({
            "success": True,
            "questions": [question.format() for question in questions],
            "total_questions": len(All_questions),
            "current_category": category.type
        })


# Create a POST endpoint to get questions to play the quiz.
    @app.route("/quizzes", methods=["POST"])
    def quizzes():
        body = request.get_json()

        previousQuestions = body.get("previous_questions", None)
        quizCategory = body.get("quiz_category", None)

        if (previousQuestions is None) or (quizCategory is None):
            abort(400)

        categoryId = quizCategory.get("id")

        questions = None
        if (categoryId == 0):
            questions = Question.query.filter(
                Question.id.notin_(previousQuestions)
            ).order_by(
                Question.id
            ).all()
        else:
            questions = Question.query.filter_by(
                category = categoryId
            ).filter(
                Question.id.notin_(previousQuestions)
            ).order_by(
                Question.id
            ).all()

        randomQuestion = None
        if len(questions) > 0:
            randomQuestion = random.choice(questions).format()

        return jsonify({
            "success": True,
            "question": randomQuestion
        })



# Create error handlers for all expected errors

    @app.errorhandler(400)
    def badRequest(error):
        return (
            jsonify({"success": False, "error": 400, "message": "bad request"}),
            400
        )

    @app.errorhandler(404)
    def resourceNotFound(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404
        )

    @app.errorhandler(405)
    def methodNotAllowed(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405
        )
    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422
        )

    @app.errorhandler(500)
    def internalServerError(error):
        return (
            jsonify({"success": False, "error": 500, "message": "internal server error"}),
            500
        )

    return app
