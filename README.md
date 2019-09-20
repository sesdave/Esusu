Features:
---------
* User registration

* User email verification

* User login

* Admin Create group

* User Search groups

* User Join group

* User Contribute saving

* Admin View group Members

* Admin Invite people to group


API Documentation
-----------------

Postman collection : https://www.getpostman.com/collections/f803c13bd223791d1b21

i. User - Registration
Create/ Register a new user.

	Endpoint 	: /api/register/
	Request Type 	: POST
	Request Params 	: username, email, password, password_2, first_name, last_name

	Response Http status codes : HTTP_200_OK or HTTP_400_BAD_REQUEST
	
	Sample Input 	: https://api.myjson.com/bins/o1id5
	Sample Output 	: https://api.myjson.com/bins/v6pmh

ii. User - Email Verification
Verify the email inorder to activate the user account.

User will recieve an email on successful registration with the verification_code. 
	
	Endpoint 	: /api/accounts/verify/<verification_code>/
	Request Type 	: GET
	
	Response Http status codes : HTTP_200_OK or HTTP_404_NO_CONTENT
	
iii. User - Login
Obtain authentication token given the user credentials.

	Endpoint 	: /api/login/
	Request Type 	: POST
	Request Params 	: email (or username) and password
	
	Response 	: { "token": <token> }
	HTTP status code: HTTP_200_OK or HTTP_400_BAD_REQUEST
	
iv. Group - Create
Create a new group.

	Endpoint 	: /api/create_group/
	Request Type 	: POST
	Request Headers : 
		Authorization : Bearer <token>
	Request Payload	: {"name": <group_name>, "description": <group_description>, "capacity": <group_capacity>, "searchable": <either true/false>}
	
	HTTP status code: HTTP_200_OK or HTTP_400_BAD_REQUEST or HTTP_401_UNAUTHORISED
	
v. User Group Search- Search Available Groups
Receive an email with password reset link.

	Endpoint 	: /api/search_groups?q=<search_value>
	Request Type 	: GET
	
	HTTP status code: HTTP_200_OK

vi. User Join Group - Join available group 

	Endpoint 	: /api/member/
	Request Type 	: POST
	Request Headers : 
		Authorization : Bearer <token>
	Request Payload	: {"groupId": <group_id>}
	
	HTTP status code: HTTP_200_OK
	
vii. User Contribute Group - Contribute savings to group 

	Endpoint 	: /api/contribute/
	Request Type 	: POST
	Request Headers : 
		Authorization : Bearer <token>
	Request Payload	: {"groupId": <group_id>,"saving": <saving_amount>}
	
	HTTP status code: HTTP_200_OK
	
viii. Admin View Group Members - View members by group and total savings 

	Endpoint 	: /api/allmembers
	Request Type 	: GET
	Request Headers : 
		Authorization : Bearer <token>
	Request Payload	: {"groupId": <group_id>}
	
	HTTP status code: HTTP_200_OK
	
ix. Group - Invite
Invite people to join the group.Those invited must be registered on platform.

	Endpoint 	: /api/<groupId>/invite/
	Request Type 	: POST
	Request Headers : 
		Authorization : Bearer <token>
	Request Payload	: {"emails": ["some_email_id@gmail.com"]}
	
	HTTP status code: HTTP_200_OK or HTTP_400_BAD_REQUEST or HTTP_401_UNAUTHORISED
	
x. User - Accept Group Invitation
Accept the email inorder to join group.

User will recieve an email on when the invite email is sent. 
	
	Endpoint 	: /api/accept_invitation/<invitation_code>/
	Request Type 	: GET
	
	Response Http status codes : HTTP_200_OK or HTTP_404_NO_CONTENT

## Invite is sent to email address to be confirmed before you are part of the group

## Run the project Locally ##

i. Clone the repository.

ii. Go to directory of manage.py and install the requirements.

	pip install -r requirements.txt
	
**Note:**
You may configure the virtual environment if required.

For instructions, click here : https://virtualenv.pypa.io/en/latest/installation/
    
iii. Create local_settings.py inside crowise directory.

	EMAIL_HOST_USER = '<to_be_filled>'

	EMAIL_HOST_PASSWORD = '<to_be_filled>'

	DEFAULT_FROM_EMAIL = '<to_be_filled>'

**Note:**
By default, Sqlite3 database is used. You may also use different database in local_settings file if required.

iv. Run migrations

	python manage.py migrate

v. Ready to run the server.

	python manage.py runserver
	
## Configuration Variables ##

#### VERIFICATION_KEY_EXPIRY_DAYS ####

Validity (in days) of user account activation email. Defaulted to 2
	
#### SITE_NAME ####

Name of Website to be displayed on outgoing emails and elsewhere. Defauled to i2x Demo

#### PASSWORD_MIN_LENGTH #### 

A constraint that defines minimum length of password. Defaulted to 8

#### INVITATION_VALIDITY_DAYS #### 

Validity (in days) of user team invitation email. Defaulted to 7


## Try it online: ##
https://dry-stream-50652.herokuapp.com/
	
	
