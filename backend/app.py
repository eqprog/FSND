import os
from flask import Flask, request, abort, jsonify, render_template, redirect
from models import setup_db
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Forum, Thread, Page, Post, User
from auth import AuthError, requires_auth


def create_app(test_config=None):
    """
    Creates a Flask application instance.

    :param test_config: Configuration for the application, defaults to None
    :type test_config: dict, optional
    :return: Flask application instance
    """
    app = Flask(__name__)
    if test_config is None:
        with app.app_context():
            setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        """
        Adds CORS headers to the response.

        :param response: The response object
        :type response: Response
        :return: The response object with CORS headers
        """
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/', methods=['GET'])
    def get_home():
        return render_template('frontend/index.html')
    
    @app.route('/admin/create/forum', methods=['POST'])
    @requires_auth('admin')
    def create_forum(jwt):
        """
        Creates a new Forum.

        :param jwt: JSON Web Token for authentication
        :type jwt: str
        :return: JSON response with success status and message

        :Request JSON:
            {
                "name": str - The name of the new forum
            }
        """
        response = {}
        exception = None
        try:
            data = request.get_json()
            if len(Forum.query.filter(Forum.name == data.get('name')).all()) > 0:
                exception = 409
                raise Exception()
            else:
                new_forum = Forum(**data)
                new_forum.insert()
                response = {
                    'status': 'SUCCESS',
                    'message': 'Forum successfully created'
                }
        except Exception:
            if exception == 409:
                abort(409)
            abort(500)
        return jsonify(response)
    
    @app.route('/admin/users', methods=['GET'])
    @requires_auth('admin')
    def get_user_list(jwt):
        """
        Gets user list for admin portal
        """
        users = [user.format() for user in User.query.all()]
        return {
            'status': 'SUCCESS',
            'users': users
        }
    
    @app.route('/admin/user', methods=['POST'])
    @requires_auth('admin')
    def create_user(jwt):
        """
        Creates a new user.

        :param jwt: JSON Web Token for authentication
        :type jwt: str
        :return: JSON response with success status and user information
        :Request JSON:
            {
                "user_id": int - The ID of the new user,
                "name": str - The name of the new user,
                "role": str - The role of the new user
            }
        """
        data = request.get_json()
        user_id = data['user_id']
        name = data['name']
        role = data['role']
        try:
            user = User(id=user_id, name=name, role=role)
            user.insert()
            formatted_user = user.format()
            return jsonify({
                'status': 'SUCCESS',
                'id': formatted_user['id'],
                'name': formatted_user['name'],
                'role': formatted_user['role']
            })
        except Exception as e:
            print(e)
            abort(409)


    
    @app.route('/admin/ban-user', methods=['POST'])
    @requires_auth('admin')
    def ban_user(jwt):
        """
        Bans a user or removes ban status.

        :param jwt: JSON Web Token for authentication
        :type jwt: str
        :return: JSON response with success status and updated user information
        :Request JSON:
            {
                "id": int - The ID of the user to ban,
                "type": str - The ban type, either "REMOVE" to remove ban or other ban type,
                "duration": int, optional - The duration of the ban in days (if applicable)
            }
        """
        data = request.get_json()
        user = User.query.get(data.get('id'))
        if not user:
            return {
                'status': 'FAILURE',
                'message': 'User does not exist!'
            }
        status_type = data.get('type')
        if status_type == 'REMOVE':
            status_type = 'NORMAL'
        user.set_status(status_type)
        if data.get('duration'):
            user.set_probation(data.get('duration'))
        user.update()
        return {
            'status': 'SUCCESS',
            'message': 'User Status updated!',
            'user': user.format()
        }

    @app.route('/all', methods=['GET'])
    def get_forums():
        """
        Retrieves the list of forums.

        :return: JSON response with success status and list of forums
        """
        forums = [forum.format() for forum in Forum.query.all()]
        return {
            'status': 'SUCCESS',
            'forums': forums
        }
    @app.route('/forum/<int:forum_id>', methods=['GET'])
    def get_forum(forum_id):
        """
        Retrieves a specific forum and its threads.

        :param forum_id: The ID of the forum
        :type forum_id: int
        :return: JSON response with success status, forum, and threads
        """
        forum = Forum.query.get(forum_id)
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
        Creates a new thread in the specified forum.

        :param jwt: JSON Web Token for authentication
        :type jwt: str
        :param forum_id: The ID of the forum
        :type forum_id: int
        :return: JSON response with success status and thread information
        :Request JSON:
            {
                "title": str - The title of the new thread,
                "content": str - The content of the initial post in the thread
            }
        """
        data = request.get_json()
        user_id = jwt['user_id']
        thread = Thread(forum_id=forum_id, title=data['title'], user_id=user_id)
        thread.insert()

        add_post(thread, user_id, data['content'])
        return {
            'status': 'SUCCESS',
            'thread': thread.get_page_posts(1)
        }

    
    def create_page(thread):
        """
        Creates a new page for the specified thread.

        :param thread: The thread instance
        :type thread: Thread
        :return: New page instance
        """
        page_number = len(thread.pages) + 1
        new_page = Page(thread_id=thread.id, page_number=page_number)
        new_page.insert()
        return new_page
    
    def add_post(thread, user_id, content):
        """
        Adds a new post to the specified thread.

        :param thread: The thread instance
        :type thread: Thread
        :param user_id: The ID of the user who created the post
        :type user_id: int
        :param content: The content of the post
        :type content: str
        """
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
        """
        Retrieves a specific thread.

        :param thread_id: The ID of the thread
        :type thread_id: int
        :return: JSON response with success status and thread information
        """
        thread = Thread.query.get(thread_id)
        if thread:
            return {
                'status': 'SUCCESS',
                'thread': thread.format()
            }
        abort(404)
        

    @app.route('/threads/<int:thread_id>/<int:page_number>', methods=['GET'])
    def get_thread_page(thread_id, page_number):
        """
        Retrieves a specific page of a thread.

        :param thread_id: The ID of the thread
        :type thread_id: int
        :param page_number: The page number to retrieve
        :type page_number: int
        :return: JSON response with success status and page information
        """
        try:
            thread = Thread.query.get(thread_id)
            page = thread.get_page_posts(page_number)
            users = {}
            for post in page['posts']:
                if post['user_id'] not in users.keys():
                    users[post['user_id']] = User.query.filter(User.id == post['user_id']).one().name
                post['user_name'] = users[post['user_id']]
            return {
                'status': 'SUCCESS',
                'page': page
            }
        except Exception as e:
            print(e)
            abort(500)
    
    @app.route('/threads/<int:thread_id>', methods=['POST'])
    @requires_auth('post:post')
    def create_post(jwt, thread_id):
        """
        Creates a new post in the specified thread.

        :param jwt: JSON Web Token for authentication
        :type jwt: str
        :param thread_id: The ID of the thread
        :type thread_id: int
        :return: JSON response with success status and thread information
        :Request JSON:
            {
                "content": str - The content of the new post
            }
        """
        try:
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
        except:
            abort(400)
        
    @app.route('/threads/<int:thread_id>', methods=['PATCH'])
    @requires_auth('edit:post')
    def edit_post(jwt, thread_id):
        """
        Edits an existing post in the specified thread.

        :param jwt: JSON Web Token for authentication
        :type jwt: str
        :param thread_id: The ID of the thread
        :type thread_id: int
        :return: JSON response with success status
        :Request JSON:
            {
                "post_id": int - The ID of the post to edit,
                "content": str - The updated content of the post
            }
        """
        data = request.get_json()
        user_id = jwt['user_id']
        post_id = data['post_id']
        content = data['content']
        post = Post.query.get(post_id)
        if post is None:
            abort(404)
        if post is not None and (jwt['admin'] or (user_id is not None and post.user_id == user_id)):
            post.content = content
            post.update()
            return {
                'status': 'SUCCESS',
            }
        abort(503)

    @app.route('/threads/<int:thread_id>', methods=['DELETE'])
    @requires_auth('delete:post')
    def delete_post(jwt, thread_id):
        """
        Deletes a post in the specified thread.

        :param jwt: JSON Web Token for authentication
        :type jwt: str
        :param thread_id: The ID of the thread
        :type thread_id: int
        :return: JSON response with success status
        :Request JSON:
            {
                "post_id": int - The ID of the post to delete
            }
        """
        data = request.get_json()
        user_id = jwt['user_id']
        post_id = data['post_id']
        post = Post.query.get(post_id)
        if post is None:
            abort(404)
        if post is not None and (jwt['admin'] or (user_id is not None and post.user_id == user_id)):
            post.delete()
            return {
                'status': 'SUCCESS'
            }
        abort(503)


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


    @app.errorhandler(409)
    def conflicting_resource(error):
        '''
            Handles HTTP 409 status code
            Arguments
                error -- Error information
        '''
        return error_message(error.code, 'Resource already exists at this location!')

    @app.errorhandler(404)
    def page_not_found(error):
        '''
            Handles HTTP 404 status code
            Arguments
                error -- Error information
        '''
        if test_config != None:
            return error_message(404, 'resource not found!')
        return redirect('/')

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

    @app.errorhandler(503)
    def bad_user(error):
        '''
            Handles HTTP 503 status code when user who is not owner of resources tries to modify
            Arguments
                error -- Error information
        '''
        return error_message(503, 'Request is not valid.')
    
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
