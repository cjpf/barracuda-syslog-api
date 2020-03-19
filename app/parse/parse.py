import re
import json
import io
import config
import os
from pygtail import Pygtail
from app import db, create_app
from app.email import send_mail
from app.models import Message, Recipient, Attachment, Account, Domain
from flask import render_template
from dns import resolver


def parse_log():
    '''
    Parses ESS Log Data to store for the App
    '''
    app = create_app(config.JobConfig)
    app_context = app.app_context()
    app_context.push()

    _detect_rotated_log(app)
    with app.app_context():
        for line in Pygtail(app.config['ESS_LOG'],
                            paranoid=True,
                            full_lines=True,
                            offset_file=app.config['ESS_LOG_OFFSET']):
            try:
                data = re.findall(r'\{.*\}', line)
                data = json.loads(data[0])
            except Exception as r:
                app.logger.error(r)

            try:
                if _is_connection_test(data['account_id'], data['domain_id']):
                    app.logger.info('Connection Test Detected. Skipping...')
                    continue

                if _message_exists(app.logger, data['message_id']):
                    app.logger.info('Message ID FOUND. Skipping...')
                    continue
                app.logger.info('Message ID NOT FOUND. Processing...')

            except Exception as e:
                app.logger.error(e)

            try:
                _store_account(app.logger, data)
                _store_domain(app.logger, data)
                _store_message(app.logger, data)

                if data['recipients']:
                    for recipient in data['recipients']:
                        _store_recipient(
                            app.logger,
                            recipient,
                            data['message_id'])

                        app.logger.info(
                            "Checking Outbound Encryption Status")
                        _check_encryption_status(recipient, data)

                if data['attachments']:
                    for attachment in data['attachments']:
                        _store_attachment(
                            app.logger,
                            attachment,
                            data['message_id'])

            except Exception as e:
                db.session.rollback()
                app.logger.error(
                    "Failed to Process Message ({})".format(
                        data['message_id']))
                app.logger.error(e)
            else:
                db.session.commit()

    app.logger.info('Closing app context for parse_log')
    app_context.pop()


def _build_from_address(env_from):
    '''
    Extract the sender's domain name and return a spoof
    address for confirmation email.
    env_from: cj@charliejuliet.net
    return: notification@charliejuliet.net
    '''
    send_domain = re.findall(r'@.*', env_from)[0]
    return 'notification{}'.format(send_domain)


def _check_encryption_status(recipient, data):
    '''
    Checks the Action value for a recipient to see if an 
    encryption confirmation message should be generated
    for the sender.
    '''
    if recipient['action'] == 'encrypted':
        subject = "Encryption Confirmation Notice"
        sender = _build_from_address(data['env_from'])
        recipient = [data['env_from']]
        _send_encryption_confirmation(subject, sender, recipient)


def _send_encryption_confirmation(subject, sender, recipient):
    '''
    Sends the encryption confirmation email
    '''
    send_mail(subject,
              sender,
              recipient,
              render_template(
                  'encryption_confirmation_email.txt'),
              render_template(
                  'encryption_confirmation_email.html')
              )


def _detect_rotated_log(app):
    '''
    Check inode stored in pygtail offset file and compare to inode of
    log file to detect rotations.
    if inode is different, delete offset file to reset
    '''
    try:
        with io.open(app.config['ESS_LOG_OFFSET']) as f:
            log_inode = re.findall(r'\d+', f.readline())
            log_inode = json.loads(log_inode[0])
            real_inode = os.stat(app.config['ESS_LOG']).st_ino
            if real_inode != log_inode:
                app.logger.info(
                    'inode value mismatch. Resetting pygtail offset file.')
                os.remove(app.config['ESS_LOG_OFFSET'])
    except Exception:
        app.logger.info('pygtail offset file not found')
        return


def _is_connection_test(account_id, domain_id):
    '''
    Checks to see if account id and domain id fields are empty.
    If empty, the log entry is simply a
    connection test from the service.
    '''
    if not account_id and not domain_id:
        return True
    return False


def _add(item):
    '''
    Add an item to the db
    '''
    try:
        db.session.add(item)
        return True
    except Exception as e:
        raise Exception(e)


def _store_account(logger, data):
    '''
    Creates new Account entry if not already created.
    '''
    if _account_exists(logger, data['account_id']):
        logger.info("Account ID FOUND. Skipping Account...")
        return False
    else:
        logger.info("Account ID NOT FOUND. Creating Account.")
        a = Account(account_id=data['account_id'])
        try:
            _add(a)
        except Exception as e:
            raise Exception(e)


