from app import db
from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth
from app.models import Attachment, Message
from flask import jsonify, request, url_for


@bp.route('/attachments/<int:attachment_id>', methods=['GET'])
@token_auth.login_required
def get_attachment(attachment_id):
    '''
        Retrieve a single attachment
    '''
    return jsonify(Attachment.query.get_or_404(attachment_id).to_dict())


@bp.route('/attachments/<string:message_id>', methods=['GET'])
@token_auth.login_required
def get_attachments(message_id):
    '''
        Retrieve a collection of all attachments
    '''
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    m = Message.query.get_or_404(message_id)
    data = Attachment.to_collection_dict(
        m.attachments,  page, per_page, 'api.get_attachments', message_id=message_id)
    return jsonify(data)


@bp.route('/attachments', methods=['POST'])
@token_auth.login_required
def create_attachment():
    '''
        Create a new attachment
    '''
    data = request.get_json() or {}
    if 'message_id' not in data:
        return bad_request('must include message_id')
    if 'name' not in data:
        return bad_request('must include name')
    if Attachment.query.filter_by(
            message_id=data['message_id'], 
            name = data['name']).first():
        return bad_request('message already has that attachment name')
    attachment = Attachment()
    attachment.from_dict(data)
    db.session.add(attachment)
    db.session.commit()
    response = jsonify(attachment.to_dict())
    response.status_code = 201
    
    response.headers['Location'] = url_for(
        'api.get_attachment', attachment_id=attachment.id)
    return response
