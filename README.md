# The Best Forums Ever *
(This is very subjective)

## BACKEND
This is a flask backend that connects to a postgres database to make queries and respond to a frontend web application.
### Environment Setup
Use python 3.8
Install requirements 'pip install -r requirements.txt'
Create PSQL tables 'forum' and 'forum_test'
Add values to path - see setup.sh for keys
Linux users can modify setup.sh and then run . setup.sh to add the values to their path.
* More info
-  ADMIN_TOKEN' should be a valid JWT from auth0 with the 'admin' permission
- 'USER_TOKEN' should be a valid JWT from auth0 with the following permissions
-- post:thread, post:post, edit:post, delete:thread, delete:post
- 'ADMIN_ID' and 'USER_ID' are the user_id values from the token's 'sub' property after the provider name and the pipe character. ie 'auth0|<id>'.
-- Udacity reviewers: These values should be provided to you, they will not be in the repository

### Running Backend Tests
Be sure to have dependencies installed and the environment set up with the forum_test db location for the TEST_URL path variable.
Run tests.py to run the tests.

## Accessing Live Backend
The backend is running on a Render instance. Access the backend through the frontend application.
-- Udacity Reviewers: I will provide a 'refresh link' that will spin up the server if the instance has spun down due to inactivity. You should be able to make a request to this url, wait a few moments, and use the frontend application to brows

### Route Documentation
All relevant information in app.py

## Frontend
This project uses an Angular frontend that must be run locally.

### Environment Setup
Install nodejs version 16 or later and node package manager (npm).
Install dependencies with 'npm install'
Run the server with the following command
* npm run start
DO NOT USE 'ng serve'!!!!

### Using Frontend
Udacity Reviewers: You should have been provided two login credentials. These accounts are already established in auth0 and in the backend database. I didn't have time to figure out how to automate this process in auth0, so it was done by hand. Unfortunately, because of this if you register a new user via auth0, depsite having a JWT you will not be able to perform most actions because there is no corresponding ID in the DB. However, if you are logged in as an admin, you can go to '/admin-portal' in the front end add a new user to the DB with its user_name and the auth0 user_id value (see backend information)

### Things That Do Nothing Because I Ran Out Of Time:
No home button
Forum will lose state if you hard refresh the page on creating/editing posts. Navigate back and return to that view and it will work.
Lock Thread does nothing
Although there are 'ban' and 'probation' states for users, I did not actually implement any restrictions due to not having the auth0 permissions sync with the db