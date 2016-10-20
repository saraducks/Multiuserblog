import os
import time
import webapp2
import jinja2
import re
from jinja2 import Environment,FileSystemLoader
from google.appengine.ext import db
import datetime

temp_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja = jinja2.Environment(loader=FileSystemLoader(temp_dir),
	                autoescape = True)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
MAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

def renderstr(template, **params):
		t = jinja.get_template(template)
		return t.render(params)

def getkey(name="default"):
	return db.Key.from_path('blog',name)

def checktitle(t):
	if t:
		return t
	else:
		return "Enter the title for the new post"
def checkdescription(t):
	if t:
		return t
	else:
		return "Enter the description for the new post"

# The basehandler will perform template rendering and display output
class BaseHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a,**kw)

	def renderstr(self, template, **params):
		return renderstr(template,**params)

	def render(self,template, **kw):
		self.write(self.renderstr(template, **kw))

# This class will define data model 
class Post(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)
	
	def render(self):
		return render('blog.html',displayblog=self)

# This will display the content user has posted into the blog
class Postcontent(BaseHandler):
	def get(self,id):
		res = db.Key.from_path('Post',int(id),parent=getkey())
		post = db.get(res)

		if post:
			self.render('specificcontent.html',post = post)

#Allows user to create new post and redirect them to Postcontent
class NewPage(BaseHandler):
	def write_form(self,inputone="",inputwo=""):
			self.render('newblog.html' % {"content":inputone,"description":inputwo})
	def get(self):
		self.render('newblog.html')
	def post(self):
		getitle = self.request.get('usertitle')
		getdescription = self.request.get('description')
		if getitle and getdescription:
			temp = Post(parent = getkey(),subject = getitle,content = getdescription)
			temp.put()
			self.redirect('/postcontent/%s' % str(temp.key().id()))
		else:
			error = "Require both fields"
			self.render('newblog.html',error = error)
			
#This will display all the posts made by the user
class MainPage(BaseHandler): 
	def get(self):
		posts = db.GqlQuery("select * from Post order by created desc")
		self.render('fronpage.html',posts= posts)

#welcomes the registered user
class WelcomeMessage(BaseHandler):
	def get(self):
		self.render('welcome.html')

#check for form validation 
check = True
#check if name is valid
def checkname(getname):
	if USER_RE.match(getname):
		check = True
		return getname
	else:
		check = False
		return "Enter valid name"

#check if password is valid
def checkpassword(getpassword,getconfirmationpassword):
	if (getpassword == getconfirmationpassword) and PASS_RE.match(getconfirmationpassword):
		check = True
		return getconfirmationpassword
	else:
		check = False
		return "Enter valid password"
        
#check if mail id is valid
def checkmail(getemail):
	if MAIL_RE.match(getemail):
		check = True
		return getemail
	else:
		check = False
		return "Enter valid mail id"

class user(db.Model):
	name = db.StringProperty(required = True)
	password = db.TextProperty(required = True)
	email = db.StringProperty(required = False)

class userhandler(BaseHandler):
	def get(self,name,password,mail):
		res = name
		print name
		checkuser = db.Key.from_path('user',str(name))
		resulofusercheck = db.get(checkuser)
		print resulofusercheck

		if resulofusercheck == True:
			error = "user name already exists"
			self.render('signup.html',error=error)
		else:
			temp = user(name = name,password = password,mail=mail)
			temp.put()
			print temp
			self.render('signup.html',name=name,password=password,email=mail)
        	
#Helps user to register 
class signup(BaseHandler):
	def get(self):
		self.render('signup.html')
	def post(self):
		getname = self.request.get('name')
		getpassword = self.request.get('password')
		getconfirmationpassword = self.request.get('re-typepassword')
		getemail = self.request.get('email')
		resname = checkname(getname)
		respass = checkpassword(getpassword,getconfirmationpassword)
		resmail = checkmail(getemail)
		
		if (resname and respass and resmail) == True:
			self.redirect('/usercheck',name=resname,password=respass,mail=resmail)
		elif (resname and respass) == True:
			self.redirect('/usercheck',name=resname,password=respass,mail="")
		else:
			self.redirect('/welcome',getname)


app = webapp2.WSGIApplication([('/register',signup),
	                           ('/main',MainPage),
	                           ('/newpage',NewPage), 
	                           ('/postcontent/([0-9]+)',Postcontent),
	                           ('/welcome',WelcomeMessage),
	                           ('/usercheck',userhandler),],debug = True)	