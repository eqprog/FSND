import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import subprocess

from app import create_app
from models import setup_db, Forum, Thread, Page, Post, User

from roles_and_status import ForumRoles, UserStatus



ADMIN_TOKEN = os.environ['ADMIN_TOKEN']
ADMIN_ID = os.environ['ADMIN_ID']
USER_TOKEN = os.environ['USER_TOKEN']
USER_ID = os.environ['USER_ID']
TEST_URL = os.environ['TEST_URL']

def provide_auth(mode=''):
    '''
    Provides auth token and headers for a test request
    Arguments
        mode -- (str) Returns the ADMIN token if mode is 'admin', otherwise a normal user token is returned
    '''
    def provides_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = ADMIN_TOKEN if mode == 'admin' else USER_TOKEN
            headers = { 'Content-Type': 'application/json', 'Authorization': f'Bearer {token}' }
            return f({
                'token': ADMIN_TOKEN if mode == 'admin' else USER_TOKEN,
                'headers': { 'Content-Type': 'application/json', 'Authorization': f'Bearer {token}' }
            }, *args, **kwargs)
        return wrapper
    return provides_auth_decorator

class AppTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(test_config=True)
        self.client = self.app.test_client
        self.database_name = "forum_test"
        self.database_path = "postgresql://{}/{}".format(
            'localhost:5432', self.database_name)
        with self.app.app_context():
            # I removed the code in this block below the following line because it causes errors with newer dep versions
            setup_db(self.app, TEST_URL)
            
    def get_token(self, mode=''):
        return { 
            'Content-Type': 'application/json', 
            'Authorization': f'Bearer {ADMIN_TOKEN if mode == "admin" else USER_TOKEN}' 
        }
    
    def assertSuccess(self, res, data):
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['status'], 'SUCCESS')
        
    def assertFailure(self, data, status_code):
        self.assertEqual(data['error'], status_code)
        self.assertEqual(data['success'], False)
    
    def test_01_create_forum_success(self):
        headers = self.get_token('admin')
        res = self.client().post('/admin/create/forum',json={
                'name': 'Test Forum',
                'description': 'This is a test forum'
            }, headers=headers)
        data = json.loads(res.data)
        self.assertSuccess(res, data)
    
    def test_02_create_forum_exists(self):
        headers = self.get_token('admin')
        res = self.client().post('/admin/create/forum',json={
                'name': 'Test Forum',
                'description': 'This is a test forum'
            }, headers=headers)
        data = json.loads(res.data)
        self.assertFailure(data, 409)
    
    def test_03_create_forum_permissions(self):
        headers = self.get_token()
        res = self.client().post('/admin/create/forum',json={
                'name': 'Test Forum',
                'description': 'This is a test forum'
            }, headers=headers)
        data = json.loads(res.data)
        self.assertFailure(data, 403)
        
    def test_04_create_admin_user_success(self):
        headers = self.get_token('admin')
        res = self.client().post('admin/user', json={
            'user_id': ADMIN_ID,
            'name': 'admin',
            'role': ForumRoles.ADMIN.value
        }, headers=headers)
        
        data = json.loads(res.data)
        self.assertSuccess(res, data)
        self.assertEqual(data['id'], ADMIN_ID)
        self.assertEqual(data['role'], ForumRoles.ADMIN.value)
        self.assertEqual(data['name'], 'admin')
    
    def test_05_create_user_user(self):
        headers = self.get_token('admin')
        res = self.client().post('admin/user', json={
            'user_id': USER_ID,
            'name': 'newbie',
            'role': ForumRoles.USER.value
        }, headers=headers)
        
        data = json.loads(res.data)
        self.assertSuccess(res, data)
        self.assertEqual(data['id'], USER_ID)
        self.assertEqual(data['role'], ForumRoles.USER.value)
        self.assertEqual(data['name'], 'newbie')
        
    def test_06_create_admin_user_no_auth(self):
        headers = self.get_token()
        res = self.client().post('admin/user', json={
            'user_id': ADMIN_TOKEN,
            'name': 'admin',
            'role': ForumRoles.ADMIN.value
        }, headers=headers)
        data = json.loads(res.data)
        self.assertFailure(data, 403)
        
    def test_07_get_user_list(self):
        headers = self.get_token('admin')
        res = self.client().get('admin/users', headers=headers)
        
        data = json.loads(res.data)
        self.assertSuccess(res, data)
        self.assertEqual(len(data['users']), 2)
    
    def test_07_get_user_list_no_auth(self):
        headers = self.get_token('user')
        res = self.client().get('admin/users', headers=headers)
        
        data = json.loads(res.data)
        self.assertFailure(data, 403)

    
    def test_08_ban_user(self):
        headers = self.get_token('admin')
        res = self.client().post('admin/ban-user', json={
            'type': UserStatus.BANNED.value,
            'id': USER_ID,
        }, headers=headers)
        
        data = json.loads(res.data)
        self.assertSuccess(res, data)
        self.assertEqual(data['user']['status'], UserStatus.BANNED.value)
    
    def test_08_ban_user_no_auth(self):
        headers = self.get_token('user')
        res = self.client().post('admin/ban-user', json={
            'type': UserStatus.BANNED.value,
            'id': USER_ID,
        }, headers=headers)
        
        data = json.loads(res.data)
        self.assertFailure(data, 403)
    
    def test_09_unban_user(self):
        headers = self.get_token('admin')
        res = self.client().post('admin/ban-user', json={
            'type': 'REMOVE',
            'id': USER_ID,
        }, headers=headers)
        
        data = json.loads(res.data)
        self.assertSuccess(res, data)
        self.assertEqual(data['user']['status'], UserStatus.NORMAL.value)
        
    def test_09_unban_user_no_auth(self):
        headers = self.get_token('user')
        res = self.client().post('admin/ban-user', json={
            'type': 'REMOVE',
            'id': USER_ID,
        }, headers=headers)
        
        data = json.loads(res.data)
        self.assertFailure(data, 403)

    def test_10_get_forums(self):
        res = self.client().get('/all')
        data = json.loads(res.data)
        self.assertSuccess(res, data)
        self.assertEqual(len(data['forums']), 1)
        
    def test_11_create_thread(self):
        headers = self.get_token()
        res = self.client().post('forum/1', json={
            'title': 'Test Thread',
            'content': 'Test content',
        }, headers=headers)
        data = json.loads(res.data)
        self.assertSuccess(res, data)
        
    def test_12_create_thread_no_auth(self):
        res = self.client().post('forum/1', json={
            'title': 'Test Thread',
            'content': 'Test content',
        })
        data = json.loads(res.data)
        self.assertFailure(data, 401)
        
    def test_13_get_forum(self):
        res = self.client().get('forum/1')
        data = json.loads(res.data)
        self.assertSuccess(res, data)
    
    def test_14_get_thread(self):
        res = self.client().get('threads/1')
        data = json.loads(res.data)
        self.assertSuccess(res, data)
        self.assertEqual(data['thread']['title'], 'Test Thread')
    
    def test_14_get_thread_404(self):
        res = self.client().get('threads/2')
        data = json.loads(res.data)
        self.assertFailure(data, 404)
        
    def test_15_get_thread_page(self):
        res = self.client().get('threads/1/1')
        data = json.loads(res.data)
        self.assertSuccess(res, data)
    
    def test_16_create_post(self):
        headers = self.get_token('admin')
        res = self.client().post('threads/1', json={
            'content': 'A new post'
        }, headers=headers)
        data = json.loads(res.data)
        self.assertSuccess(res, data)
    
    def test_17_create_post_no_auth(self):
        res = self.client().post('threads/1', json={
            'content': 'A new post'
        })
        data = json.loads(res.data)
        self.assertFailure(data, 401)
    
    def test_18_edit_post(self):
        headers = self.get_token()
        res = self.client().patch('threads/1', json={
            'post_id': '1',
            'content': 'edited post'
        }, headers=headers)
        data = json.loads(res.data)
        self.assertSuccess(res, data)
        
    def test_19_edit_post_admin(self):
        headers = self.get_token('admin')
        res = self.client().patch('threads/1', json={
            'post_id': '1',
            'content': 'edited post by admin'
        }, headers=headers)
        data = json.loads(res.data)
        self.assertSuccess(res, data)
    
    def test_20_edit_post_auth_different(self):
        headers = self.get_token()
        res = self.client().patch('threads/1', json={
            'post_id': '2',
            'content': 'non owner edited post'
        }, headers=headers)
        data = json.loads(res.data)
        self.assertFailure(data, 503)
    
    def test_21_delete_post_auth_different(self):
        headers = self.get_token()
        res = self.client().delete('threads/1', json={
            'post_id': '2',
        }, headers=headers)
        data = json.loads(res.data)
        self.assertFailure(data, 503)
        
    def test_22_delete_post(self):
        headers = self.get_token('admin')
        res = self.client().delete('threads/1', json={
            'post_id': '2',
        }, headers=headers)
        data = json.loads(res.data)
        self.assertSuccess(res, data)

# Make the tests conveniently executable
if __name__ == "__main__":
    """ Resets the database each time the test suite starts"""
    subprocess.run("dropdb forum_test", shell=True)
    subprocess.run("createdb forum_test", shell=True)
    unittest.main()


