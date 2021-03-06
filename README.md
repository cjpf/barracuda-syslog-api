# barracuda-syslog-api
A RESTful API sitting on top of a syslog parser that stores Barracuda Email Security Service syslog data.  The API and parsing can both be enabled or disabled with environment configuration.

The Barracuda Email Security Service allows you to send email metadata to a syslog server. This integration accepts the metadata for all mail that passes through the service.  The Barracuda syslog integration requires TLS with peer verification disabled.

## Log Parser
The log parser will read and store the syslog entries pushed to the syslog-ng server by the Barracuda Email Security Service.  Each log entry will be stored in a MySQL database for retrieval by the API later.
The Log Parser is also responsible for queueing encryption confirmation emails to be sent to the sender when they trigger the Barracuda encryption service.

## API Routes
The API provides routes for Messages, Recipients, Attachments, Domains, and Accounts.

### Messages
Messages contain the following elements; 

Message ID, Domain ID, Account ID, Source IP, PTR Record, Header-From, Envelope-From, Header-To, Destination Domain, Message Size, Subject, Timestamp.

#### Messages Routes
GET

  /api/messages
  
  /api/messages/<message_id>
 
 
POST

  /api/messages
  

### Recipients
Recipients contain the following elements; 

Recipient ID, Message ID, Action, Reason, Reason-Extra, Delivered, Delivery Detail, Email Address

#### Recipients Routes
GET

  /api/recipients/<recipient_id>
  
  /api/recipients/<message_id>
 
 
POST

  /api/recipients


### Attachments
Attachments contain the following elements; 

Attachment ID, Message ID, Name

#### Attachments Routes
GET

  /api/attachments/<message_id>
  
  /api/attachments/<message_id>/<attachment_id>
 
 
POST

  /api/attachments/<message_id> 
  
  
### Domains
Domains contain the following elements; 

Domain ID, Account ID, Name

#### Domains Routes
GET

  /api/domains
 
  /api/domains/<domain_id>
 
 
POST

  /api/domains
  
  
PUT

  /api/domains/<domain_id>
  
  
DELETE

  /api/domains/<domain_id>


### Accounts
Accounts contain the following elements; 

Account ID, Name

#### Accounts Routes
GET

  /api/accounts
  
  /api/accounts/<account_id>
 
 
POST

  /api/accounts
  
  
PUT

  /api/accounts/<account_id>
  
  
DELETE

  /api/accounts/<account_id>
