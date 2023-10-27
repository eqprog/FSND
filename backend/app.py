import os
from flask import Flask, request, abort, jsonify
from models import setup_db
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Forum, Thread, Page, Post, User
from auth import AuthError, requires_auth, get_token_auth_header, verify_decode_jwt


def create_app(test_config=None):

    app = Flask(__name__)
    if test_config is None:
        with app.app_context():
            setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/admin/create/forum', methods=['POST'])
    @requires_auth('admin')
    def create_forum(jwt):
        """
        Creates a new Forum
        """
        response = {}
        try:
            data = request.get_json()
            if len(Forum.query.filter(Forum.name == data.get('name')).all()) > 0:
                response = {
                    'status': 'FAILURE',
                    'message': 'A forum with that name already exists!'
                }
            else:
                new_forum = Forum(**data)
                new_forum.insert()
                response = {
                    'status': 'SUCCESS',
                    'message': 'Forum successfully created'
                }
        except Exception as e:
            print(e)
            abort(500)
        return jsonify(response)
    
    @app.route('/admin/users', methods=['GET'])
    @requires_auth('admin')
    def get_user_list(jwt):
        print(jwt)
        """
        Gets user list for admin portal
        """
        users = [user.format() for user in User.query.all()]
        print(jsonify(users))
        print(users)
        return {
            'status': 'SUCCESS',
            'users': users
        }
    
    @app.route('/admin/user', methods=['POST'])
    @requires_auth('admin')
    def create_user(jwt):
        """
        Creates a new user
        """
        data = request.get_json()
        id = data['id']
        name = data['name']
        user = User(id=id, name=name)
        user.insert()
        return jsonify({ 'status': 'SUCCESS'})
    
    @app.route('/admin/ban-user', methods=['POST'])
    @requires_auth('admin')
    def ban_user():
        data = request.get_json()
        user = User.query.get(data.get('id'))
        if not user:
            return {
                'status': 'FAILURE',
                'message': 'User does not exist!'
            }
        type = data.get('type')
        if type == 'REMOVE':
            type = 'NORMAL'
        status_set = user.set_status(data.get('type'))
        if data.get('duration'):
            user.set_probation(data.get('duration'))
        user.update()
        return {
            'status': 'SUCCESS',
            'message': 'User Status updated!'
        }

    @app.route('/', methods=['GET'])
    def get_forums():
        forums = [forum.format() for forum in Forum.query.all()]
        return {
            'status': 'SUCCESS',
            'forums': forums
        }
    @app.route('/forum/<int:forum_id>', methods=['GET'])
    def get_forum(forum_id):
        forum = Forum.query.get(forum_id)
        print(forum.threads)
        for thread in forum.threads:
            if (thread.pages):
                print (thread.id, thread.pages)
        threads = [thread.format() for thread in forum.format_threads()['threads']]
        return { 
            'status': 'SUCCESS',
            'forum': forum.format(),
            'threads': threads or []
        }
    
    @app.route('/forum/<int:forum_id>', methods=['POST'])
    @requires_auth('post:thread')
    def create_thread(jwt, forum_id):
        """
        Creates a forum thread in the specified forum
        """
        data = request.get_json()
        print(jwt)
        user_id = jwt['user_id']
        print(user_id)
        print(data)
        thread = Thread(forum_id=forum_id, title=data['title'], user_id=user_id)
        print(thread)
        thread.insert()

        add_post(thread, user_id, data['content'])
        # Create thread
        # Create page
        # Create post
        # data = request.get_json()
            # title
            # content (base64)
            # - get thread id
            # create page with thread id
        return {
            'status': 'SUCCESS',
            'thread': thread.get_page_posts(1)
        }

    
    def create_page(thread):
        page_number = len(thread.pages) + 1
        new_page = Page(thread_id=thread.id, page_number=page_number)
        new_page.insert()
        return new_page
    
    def add_post(thread, user_id, content):
        page = None
        len_pages = len(thread.pages)
        if len_pages == 0:
            page = create_page(thread)
        else:
            page = thread.pages[len_pages - 1]
        
        post = Post(user_id=user_id, page_id=page.id, content=content)
        post.insert()

    @app.route('/threads/<int:thread_id>', methods=['GET'])
    def get_thread(thread_id):
        thread = Thread.query.get(thread_id)
        if thread:
            return {
                'status': 'SUCCESS',
                'thread': thread.format()
            }
        else:
            abort(404)
        

    @app.route('/threads/<int:thread_id>/<int:page_number>', methods=['GET'])
    def get_thread_page(thread_id, page_number):
        thread = Thread.query.get(thread_id)
        page = thread.get_page_posts(page_number)
        users = {}
        for post in page['posts']:
            if post['user_id'] not in users.keys():
                users[post['user_id']] = User.query.filter(User.id == post['user_id']).one().name
            post['user_name'] = users[post['user_id']] 
            print(users)
        return {
            'status': 'SUCCESS',
            'page': page
        }
    
    @app.route('/threads/<int:thread_id>', methods=['POST'])
    @requires_auth('post:post')
    def create_post(jwt, thread_id):
        data = request.get_json()
        user_id = jwt['user_id']
        content = data['content']
        thread = Thread.query.get(thread_id)
        page = thread.pages[-1]
        if len(page.posts) + 1 > 40:
            create_page(thread)
        add_post(thread, user_id, content)
        return {
            'status': 'SUCCESS',
            'thread': thread.format()
        }
    
    @app.route('/threads/<int:thread_id>', methods=['PATCH'])
    @requires_auth('edit:post')
    def edit_post(jwt, thread_id):
        data = request.get_json()
        print(jwt)
        user_id = jwt['user_id']
        post_id = data['post_id']
        content = data['content']
        post = Post.query.get(post_id)
        if post is not None and (jwt['admin'] or (user_id is not None and post['user_id'] == user_id)):
            post.content = content
            post.update()
            return {
                'status': 'SUCCESS',
            }
        else:
            raise AuthError(400)
    @app.route('/threads/<int:thread_id>', methods=['DELETE'])
    @requires_auth('delete:post')
    def delete_post(jwt, thread_id):
        data = request.get_json()
        user_id = jwt['user_d']
        post_id = data['post_id']
        post = Post.query.get(post_id)
        if post is not None and (jwt['admin'] or (user_id is not None and post['user_id'] == user_id)):
            post.delete()
            return {
                'status': 'SUCCESS'
            }
        else:
            raise AuthError(400)

    # Error Handling
    @app.errorhandler(422)
    def unprocessable(error):
        '''
            Handles HTTP 422 status code
            Arguments
                error -- Error information
        '''
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422


    '''
    @TODO implement error handlers using the @app.errorhandler(error) decorator
        each error handler should return (with approprate messages):
                jsonify({
                        "success": False,
                        "error": 404,
                        "message": "resource not found"
                        }), 404

    '''

    '''
    @TODO implement error handler for 404
        error handler should conform to general task above
    '''
    @app.errorhandler(404)
    def page_not_found(error):
        '''
            Handles HTTP 404 status code
            Arguments
                error -- Error information
        '''
        return error_message(404, 'resource not found!')

    '''
    @TODO implement error handler for AuthError
        error handler should conform to general task above
    '''
    @app.errorhandler(401)
    def unauthorized(error):
        '''
            Handles HTTP 401 status code
            Arguments
                error -- Error information
        '''
        return error_message(401, "You are not authorized to perform this action.")
    
    @app.errorhandler(400)
    def bad_request(error):
        '''
            Handles HTTP 400 status code
            Arguments
                error -- Error information
        '''
        return error_message(400, 'Request is not valid.')

    
    @app.errorhandler(AuthError)
    def auth_error(error):
        '''
            Handles Errors related to authorization
            Arguments
                error -- AuthError
        '''
        return error_message(error.status_code, error.error)

    def error_message(status_code, message):
        '''
            Generates an error json to return to the client
            Arguments
                status_code -- (number) HTTP status code
                message -- (str) Message to send back to client describing what happened
        '''
        return jsonify({
            "success": False,
            "error": status_code,
            "message": message
        }), status_code



    


    
    
    
    
    
    return app




app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()
