from app import db
from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth
from app.models import Attachment
from flask import jsonify, request, url_for


@bp.route('/attachments/<string:attachment_id>', methods=[GET])
@token_auth.login_required
def get_attachment(attachment_id):
    '''
        Retrieve a single attachment
    '''
    return jsonify(Attachment.query.get_or_404(attachment_id).to_dict())

@bp.route('/attachments/<string:message_id>', methods=[GET])
@token_auth.login_required
def get_attachments():
    '''
        Retrieve a collection of all attachments
    '''
    print("message id : {}".format(message_id))
    m = Message.query.get_or_404(message_id).first()
    return jsonify(m.attachments.all())
    # look at tables and models and check out how to do this
    # look into this^^

@bp.route('/attachments/<string:message_id>', methods=[POST])
@token_auth.login_required
def create_attachment():
    '''
        Create a new attachment
    '''
    

