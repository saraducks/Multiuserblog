import os
import time
import webapp2
import jinja2
from jinja2 import Environment,FileSystemLoader
from google.appengine.ext import db
import datetime

temp_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja = jinja2.Environment(loader=FileSystemLoader(temp_dir),
	                autoescape = True)
mysystime = time.ctime()

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

class BaseHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a,**kw)

	def renderstr(self, template, **params):
		return renderstr(template,**params)

	def render(self,template, **kw):
		self.write(self.renderstr(template, **kw))

class Post(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)
	
	def render(self):
		return render('blog.html',displayblog=self)

class Postcontent(BaseHandler):
	def get(self,id):
		res = db.Key.from_path('Post',int(id),parent=getkey())
		post = db.get(res)
		print post.content

		if post:
			self.render('specificcontent.html',post = post)

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
			
class MainPage(BaseHandler): 
	def get(self):
		posts = db.GqlQuery("select * from Post order by created desc")
		self.render('fronpage.html',posts= posts)


app = webapp2.WSGIApplication([('/main',MainPage),('/newpage',NewPage),('/postcontent/([0-9]+)',Postcontent)],debug = True)