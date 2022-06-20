import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
# set up the paginated Function
def paginated_func(request, selections):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    selected_pages = [selection.format() for selection in selections]
    return selected_pages[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # Setting up cors header
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, True')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE,PATCH, OPTIONS')
        return response

    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': {cat.id: cat.type for cat in categories}
        })


    @app.route('/questions')
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        current_selection = paginated_func(request, questions)
        
        if len(current_selection) == 0:
            abort(404)
        
        categories = Category.query.order_by(Category.id).all()
        return jsonify({
            'success': True,
            'questions': current_selection,
            'total_questions': len(questions),
            'categories': {cat.id: cat.type for cat in categories} 

        })


    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id==question_id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            
            return jsonify({
                'success': True
            })
        except:
            abort(422)
    

    @app.route('/questions/add', methods=['POST'])
    def new_question():
        body = request.get_json()
        new_question =  body.get('question', None)
        new_answer =  body.get('answer', None)
        new_category =  body.get('category', None)
        new_difficulty =  body.get('difficulty', None)

        try:
            question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
            question.insert()
            return jsonify({
                'success': True
            })
        except:
            abort(400)
    
    @app.route('/questions/search', methods=['POST'])
    def question_search():
        body = request.get_json()
        search_term = body.get('searchTerm', None)
        
        search_questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).order_by(Question.question).all()
        
        if search_questions:
            current_questions = paginated_func(request, search_questions)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_search_questions': len(search_questions)
            })

        else:
            abort(404)
  

    @app.route('/categories/<int:category_id>/questions')
    def question_by_category(category_id):
        category  = Category.query.filter(Category.id==category_id).one_or_none()

        if category: 
            questions = Question.query.filter(Question.category==category_id).all()
            current_questions = paginated_func(request, questions)
        
        return jsonify({
            'success': True,
            'cagegory': category.type,
            'questions': current_questions
        })
    
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        # try:

            body = request.get_json()
            quiz_category = body.get('quiz_category', None)
            previous_question = body.get('previous_question', None)
            cat_id = quiz_category['id']
            if (quiz_category is None) or (previous_question is None):
                abort(400)

            if cat_id == 0:
                selections = Question.query.filter(Question.id.notin_(previous_question)).all()

            else:
                selections = Question.query.filter(Question.id.notin_(previous_question), Question.category==cat_id).all()

            question = None
            index = random.randrange(0, len(selections))
            question = selections[index].format()
                

            return({
                'success':True,
                'question': question,
                'total_questions': len(selections)
                
            })
        # except:
        #     abort(422)
   

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Resource not found"
            }), 404
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400 
   
    return app

