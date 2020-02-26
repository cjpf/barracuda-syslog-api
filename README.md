# barracuda-syslog-api
A RESTful API sitting on top of a syslog parser that stores Barracuda Email Security Service syslog data.  The API and parsing can both be enabled or disabled with environment configuration.

The Barracuda Email Security Service allows you to send email metadata to a syslog server. This integration accepts the metadata for all mail that passes through the service.  The Barracuda syslog integration requires TLS with peer verification disabled.

## Log Parser

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
  
  
PUT

  /api/messages/<message_id>
  
  
DELETE

  /api/messages/<message_id>
  

### Recipients
Recipients contain the following elements; 

ID, Message ID, Action, Reason, Reason-Extra, Delivered, Delivery Detail, Email Address

#### Recipients Routes
GET

  /api/recipients/<message_id>
  
  /api/recipients/<message_id>/<id>
 
 
POST

  /api/recipients/<message_id>
  
  
PUT

  /api/recipients/<message_id>
  
  
DELETE

  /api/recipients/<message_id>


### Attachments
Attachments contain the following elements; 

ID, Message ID, Name

#### Attachments Routes
GET

  /api/attachments/<message_id>
  
  /api/attachments/<message_id>/<id>
 
 
POST

  /api/attachments/<message_id>
  
  
PUT

  /api/attachments/<message_id>
  
  
DELETE

  /api/attachments/<message_id>
  
  
### Domains
Domains contain the following elements; 

Domain ID, Account ID, Name

#### Domains Routes
GET

  /api/domains
 
  /api/domains/<domain_id>
 
 
POST

  /api/domains/<domain_id>
  
  
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

  /api/accounts/<account_id>
  
  
PUT

  /api/accounts/<account_id>
  
  
DELETE

  /api/accounts/<account_id>