def _store_attachment(logger, data, message_id):
    '''
    Creates new Attachment entry if Message has already been created
    '''
    logger.info('Creating Attachment.')
    a = Attachment(
        message_id=message_id,
        name=data['name']
    )
    try:
        _add(a)
    except Exception as e:
        raise Exception(e)


def _store_domain(logger, data):
    '''
    Creates new Domain entry if not already created.
    '''
    if _domain_exists(logger, data['domain_id']):
        logger.info("Domain ID FOUND. Checking for Name...")
        if not _domain_has_name(data['domain_id']):
            logger.info("No name found. Obtaining Domain name...")
            name = _get_domain_name_by_id(
                data['dst_domain'], data['domain_id'])
            if name:
                logger.info("Name Obtained: {}".format(name))
                try:
                    domain = Domain.query.filter_by(domain_id=domain_id).first()
                    domain.name = name
                    db.session.commit()
                except Exception as e:
                    raise Exception(e)
                logger.info("Domain updated!)
        else:
            logger.info("Domain already has a Name.")
    else:
        logger.info("Domain ID NOT FOUND. Creating Domain.")
        name = _get_domain_name_by_id(data['dst_domain'], data['domain_id'])
        if not name:
            logger.info("Name not found, creating domain without name.")
            d = Domain(domain_id=data['domain_id'],
                       account_id=data['account_id'])
        else:
            logger.info("Name Obtained: {}".format(name))
            d = Domain(domain_id=data['domain_id'],
                       account_id=data['account_id'], name=name)
        try:
            _add(d)
        except Exception as e:
            raise Exception(e)


def _get_domain_name_by_id(destination, domain_id):
    '''
    Determines the Name of a Domain by ID. 
    Perform MX record lookups on the dst_domain and check to see
    if the Domain ID is matched within any of those records.  
    Barracuda MX records use the following format; d206037a.ess.barracudanetworks.com
    If no match is found, return None.
    '''
    mx_records = resolver.query(destination, 'MX')
    for mx in mx_records:
        result = re.search(
            r'd(\d{5,8})[ab]\.ess\.barracudanetworks\.com', str(mx))
        if result and result.group(1) == domain_id:
            return destination


def _domain_has_name(domain_id):
    '''
    Checks to see if an existing domain ID entry has a populated Name field
    '''
    return True if Domain.query.filter_by(domain_id=domain_id).first().name \
        else False


def _store_message(logger, data):
    '''
    Creates new Message entry if not already created.
    '''
    logger.info("Creating Message.")
    m = Message(
        message_id=data['message_id'],
        account_id=data['account_id'],
        domain_id=data['domain_id'],
        src_ip=data['src_ip'],
        ptr_record=data['ptr_record'],
        hdr_from=data['hdr_from'],
        env_from=data['env_from'],
        hdr_to=data['hdr_to'],
        dst_domain=data['dst_domain'],
        size=data['size'],
        subject=data['subject'],
        timestamp=data['timestamp']
    )
    try:
        _add(m)
    except Exception as e:
        raise Exception(e)


def _store_recipient(logger, data, message_id):
    '''
    Creates new Recipient entry if Message has already been created
    '''
    logger.info('Creating Recipient.')
    r = Recipient(
        message_id=message_id,
        action=data['action'],
        reason=data['reason'],
        reason_extra=data['reason_extra'],
        delivered=data['delivered'],
        delivery_detail=data['delivery_detail'],
        email=data['email'],
    )
    try:
        _add(r)
    except Exception as e:
        raise Exception(e)


def _account_exists(logger, account_id):
    '''
    Checks to see if an Account already exists in the database.
    '''
    logger.info(
        "Checking for existing Account ID ({})".format(account_id))
    return True if Account.query.filter_by(account_id=account_id).first() \
        else False


def _domain_exists(logger, domain_id):
    '''
    Checks to see if a Domain already exists in the database.
    '''
    logger.info(
        "Checking for existing Domain ID ({})".format(domain_id))
    return True if Domain.query.filter_by(domain_id=domain_id).first() \
        else False


def _message_exists(logger, message_id):
    '''
    Checks to see if a Message already exists in the database.
    '''
    logger.info(
        'Checking for existing Message ID ({})'.format(message_id))
    return True if Message.query.filter_by(message_id=message_id).first() \
        else False
