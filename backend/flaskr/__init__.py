import os
import sys
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
                'success': True,
                'deleted_id': question_id
            })
        except:
            abort(422)
    

    @app.route('/questions/add', methods=['POST'])
    def create_new_question():
        body = request.get_json()
        new_question =  body.get('question', None)
        new_answer =  body.get('answer', None)
        new_category =  body.get('category', None)
        new_difficulty =  body.get('difficulty', None)

        try:
            question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
            question.insert()
            return jsonify({
                'success': True,
                'created': question.id,
                'total_question': len(Question.query.all())
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
            selection = Question.query.filter(Question.category==str(category_id)).all()
            curr_questions = paginated_func(request, selection)
        
            return jsonify({
                'success': True,
                'category': category_id,
                'questions': curr_questions
            })

        else: 
            abort(404)
    
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:

            body = request.get_json()
            quiz_category = body.get('quiz_category', None)
            previous_question = body.get('previous_questions', None)
            cat_id = quiz_category['id']
    

            if cat_id == 0:
                selections = Question.query.all()

            else:
                selections = Question.query.filter(Question.category==cat_id).all()

            
            ids = [question.id for question in selections]
            current_ids = list(set(ids) - set(previous_question))

            if len(current_ids) == 0:
                 current_question = ''
            else:

                id_random = int(random.choice(ids))
                current_question = Question.query.filter(Question.id == id_random).one_or_none()

                return jsonify({
                    'success':True,
                    'question': {
                        'id': current_question.id,
                        'question': current_question.question,
                        'answer': current_question.answer
                    }
                    
                })
                
        except:
            abort(422)
   

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
   
    @app.errorhandler(500)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Server error'
        }), 500 
    return app

