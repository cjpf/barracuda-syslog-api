import os
from dotenv import load_dotenv
from app.parse import jobs


BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))


class BaseConfig(object):
    '''
    Base Config Class for App
    '''
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
        'some-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['cjpf@charliejuliet.net']
    ESS_LOG = os.environ.get('ESS_LOG') or \
        'ess.log'
    ESS_LOG_OFFSET = os.environ.get('ESS_LOG_OFFSET') or \
        'ess.log.offset'
    JOBS = [
        {
            'id': 'job1',
            'func': jobs.parse_log,
            'trigger': 'cron',
            'day_of_week': '*',
            'hour': '*',
            'minute': '5'
        }
    ]
    # SCHEDULER_JOBSTORES = {
    #     'default': SQLAlchemyJobStore(url='sqlite:///jobs.db')
    # }
    SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 1}
    }
    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 3
    }
    SCHEDULER_API_ENABLED = True
    JOB_CONFIG = False
    DEBUG = True
    TESTING = False


class DevelopmentConfig(BaseConfig):
    '''
    Development environment specific config
    '''
    DEBUG = True
    TESTING = True
    

class ProductionConfig(BaseConfig):
    '''
    Production specific config
    '''
    DEBUG = False
    TESTING = False
    # SECRET_KEY = open('/path/to/secret/key/file').read()


class TestConfig(BaseConfig):
    '''
    Unit Testing Config
    '''
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SCHEDULER_API_ENABLED = False


class JobConfig(BaseConfig):
    '''
    Config for running ESS Log parsing jobs
    '''
    SCHEDULER_API_ENABLED = False
    JOB_CONFIG = True
    DEBUG = True
    TESTING = False