import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)
# Enable debug mode.
DEBUG = False

# Secret key for session management. You can generate random strings here:
# https://randomkeygen.com/
SECRET_KEY = 'my precious'

# Connect to the database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
