from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import errors, domains, accounts, messages, attachments
