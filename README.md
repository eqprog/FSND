# The Best Forums Ever *
(This is very subjective)

# URL - https://render-deployment-5s2m.onrender.com

# Backend - Forum Management API

## Setting up the Backend

### Install Dependencies

1. **Python 3.8** - Follow instructions to install the latest version of Python for your platform in the python docs

2. **Virtual Environment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virtual environment for your platform can be found in the python docs

3. **PIP Dependencies** - Once your virtual environment is set up and running, install the required dependencies by navigating to the /backend directory and running:

```pip install -r requirements.txt```

### Key Pip Dependencies

- **Flask** is a lightweight backend microservices framework. Flask is required to handle requests and responses.
- **SQLAlchemy** is the Python SQL toolkit and ORM we'll use to handle the lightweight SQL database. You'll primarily work in app.py and can reference models.py.
- **Flask-CORS** is the extension we'll use to handle cross-origin requests from our frontend server.
- **Flask-Migrate** is an extension that handles SQLAlchemy database migrations for Flask applications using Alembic.

### Set up the Database

With Postgres running, create a forum_management database:

```createdb forum```

### Run the Server

From within the `/backend` directory first ensure you are working using your created virtual environment.

Add the following secrets to your environment: 
- `DATABASE_URL`: postgres url for the `forum` database
- `TEST_URL`: postgres url for test database
- `ADMIN TOKEN`: Test JWT token for Admin role
- `ADMIN ID`: Admin ID corresponding to the Auth0 `user_id` value.
- `USER_TOKEN`: Test JWT token for User role
- `USER_ID`: User ID correspoding to the Auth0 `user_id` value.

To run the server, execute:

`flask run --reload`

The `--reload` flag will detect file changes and restart the server automatically.

## API Endpoints

For all endpoints, in case of an unexpected server error, a generic error message with a `500 status code` will be returned:
```json
{
  "success": false,
  "error": 500,
  "message": "An error occurred on the server"
}
```

`GET '/'`
- Fetches a list of forums
- Request arguments: None
- Expected responses:
  ```json 
  Success:
  {
    "status": "SUCCESS",
    "forums": [array of forum objects]
  }
  Failure - No specific failure scenarios for this endpoint. If an error occurs, a generic error message will be returned.
  ```

`GET '/forum/<int:forum_id>'`
- Fetches a specific forum and its threads
- Request arguments: forum_id (int)
- Expected responses:
  ```json
  Success:
  {
    "status": "SUCCESS",
    "forum": forum object,
    "threads": [array of thread objects]
  }
  
  Failure: Forum not found
  {
    "status": "FAILURE",
    "message": "Forum does not exist!"
  }
  ```

`POST '/admin/create/forum'`
- Creates a new forum
- Request arguments: None
- Expected responses:
  ```json
  Success:
  {
    "status": "SUCCESS",
    "message": "Forum successfully created"
  }
  Failure: Forum with the same name already exists
  {
    "status": "FAILURE",
    "message": "Forum with this name already exists!"
  }
  ```

GET '/admin/users'
- Retrieves the list of users for the admin portal
- Request arguments: None
- Expected responses:
  ```json
  Success:
  {
    "status": "SUCCESS",
    "users": [array of user objects]
  }
  Failure: No specific failure scenarios for this endpoint. If an error occurs, a generic error message will be returned.
  ```

`POST '/admin/user'`
- Creates a new user
- Request arguments: None
- Expected responses:
  ```json
  Success:
  {
    "status": "SUCCESS",
    "id": user ID,
    "name": user name,
    "role": user role
  }
  Failure: User with the same ID already exists
  {
    "status": "FAILURE",
    "message": "User with this ID already exists!"
  }
  ```

`POST '/admin/ban-user'`
- Bans a user or removes ban status
- Request arguments: None
- Expected responses:
  ```json
  Success:
  {
    "status": "SUCCESS",
    "message": "User Status updated!",
    "user": updated user object
  }
  Failure: User not found
  {
    "status": "FAILURE",
    "message": "User does not exist!"
  }
  ```
  

