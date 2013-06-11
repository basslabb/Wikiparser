#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
import logging
import user
#from wikiParser import wikiParser
import wikiParser
import basehandler
import event
from google.appengine.ext import db
import ast


class MainHandler(basehandler.BaseHandler):
    def get(self):
    	self.render("main.html")
class DetailsHandler(basehandler.BaseHandler):
	def get(self,id):
		try:
			#e = event.Event.by_id(id)
			e = event.Event.get_by_id(int(id))
			d = event.Event.as_Dict(e)
			#d = {"date":e.date,"text":e.text,"keywords":ast.literal_eval(e.keywords)}
			self.render("detail.html",event=d)
		except Exception,e:
			self.response.out.write(e)

class UserSignUp(basehandler.BaseHandler):
	def get(self):
		self.render("signup-form.html")
	#The user should not be able to set their own role of course
	#An admin interface is a TODO
	def post(self):
		self.username = self.request.get("username")
		self.password = self.request.get("password")
		self.verify = self.request.get("verify")
		self.email = self.request.get("email")
		self.role = self.request.get("role")
		
		userMessage = ""
		passMessage = ""
		verify_Message = ""
		email_Message = ""
		role_Message = ""
		
		validRole = user.valid_role(self.role)
		validUserName = user.valid_username(self.username)
		#validUserName = USER_RE.match(username)
		validPassword = user.valid_password(self.password)
		validEmail = user.valid_email(self.email)
		if (validUserName and validPassword and (self.verify == self.password) and validEmail and validRole):
			self.done()
		else:
			if not validUserName:
				userMessage = "Incorrect username"
			
			if not validPassword:
				passMessage = "Incorrect password"
				
			if not validEmail:
				email_Message = "Incorrect email"
				
			if not self.verify == self.password:
				verify_Message = "The passwords didn't match"

			if not validRole:
				role_Message = "Incorrect role"
			
			self.render("signup-form.html", usernameMessage=userMessage, 
				passwordMessage=passMessage,
				verifyMessage = verify_Message, 
			emailMessage = email_Message,
			roleMessage = role_Message,
			usernameValue=username, 
			emailValue=email,
			roleValue=role)

	def done(self, *a, **kw):
		raise NotImplementedError

class SignupHandler(UserSignUp):
	def done(self):
		#make sure the user doesn't already exist
		u = user.User.by_name(self.username)
		if u:
			msg = 'That user already exists.'
			self.render('signup-form.html', usernameMessage = msg)
		else:
			u = user.User.register(self.username, self.password,self.role, self.email)
			u.put()

			self.login(u)
			self.redirect('/')

class Login(basehandler.BaseHandler):
	def get(self):
		self.render("login-form.html")

	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")

		u = user.User.login(username,password)
		if u:
			self.login(u)
			self.response.set_cookie('user', username, path='/')
			self.redirect("/")
		else:
			msg = "Wrong credentials"
			self.render("login-form.html",error=msg)

class Logout(basehandler.BaseHandler):
	def get(self):
		self.response.delete_cookie('user')
		self.logout()
		self.redirect('/')

class ParseHandler(basehandler.BaseHandler):
	def get(self):
		if self.user and self.user.role == "admin":
			logging.error(self.user.role)
			self.render("parsePostPage.html")
		else:
			self.abort(403)
		"""if seluser =="admin":
			self.render("parsePostPage.html")
		"""
		


	def post(self):
		start_year = self.request.get("start_year")
		end_year = self.request.get("end_year")
		if start_year and end_year:
			try:
				start_year = int(start_year)
				end_year = int(end_year)
			except:
				self.response.out.write("Has to be integer value")
			#A correct start and end year
			if int(start_year) < int(end_year) or int(start_year) == int(end_year):
				print "Equal"
				db.delete(event.Event.all())
				w = wikiParser.WikiParse(start_year,end_year)
				self.response.out.write("%s %s" % (start_year,end_year))

			else:
				self.response.out.write("End year has to equal, or be larger than start year")
		else:
			self.response.out.write("Has to have startyear and endyear")
	

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/parse', ParseHandler),
    ('/event/(\d+)/detail', DetailsHandler),
    ("/signup",SignupHandler),
    ('/login', Login),
    ('/logout', Logout),
], debug=True)
