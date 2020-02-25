from app import db
from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth
from app.models import Attachment
from flask import jsonify, request, url_for


@bp.route('/attachments/<string:account_id>', methods=[GET])
@token_auth.login_required
def get_attachment(attachment_id):
    '''
        Retrieve a single attachment
    '''
    return jsonify(Attachment.query.get_or_404(attachment_id).to_dict())