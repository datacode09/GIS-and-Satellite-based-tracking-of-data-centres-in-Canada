import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database', 'datacentres.db')
DEBUG = True
SECRET_KEY = 'dev-key-change-in-production'
