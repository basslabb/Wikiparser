import re
from google.appengine.ext import db
import hashlib
import hmac
import random
import string
from string import letters
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE	= re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

secret ="secret"

def make_salt(length = 5):
	return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name,pw,salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return "%s,%s" % (salt,h)

def make_secure_val(val):
	return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
	val = secure_val.split('|')[0]
	if secure_val == make_secure_val(val):
		return val

def valid_pw(name, password, h):
	salt = h.split(',')[0]
	return h == make_pw_hash(name, password, salt)

def valid_username(raw_username):
	return USER_RE.match(raw_username)

def valid_password(raw_password):
	return PASS_RE.match(raw_password)

def valid_email(raw_email):
	if (raw_email == ""):
		return True
	else:
		return EMAIL_RE.match(raw_email)

def valid_role(raw_role):
	if (raw_role == "admin" or user):
		return True
	else:
		return False

def users_key(group = 'default'):
	return db.Key.from_path('users', group)

class User(db.Model):
	username = db.StringProperty(required=True)
	pw_hash = db.StringProperty(required=True)
	email = db.StringProperty
	role = db.StringProperty(required=True)

	@classmethod
	def by_id(cls, uid):
		return User.get_by_id(uid, parent = users_key())


	@classmethod
	def by_name(cls, name):
		u = User.all().filter("username =", name).get()
		return u
	@classmethod
	def register(cls,name,pw,role,email=None):
		hash_pw = make_pw_hash(name,pw)
		return User(parent = users_key(),
                   username = name,
                   pw_hash = hash_pw,	
                   email = email,
                   role = role)

	@classmethod
	def login(cls, name, pw):
		u = User.by_name(name)
		if u and valid_pw(name, pw, u.pw_hash):
			return u