from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .questions import Question
from .answers import Answer
from .category import Category