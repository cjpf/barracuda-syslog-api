from app import db
from app.api import bp
from app.api.errors import bad_request
from app.models import Recipient, Message
from flask import jsonify, request, url_for

# get single recipient by id
@bp.route('/recipients/<int:recipient_id>', methods=['GET'])
def get_recipient(recipient_id):
    '''
        Retrieve a single recipient
    '''
    return jsonify(Recipient.query.get_or_404(recipient_id).to_dict())
    # return jsonify(Attachment.query.get_or_404(attachment_id).to_dict())


# get all recipients by message id
@bp.route('/recipients/<string:message_id>', methods=['GET'])
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
@bp.route('/recipients', methods=['POST'])
def create_recipient():
    '''
        Create Recipient
    '''
    data = request.get_json() or {}
    if 'message_id' not in data:
        return bad_request('must include message_id')
    if 'email' not in data:
        return bad_request('recipient must have an email')
    if 'delivered' not in data:
        return bad_request('must include delivery status')
    if Recipient.query.filter_by(
            message_id=data['message_id'],
            email = data['email']).first():
        return bad_request('message already has this recipient email')
    recipient = Recipient()
    recipient.from_dict(data)
    db.session.add(recipient)
    db.session.commit()
    response = jsonify(recipient.to_dict())
    response.status_code = 201

    # response.headers['Location'] = url_for(
    #     'api.get_recipient', recipient=recipient.id
    # )
    return response    