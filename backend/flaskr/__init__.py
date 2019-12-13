import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import math

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# a function that returns a list of 10 questions depending on the page number
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

# a function that takes a list of questions and returns a list of the categories of the questions
def list_current_categories(questions):
  current_categories = []
  for question in questions:
    if (question['category'] not in current_categories):
      current_categories.append(question['category'])
  
  return current_categories

# a function that takes a list of Category objects as defined in models.py
# and returns a list of the names of the categories only without the ids of the categories
def list_all_categories(categories):
  categories_list = []
  for category in categories:
    categories_list.append(category.type)
  
  return categories_list

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  # setting up CORS, allowing all origins to access the API
  CORS(app, resources={r"/*": {'origins': '*'}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Headers', 'GET, PATCH, POST, DELETE, OPTIONS')
    return response

  
  # GET enpoint for fetching all categories
  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()

    categories_list = []
    for category in categories:
      categories_list.append(category.type)
    
    return jsonify({
      'success': True,
      'categories': list_all_categories(categories)
    })
  

  # GET enpoint for fetching 10 questions from all the questions stored on the database.
  # The questions are chosen depending on the page number, for example, if we have a total
  # of 25 questions stored on the database, and the user is viewing the 2nd page of questions,
  # they will be viewing questions 11-20
  @app.route('/questions')
  def get_questions():
    questions = Question.query.all()
    
    page = request.args.get('page', 1, type=int)
    if page > math.ceil(len(questions) / 10.0):
      abort(404)

    body = request.get_json()
    if body:
      abort(400)

    current_questions = paginate_questions(request, questions)
    current_categories = list_current_categories(current_questions)
    all_categories = list_all_categories(Category.query.all())

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(questions),
      'categories': all_categories,
      'current_category': current_categories
    })

  # DELETE enpoint for deleting a question using its id
  @app.route('/questions/<question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.filter_by(id=question_id).first()
    
    if question is None:
      abort(404)

    question.delete()

    return jsonify({
      'success': True,
      'message': 'question deleted'
    })
    
  # POST endpoint for handeling requests for posting a new question
  # or searching the questions already on the data base using a search term
  @app.route('/questions', methods=['POST'])
  def post_question():
    body = request.get_json()

    if 'searchTerm' in body and body['searchTerm'] is not None:
      search_term = body['searchTerm']
      questions = Question.query.all()
      filtered_questions = []
      for question in questions:
        if search_term.lower() in question.question.lower():
          filtered_questions.append(question)

      questions_formatted = [question.format() for question in filtered_questions]

      current_categories = []
      for question in questions_formatted:
        current_categories.append(question['category'])

      return jsonify({
        'success': True,
        'questions': questions_formatted,
        'total_questions': len(questions_formatted),
        'current_category': current_categories
      })
    elif 'searchTerm' in body and body['searchTerm'] is None:
      abort(400)
    else:
      question = body['question']
      answer = body['answer']
      difficulty = body['difficulty']
      category_id = body['category']
      
      if question == '' or answer == '':
        abort(422)

      new_question = Question(question=question, answer=answer, difficulty=difficulty, category=category_id)
      new_question.insert()

      return jsonify({
        'success': True,
        'new_entry': {
          'question': question,
          'answer': answer,
          'difficulty': difficulty,
          'category': Category.query.filter_by(id=category_id).first().type
        }
        })

  # GET enpoint for getting questions based on category
  @app.route('/categories/<category_id>/questions')
  def get_questions_by_category(category_id):
    category = Category.query.filter_by(id=category_id).one_or_none()
    questions = Question.query.filter_by(category=category_id).all()
    
    if category is None:
      abort(404)

    current_questions = paginate_questions(request, questions)
    current_categories = list_current_categories(current_questions)
    all_categories = list_all_categories(Category.query.all())

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(questions),
      'categories': all_categories,
      'current_category': current_categories
    })

  # POST endoing for getting questions to play a quiz
  # the quiz is 5 questions long,
  # the questions are not repeated, and based on the user chosen category
  @app.route('/quizzes', methods=['POST'])
  def generate_quiz():
    body = request.get_json()
    
    category = int(body['quiz_category']['id']) + 1
    previous_questions = body['previous_questions']

    if body['quiz_category']['type'] == 'click':
      category_questions = Question.query.all()
    else:
      category_questions = Question.query.filter_by(category=str(category)).all()

    random_id = random.randint(1, len(category_questions))
    if (len(category_questions) != len(previous_questions)):
      while(category_questions[random_id - 1].id in previous_questions):
        random_id = random.randint(1, len(category_questions))
      
      new_question = category_questions[random_id - 1]

      return jsonify({
        'success': True,
        'previous_questions': previous_questions,
        'current_question': {
          'id': new_question.id,
          'question': new_question.question,
          'answer': new_question.answer
        }
      })
    elif (len(category_questions) == len(previous_questions)):
      return jsonify({
        'success': True,
        'current_question': {
          'id': '',
          'question': '',
          'answer': ''
        }
      })

  # error handler for "resource not found" error
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
    }), 404

  # error handler for "method not allowed" error
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False, 
        "error": 405,
        "message": "method not allowed"
    }), 405

  # error handler for "unprocessable, form data might be missing" error
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable, form data might be missing"
    }), 422

  # error handler for "bad request" error
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "bad request"
    }), 400

  return app

    