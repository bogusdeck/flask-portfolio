import datetime
import requests
import base64
import json
import firebase_admin
from flask import Flask, render_template, redirect, url_for, flash, request, abort, session
from firebase_admin import credentials, auth ,db
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

cred = credentials.Certificate("portfolio-672ef-firebase-adminsdk-nocvk-ba1b278397.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://portfolio-672ef-default-rtdb.firebaseio.com/'
})

app.config['SECRET_KEY'] = '6e6cf3f875a3a73830d88caf'

#spotify api credentials
CLIENT_ID = '764a7f7994f84da788a33f333cc5714c'
CLIENT_SECRET = 'bf983ff1785940d8abc1455b22ee158f'
REDIRECT_URI = 'http://localhost:5000/callback'
user_id = '31rrr7lh7gubxpbngbjuns6iagte'
auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

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

def spotify_access_token():
    token_url='https://accounts.spotify.com/api/token'
    token_data={
        'grant_type':'client_credentials'
    }
    token_headers={
        'Authorization':f'Basic {auth_header}',
        'Content-Type' : 'application/x-www-form-urlencoded'
    }
    response = requests.post(token_url, data=token_data, headers=token_headers)

    access_token = response.json().get('access_token')
    
    return access_token

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

def get_projects():
    projects_ref = db.reference('projects')
    projects = projects_ref.get()
    return projects

# @app.route("/submit_data", methods=['GET', 'POST'])
# def submit_data():
#     # Verify Firebase auth.
#     try:
#         id_token = request.cookies.get("token", "")
#         decoded_token = auth.verify_id_token(id_token)
#         uid = decoded_token['uid']
        
#         # If the user is authenticated, allow data submission
#         if request.method == 'POST':
#             # Handle data submission
#             # Extract data from the request and store it in Firebase
#             return "Data submitted successfully!"
        
#         return render_template('submit_data.html')
    
#     except auth.InvalidIdTokenError as e:
#         return "Invalid token"
#     except auth.ExpiredIdTokenError as e:
#         return "Expired token"

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

@app.route('/projects', methods=['GET'])
def projects():
    # Retrieve data from Firebase
    projects = get_projects()
   
    # Pagination parameters
    page = request.args.get('page', 1, type=int)  # Current page number
    per_page = 3  # Number of items per page
    total_projects = len(projects) if projects else 0
    total_pages = (total_projects + per_page - 1) // per_page  # Total number of pages

    # Calculate start and end index for slicing
    start_index = (page - 1) * per_page
    end_index = min(start_index + per_page, total_projects)

    # Get projects for the current page
    pagination_projects = list(projects.values())[start_index:end_index]

    return render_template('project.html', projects=pagination_projects, page=page, per_page=per_page, total_pages=total_pages)

    
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

@app.route("/downloads")
def downloads():
    return render_template("downloads.html", time=current_time, date=current_date)

@app.route("/music.html")
def music():
    user_id = '31rrr7lh7gubxpbngbjuns6iagte'
    playlists_url = "https://api.spotify.com/v1/users/31rrr7lh7gubxpbngbjuns6iagte/playlists"
    at = spotify_access_token()
    print(at)
    headers = {'Authorization': f'Bearer {at}'}
    response = requests.get(playlists_url, headers=headers)

    if response.status_code == 200:
        playlists_data = response.json().get('items',[])
    else:
        print(f"Failed to fetch playlists. Status code: {response.status_code}")
        playlists_data = []

    print(playlists_data)

    return render_template("music.html",playlists=playlists_data, time=current_date, date=current_date)

@app.route('/playlist/<slug>')
def playlist_detail(slug):
    playlist_id = slug

    if not playlist_id:
        abort(404)
    
    playlist_url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    access_token = spotify_access_token()
    headers = {'Authorization':f'Bearer {access_token}'}
    response = requests.get(playlist_url, headers= headers)

    if response.status_code==200:
        playlist_data= response.json()
        return render_template('playlist.html', playlist=playlist_data)
    else:
        abort(404)



if __name__ == "__main__":
    app.run(debug=True)
    
