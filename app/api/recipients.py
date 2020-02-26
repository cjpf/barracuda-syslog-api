from app import db
from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth
from app.models import Recipient, Message
from flask import jsonify, request, url_for

# get single recipient by id
@bp.route('/recipients/<int:recipient_id>', methods=['GET'])
@token_auth.login_required
def get_recipient(recipient_id):
    '''
        Retrieve a single recipient
    '''
    return jsonify(Recipient.query.get_or_404(recipient_id).to_dict())
    # return jsonify(Attachment.query.get_or_404(attachment_id).to_dict())


# get all recipients by message id
@bp.route('/recipients/<string:message_id>', methods=['GET'])
@token_auth.login_required
def get_recipients(message_id):
    '''
        Retrieve collection of recpients for a message
    '''
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    m = Message.query.get_or_404(message_id)
    data = Recipient.to_collection_dict(
        m.recipients, page, per_page, 'api.get_recipients', message_id=message_id)
    return jsonify(data)

# create a recipient by message id
