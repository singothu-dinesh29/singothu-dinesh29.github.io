"""
DD-Solutions Backend — Flask REST API
Founder: Singothu Dinesh
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo
from flask_mail import Mail, Message
import jwt
import datetime
import os
from functools import wraps
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ── Config ───────────────────────────────────────────────────
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dd-solutions-secret-2025')
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ddsolutions')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

bcrypt = Bcrypt(app)
mongo = PyMongo(app)
mail = Mail(app)

# ── JWT Decorator ─────────────────────────────────────────────
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = mongo.db.users.find_one({'_id': ObjectId(data['user_id'])})
        except Exception:
            return jsonify({'error': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(current_user, *args, **kwargs):
            if current_user.get('role') not in roles:
                return jsonify({'error': 'Access denied'}), 403
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator

def serialize(doc):
    """Convert MongoDB document to JSON-serializable dict."""
    doc['_id'] = str(doc['_id'])
    return doc

# ═══════════════════════════════════════════════════════════════
#  AUTH ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    required = ['first_name', 'last_name', 'email', 'password', 'role']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    if data['role'] not in ['student', 'professional', 'admin']:
        return jsonify({'error': 'Invalid role'}), 400

    if mongo.db.users.find_one({'email': data['email']}):
        return jsonify({'error': 'Email already registered'}), 409

    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = {
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'email': data['email'],
        'password': hashed,
        'role': data['role'],
        'created_at': datetime.datetime.utcnow(),
        'profile': {},
        'skills': [],
        'progress': {'career_readiness': 0, 'sessions': 0},
    }
    result = mongo.db.users.insert_one(user)
    return jsonify({'message': 'Registration successful', 'user_id': str(result.inserted_id)}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = mongo.db.users.find_one({'email': data.get('email')})
    if not user or not bcrypt.check_password_hash(user['password'], data.get('password', '')):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = jwt.encode({
        'user_id': str(user['_id']),
        'role': user['role'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({
        'token': token,
        'role': user['role'],
        'name': f"{user['first_name']} {user['last_name']}"
    })

# ═══════════════════════════════════════════════════════════════
#  USER / DASHBOARD ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify(serialize(current_user))

@app.route('/api/user/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json()
    allowed = ['first_name', 'last_name', 'phone', 'college', 'bio', 'skills', 'profile']
    update = {k: v for k, v in data.items() if k in allowed}
    mongo.db.users.update_one({'_id': ObjectId(current_user['_id'])}, {'$set': update})
    return jsonify({'message': 'Profile updated'})

@app.route('/api/user/progress', methods=['GET'])
@token_required
def get_progress(current_user):
    progress = mongo.db.progress.find_one({'user_id': str(current_user['_id'])}) or {}
    return jsonify(serialize(progress) if progress else {})

@app.route('/api/user/progress', methods=['PUT'])
@token_required
def update_progress(current_user):
    data = request.get_json()
    mongo.db.progress.update_one(
        {'user_id': str(current_user['_id'])},
        {'$set': {**data, 'updated_at': datetime.datetime.utcnow()}},
        upsert=True
    )
    return jsonify({'message': 'Progress updated'})

# ═══════════════════════════════════════════════════════════════
#  RESUME BUILDER
# ═══════════════════════════════════════════════════════════════

@app.route('/api/resume', methods=['GET'])
@token_required
def get_resumes(current_user):
    resumes = list(mongo.db.resumes.find({'user_id': str(current_user['_id'])}))
    return jsonify([serialize(r) for r in resumes])

@app.route('/api/resume', methods=['POST'])
@token_required
def create_resume(current_user):
    data = request.get_json()
    resume = {
        'user_id': str(current_user['_id']),
        'title': data.get('title', 'My Resume'),
        'template': data.get('template', 'modern'),
        'personal': data.get('personal', {}),
        'education': data.get('education', []),
        'experience': data.get('experience', []),
        'skills': data.get('skills', []),
        'projects': data.get('projects', []),
        'certifications': data.get('certifications', []),
        'created_at': datetime.datetime.utcnow(),
        'updated_at': datetime.datetime.utcnow(),
        'version': 1
    }
    result = mongo.db.resumes.insert_one(resume)
    return jsonify({'message': 'Resume created', 'id': str(result.inserted_id)}), 201

@app.route('/api/resume/<resume_id>', methods=['PUT'])
@token_required
def update_resume(current_user, resume_id):
    data = request.get_json()
    data['updated_at'] = datetime.datetime.utcnow()
    mongo.db.resumes.update_one(
        {'_id': ObjectId(resume_id), 'user_id': str(current_user['_id'])},
        {'$set': data, '$inc': {'version': 1}}
    )
    return jsonify({'message': 'Resume updated'})

# ═══════════════════════════════════════════════════════════════
#  STUDENT RECORDS
# ═══════════════════════════════════════════════════════════════

@app.route('/api/records', methods=['GET'])
@token_required
def get_records(current_user):
    records = list(mongo.db.records.find({'user_id': str(current_user['_id'])}))
    return jsonify([serialize(r) for r in records])

@app.route('/api/records', methods=['POST'])
@token_required
def add_record(current_user):
    data = request.get_json()
    record = {
        'user_id': str(current_user['_id']),
        'type': data.get('type'),       # 'certificate', 'achievement', 'project'
        'title': data.get('title'),
        'description': data.get('description'),
        'date': data.get('date'),
        'file_url': data.get('file_url'),
        'created_at': datetime.datetime.utcnow()
    }
    result = mongo.db.records.insert_one(record)
    return jsonify({'message': 'Record added', 'id': str(result.inserted_id)}), 201

# ═══════════════════════════════════════════════════════════════
#  CONTACT / NEWSLETTER
# ═══════════════════════════════════════════════════════════════

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json()
    required = ['name', 'email', 'message']
    for f in required:
        if not data.get(f):
            return jsonify({'error': f'{f} is required'}), 400

    mongo.db.contacts.insert_one({
        **data,
        'status': 'new',
        'created_at': datetime.datetime.utcnow()
    })

    try:
        msg = Message(
            subject=f"New Contact: {data['name']}",
            recipients=[os.getenv('ADMIN_EMAIL', 'admin@ddsolutions.in')],
            body=f"Name: {data['name']}\nEmail: {data['email']}\nRole: {data.get('role','')}\n\n{data['message']}"
        )
        mail.send(msg)
    except Exception:
        pass  # Don't fail if mail is misconfigured

    return jsonify({'message': 'Message received! We\'ll respond within 24 hours.'})

@app.route('/api/newsletter/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email required'}), 400
    existing = mongo.db.newsletter.find_one({'email': email})
    if existing:
        return jsonify({'message': 'Already subscribed!'})
    mongo.db.newsletter.insert_one({'email': email, 'subscribed_at': datetime.datetime.utcnow()})
    return jsonify({'message': 'Subscribed successfully!'})

# ═══════════════════════════════════════════════════════════════
#  ADMIN ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route('/api/admin/users', methods=['GET'])
@role_required('admin')
def admin_get_users(current_user):
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    role_filter = request.args.get('role')
    query = {'role': role_filter} if role_filter else {}
    users = list(mongo.db.users.find(query, {'password': 0}).skip((page-1)*limit).limit(limit))
    total = mongo.db.users.count_documents(query)
    return jsonify({'users': [serialize(u) for u in users], 'total': total, 'page': page})

@app.route('/api/admin/stats', methods=['GET'])
@role_required('admin')
def admin_stats(current_user):
    return jsonify({
        'total_users': mongo.db.users.count_documents({}),
        'students': mongo.db.users.count_documents({'role': 'student'}),
        'professionals': mongo.db.users.count_documents({'role': 'professional'}),
        'contacts': mongo.db.contacts.count_documents({}),
        'new_contacts': mongo.db.contacts.count_documents({'status': 'new'}),
        'newsletter_subs': mongo.db.newsletter.count_documents({}),
        'resumes': mongo.db.resumes.count_documents({}),
    })

@app.route('/api/admin/contacts', methods=['GET'])
@role_required('admin')
def admin_contacts(current_user):
    contacts = list(mongo.db.contacts.find().sort('created_at', -1).limit(50))
    return jsonify([serialize(c) for c in contacts])

@app.route('/api/admin/blog', methods=['POST'])
@role_required('admin')
def create_blog_post(current_user):
    data = request.get_json()
    post = {
        'title': data['title'],
        'content': data['content'],
        'excerpt': data.get('excerpt', ''),
        'tags': data.get('tags', []),
        'author_id': str(current_user['_id']),
        'author_name': f"{current_user['first_name']} {current_user['last_name']}",
        'published': data.get('published', False),
        'created_at': datetime.datetime.utcnow()
    }
    result = mongo.db.blog.insert_one(post)
    return jsonify({'message': 'Post created', 'id': str(result.inserted_id)}), 201

@app.route('/api/blog', methods=['GET'])
def get_blog():
    posts = list(mongo.db.blog.find({'published': True}).sort('created_at', -1).limit(10))
    return jsonify([serialize(p) for p in posts])

# ═══════════════════════════════════════════════════════════════
#  TESTIMONIALS (public)
# ═══════════════════════════════════════════════════════════════

@app.route('/api/testimonials', methods=['GET'])
def get_testimonials():
    items = list(mongo.db.testimonials.find({'approved': True}).limit(12))
    return jsonify([serialize(t) for t in items])

@app.route('/api/testimonials', methods=['POST'])
@token_required
def submit_testimonial(current_user):
    data = request.get_json()
    t = {
        'user_id': str(current_user['_id']),
        'name': f"{current_user['first_name']} {current_user['last_name']}",
        'role': data.get('role', current_user.get('role', '')),
        'text': data['text'],
        'rating': data.get('rating', 5),
        'approved': False,
        'created_at': datetime.datetime.utcnow()
    }
    mongo.db.testimonials.insert_one(t)
    return jsonify({'message': 'Testimonial submitted for review!'})

# ═══════════════════════════════════════════════════════════════
#  HEALTH CHECK
# ═══════════════════════════════════════════════════════════════

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'service': 'DD-Solutions API', 'version': '1.0.0'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
