#!/bin/bash
export DATABASE_URL="postgresql://eqprog:udacity@localhost:5432/forum"
export FLASK_APP=app.py
export EXCITED="true"
export CLIENT_SECRET="f785d820ed7f94451e1d9c772e42a6dd2abdd9c64c4fa2c0"
/etc/init.d/postgresql start
echo "setup.sh script executed successfully!"