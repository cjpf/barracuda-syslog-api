import os
import logging
from logging.handlers import SMTPHandler, TimedRotatingFileHandler
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_apscheduler import APScheduler


login = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
scheduler = APScheduler()


def create_app(config_class):
    '''
    Creates a flask app
    Requires a config class from config.py
    '''
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    if app.config['JOB_CONFIG']:
        from app.parse import bp as parse_bp
        app.register_blueprint(parse_bp)
    else:
        from app.api import bp as api_bp
        app.register_blueprint(api_bp, url_prefix='/api')

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'],
                subject='barracuda-syslog-tools Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    if not app.config['JOB_CONFIG']:
        file_handler = TimedRotatingFileHandler(
            'logs/barracuda-syslog-tools.log',
            when='D',
            interval=1,
            backupCount=14)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s \
                [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

    if app.config['SCHEDULER_API']:
        app.logger.info("Scheduler API Enabled.  Starting Scheduler...")
        try:
            scheduler.init_app(app)
            scheduler.start()
            app.logger.info(scheduler.get_jobs()[0])
        except Exception as e:
            app.logger.info(e)
            
    app.logger.info('db URL: {}'.format(
        app.config['SQLALCHEMY_DATABASE_URI']))
    app.logger.info('app created')


    return app
