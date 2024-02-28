import datetime
import requests
import firebase_admin
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from firebase_admin import credentials, auth
# from flask_pymongo import PyMongo
# from flask_mongoengine import MongoEngine
from flask_mail import Mail, Message
from urllib.parse import quote
# from flask_admin import Admin
# from flask_admin.contrib.pymongo import ModelView
# from flask_login import LoginManager, login_required

from forms import HiremeForm

app = Flask(__name__)

NOTION_API_KEY = "secret_JWOHlDkr92kgzI5eXLqNK90SuSEpWeU8uasvdDf8cyo"
DATABASE_ID= "076ee42772584168aac60bd2b8366ce6" 
FIREBASE_DATABASE_URL="https://portfolio-672ef-default-rtdb.firebaseio.com/"

cred = credentials.Certificate("portfolio-672ef-firebase-adminsdk-nocvk-271944b24b.json")
firebase_admin.initialize_app(cred)

app.config['SECRET_KEY'] = '6e6cf3f875a3a73830d88caf'

# Mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'rockbottom0111@gmail.com'
app.config['MAIL_PASSWORD'] = 'omyb xpzn oeok mdqy'
app.config['MAIL_DEFAULT_SENDER'] = 'rockbottom0111@gmail.com'

# mongo = PyMongo(app)
# mongo = MongoEngine(app)
# login_manager = LoginManager(app)
# admin = Admin(app, name='MyBlog', template_mode='bootstrap3')
mail = Mail(app)

def fetch_notion_data():
    url = f'https://api.notion.com/v1/databases/{DATABASE_ID}/query'
    headers = {
        'Authorization': f'Bearer {NOTION_API_KEY}',
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16',
    }
    response = requests.post(url, headers=headers)
    data = response.json()
    
    # for entry in data.get('results', []):
    #     cover_image_url = entry.get('properties', {}).get('CoverImage', {}).get('files', [{}])[0].get('url')
    #     # {{ entry['properties']['coverimg']['files'][0]['url'] }}
    #     print(f"Cover Image URL: {cover_image_url}")

    return data.get('results',[])

def get_entries_for_page(page, per_page):
    entries = fetch_notion_data()
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    print(entries[start_index]) 
    return entries[start_index:end_index]

def has_next_page(page, per_page):
    entries = fetch_notion_data()
    start_index = page * per_page
    return start_index < len(entries)

@app.route("/submit_data", methods=['GET', 'POST'])
def submit_data():
    # Verify Firebase auth.
    try:
        id_token = request.cookies.get("token", "")
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        # If the user is authenticated, allow data submission
        if request.method == 'POST':
            # Handle data submission
            # Extract data from the request and store it in Firebase
            return "Data submitted successfully!"
        
        return render_template('submit_data.html')
    
    except auth.InvalidIdTokenError as e:
        return "Invalid token"
    except auth.ExpiredIdTokenError as e:
        return "Expired token"

# class Blog(mongo.Document):
#     title = mongo.StringField(max_length=200, required=True)
#     content = mongo.StringField(required=True)
#     image = mongo.StringField(max_length=1024, required=True)

# @login_manager.user_loader
# def load_user(user_id):
#     # Implement this function if you are using Flask-Login and have a user model
#     pass

# class BlogView(ModelView):
#     # Customize if needed
#     pass

# admin.add_view(BlogView(Blog, mongo.db))

now = datetime.datetime.now()

current_time = now.strftime(" %I:%M %p")

current_date = now.strftime("%a %b %d ")

@app.route("/")
def hello():
    return render_template("moyemoye.html", time=current_time, date=current_date)

# @app.route("/admin")
# @login_required
# def admin():
#     return render_template("moye.html")
@app.route("/project")
def project():
    return render_template('project.html', time=current_time, date=current_date)
    
@app.route("/blog")
def blog():
    page = request.args.get('page', default=1, type=int)
    per_page = 2
    entries = get_entries_for_page(page, per_page)
    return render_template('blog.html', entries=entries, page=page, per_page=per_page, has_next_page=has_next_page(page, per_page), time=current_time, date=current_date)

# @app.route('/blog/<slug>')
# def blog_detail(slug):
#     entries = fetch_notion_data()
    
#     # Find the entry with the matching slug
#     selected_entry = next((entry for entry in entries if entry.get('slug') == slug), None)
    
#     if not selected_entry:
#         abort(404)  # Return a 404 error if the entry with the specified slug is not found
    
#     return render_template('blog_detail.html', entry=selected_entry)


@app.route("/home")
def home():
    return render_template("home.html", time=current_time, date=current_date)

@app.route("/about")
def about():
    return render_template("about.html", time=current_time, date=current_date)

# @app.route("/blog")
# def blog():
    #     posts = Blog.objects.all()
#     return render_template("blog.html", time=current_time, date=current_date, posts=posts)

@app.route("/hireme", methods=['GET', 'POST'])
def hireme():
    form = HiremeForm()
    if form.validate_on_submit():
        sname = form.name.data
        semail = form.email.data
        smsg = form.msg.data

        msg = Message('New contact Form Submission', recipients=["tanishvashisth@gmail.com"])
        msg.body = f'Name: {sname}\nEmail: {semail}\nMessage: {smsg}'
        mail.send(msg)

        print(f'{sname} from {semail} said {smsg}')
        flash('Message sent successfully', category="success")

        return redirect(url_for('about'))

    if form.errors:
        flash('Please enter the correct details', category="danger")

    return render_template("hireme.html", time=current_time, date=current_date, form=form)




if __name__ == "__main__":
    app.run(debug=True)
