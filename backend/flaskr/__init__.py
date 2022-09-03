import os
from flask import Flask, request, abort, jsonify
import json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category


# Set up pagination function
def paginate_questions(request,selection):
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



    @app.route('/questions', methods = ['GET'])
    def getQuestions():
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
    
    

    
    return app



