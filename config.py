import os
from dotenv import load_dotenv
from app.parse import parse


BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))


class BaseConfig(object):
    '''
    Base Config Class for App
    '''
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
        'some-secret-key'
    DEBUG = True
    TESTING = False

    # Database Configurations
    # Set DATABASE_URL in .env or allow SQLite as default.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # APScheduler Configuration
    SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 1}
    }
    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 3
    }
    SCHEDULER_API = True

    # Parser Configurations
    JOB_CONFIG = False
    # Parse Job will default to running every 3 minutes in production.
    JOBS = [
        {
            'id': 'job1',
            'func': parse.parse_log,
            'trigger': 'cron',
            'day_of_week': '*',
            'hour': '*',
            'minute': '2,5,8,11,14,17,20,23,26,29,32,35,38,41,44,47,50,53,56,59'
        }
    ]

    # Mail Configurations
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    # MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['cjpf@charliejuliet.net']


class DevelopmentConfig(BaseConfig):
    '''
    Development environment specific config
    '''
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'app.db')

class ProductionConfig(BaseConfig):
    '''
    Production specific config
    '''
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')


class TestConfig(BaseConfig):
    '''
    Unit Testing Config
    '''
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SCHEDULER_API = False


class JobConfig(BaseConfig):
    '''
    Config for running ESS Log parsing jobs
    '''
    DEBUG = False
    TESTING = False
    SCHEDULER_API = False
    JOB_CONFIG = True
    # Default ess.log file will not work for most deployments.
    # Production environments require this to be set in .env
    ESS_LOG = os.environ.get('ESS_LOG')
    ESS_LOG_OFFSET = os.environ.get('ESS_LOG_OFFSET')