`POST '/forum/<int:forum_id>'`
- Creates a new thread in the specified forum
- Request arguments: forum_id (int)
- Expected responses:
  ```json
  Success:
  {
    "status": "SUCCESS",
    "thread": thread object
  }
  Failure: Forum not found
  {
    "status": "FAILURE",
    "message": "Forum does not exist!"
  }
  ```
  
`GET '/threads/<int:thread_id>'`
- Retrieves a specific thread
- Request arguments: thread_id (int)
- Expected responses:
  ```json
  Success:
  {
    "status": "SUCCESS",
    "thread": thread object
  }
  Failure: Thread not found
  {
    "status": "FAILURE",
    "message": "Thread does not exist!"
  }
  ```

`GET '/threads/<int:thread_id>/<int:page_number>'`
- Retrieves a specific page of a thread
- Request arguments: thread_id (int), page_number (int)
- Expected responses:
  ```json
  Success:
  {
    "status": "SUCCESS",
    "page": page object
  }
  Failure: Thread not found or page not found
  {
    "status": "FAILURE",
    "message": "Thread or page does not exist!"
  }
  ```

`POST '/threads/<int:thread_id>'`
- Creates a new post in the specified thread
- Request arguments: thread_id (int)
- Expected responses:
  ```json
  Success:
  {
    "status": "SUCCESS",
    "thread": thread object
  }
  Failure: Thread not found
  {
    "status": "FAILURE",
    "message": "Thread does not exist!"
  }
  ```
  

`PATCH '/threads/<int:thread_id>'`
- Edits an existing post in the specified thread
- Request arguments: thread_id (int)
- Expected responses:
  ```json
  Success:
  {
    "status": "SUCCESS"
  }
  Failure: Tread not found or user not authorized to edit the post
  {
    "status": "FAILURE",
    "message": "Thread does not exist or user not authorized!"
  }
  ```

`DELETE '/threads/<int:thread_id>'`
- Deletes a post in the specified thread
- Request arguments: thread_id (int)
- Expected responses:
  ```json
  Success:
  {
    "status": "SUCCESS"
  }
  {
    "status": "FAILURE",
    "message": "Thread does not exist or user not authorized!"
  }
  ```

### Running Backend Tests
Be sure to have dependencies installed and the environment set up with the forum_test db location for the TEST_URL path variable.
Run tests.py to run the tests.

## Accessing Live Backend
The backend is running on a Render instance. Access the backend through the frontend application.
-- Udacity Reviewers: I will provide a 'refresh link' that will spin up the server if the instance has spun down due to inactivity. You should be able to make a request to this url, wait a few moments, and use the frontend application to brows

### Route Documentation
All relevant information in app.py

## Frontend
This project uses an Angular frontend. It is already built as a static resource for the backend server. However, if you wish to build it yourself see below.

Udacity Reviewers: You should have been provided two login credentials. These accounts are already established in auth0 and in the backend database. I didn't have time to figure out how to automate this process in auth0, so it was done by hand. Unfortunately, because of this if you register a new user via auth0, depsite having a JWT you will not be able to perform most actions because there is no corresponding ID in the DB. However, if you are logged in as an admin, you can go to '/admin-portal' in the front end add a new user to the DB with its user_name and the auth0 user_id value (see backend information)

### Environment Setup
Install nodejs version 16 or later and node package manager (npm).
Install dependencies with 'npm install'
Run the server with the following command
* npm run start
DO NOT USE 'ng serve'!!!!


### Things That Do Nothing Because I Ran Out Of Time:
No home button
Forum will lose state if you hard refresh the page on creating/editing posts. Navigate back and return to that view and it will work.
Lock Thread does nothing
Although there are 'ban' and 'probation' states for users, I did not actually implement any restrictions due to not having the auth0 permissions sync with the db