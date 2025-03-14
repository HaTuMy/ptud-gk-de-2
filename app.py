from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from datetime import datetime
import os
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import random

# Add allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)
    tasks = db.relationship('Task', backref='user', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tasks = db.relationship('Task', backref='category', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    finished_time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_random_avatar():
    # Using DiceBear's avatar service with random styles and seeds
    styles = ['adventurer', 'avataaars', 'bottts', 'fun-emoji', 'lorelei']
    style = random.choice(styles)
    seed = str(random.randint(1, 1000000))
    return f"https://api.dicebear.com/7.x/{style}/svg?seed={seed}"

# Routes
@app.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    categories = Category.query.all()
    return render_template('index.html', tasks=tasks, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        avatar_url = get_random_avatar()
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            avatar=avatar_url
        )
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/task/add', methods=['POST'])
@login_required
def add_task():
    title = request.form.get('title')
    description = request.form.get('description')
    category_id = request.form.get('category_id')
    
    if not title:
        flash('Task title is required')
        return redirect(url_for('index'))
    
    try:
        category_id = int(category_id) if category_id else None
        if category_id:
            category = Category.query.get(category_id)
            if not category:
                flash('Selected category does not exist')
                return redirect(url_for('index'))
    except ValueError:
        flash('Invalid category selection')
        return redirect(url_for('index'))
    
    task = Task(
        title=title,
        description=description,
        user_id=current_user.id,
        category_id=category_id
    )
    db.session.add(task)
    db.session.commit()
    flash('Task added successfully!')
    return redirect(url_for('index'))

@app.route('/task/<int:task_id>/complete')
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id == current_user.id:
        task.status = 'completed'
        task.finished_time = datetime.utcnow()
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Category name is required')
            return redirect(url_for('manage_categories'))
        
        # Check if category already exists
        existing_category = Category.query.filter_by(name=name).first()
        if existing_category:
            flash('A category with this name already exists')
            return redirect(url_for('manage_categories'))
        
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!')
        
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        if 'avatar' not in request.files:
            flash('No file selected')
            return redirect(url_for('profile'))
        
        file = request.files['avatar']
        if file.filename == '':
            flash('No file selected')
            return redirect(url_for('profile'))
        
        if file and allowed_file(file.filename):
            # Create a unique filename
            filename = secure_filename(f"avatar_{current_user.id}_{int(datetime.now().timestamp())}{os.path.splitext(file.filename)[1]}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the file
            file.save(file_path)
            
            # Update user's avatar URL
            current_user.avatar = url_for('static', filename=f'uploads/{filename}')
            db.session.commit()
            
            flash('Avatar updated successfully!')
            return redirect(url_for('profile'))
        else:
            flash('Invalid file type. Please use PNG, JPG, JPEG, or GIF.')
            
    return render_template('profile.html')

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to edit this task.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        
        if not title:
            flash('Title is required!')
            return redirect(url_for('index'))
        
        task.title = title
        task.description = description
        if category_id:
            category = Category.query.get(category_id)
            if category:
                task.category_id = category_id
        
        db.session.commit()
        flash('Task updated successfully!')
        return redirect(url_for('index'))
    
    return redirect(url_for('index'))

@app.route('/delete_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to delete this task.')
        return redirect(url_for('index'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 