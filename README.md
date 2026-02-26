# 🚀 DD-Solutions Portfolio — Complete Setup & Deployment Guide

**Founded by:** Singothu Dinesh  
**Purpose:** Empowering students (10th–B.Tech) and working professionals

---

## 📁 Folder Structure

```
dd-solutions/
├── index.html                  ← Main frontend (self-contained)
├── README.md
│
├── backend/
│   ├── app.py                  ← Flask REST API
│   ├── requirements.txt
│   ├── .env.example
│   ├── schema.py               ← MongoDB collection schemas
│   └── Procfile                ← For Render deployment
│
└── assets/                     ← (optional) images, icons
    ├── logo.png
    └── og-image.png
```

---

## 🖥️ Tech Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| Frontend    | HTML5, CSS3, JavaScript ES6+      |
| 3D/Animation| Three.js r128, GSAP 3.12          |
| Backend     | Python 3.11 + Flask 3.0           |
| Database    | MongoDB Atlas (free tier)         |
| Auth        | JWT (HS256) + bcrypt              |
| Email       | Flask-Mail + Gmail SMTP           |
| Hosting     | Vercel (frontend) + Render (API)  |

---

## ⚡ Quick Start (Local)

### 1. Frontend
```bash
# Just open index.html in any browser — no build step needed!
open index.html
# OR serve locally:
python -m http.server 8080
# Visit: http://localhost:8080
```

### 2. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your MongoDB URI and Gmail credentials

# Run development server
python app.py
# API running at: http://localhost:5000
```

---

## 🌐 Deployment

### Frontend → Vercel (Free, CDN, HTTPS)

1. Push your project to GitHub
2. Go to [vercel.com](https://vercel.com) → New Project
3. Import your GitHub repo
4. Set **Framework Preset**: Other
5. Set **Output Directory**: `.` (root)
6. Click **Deploy**
7. Your site is live at: `https://dd-solutions.vercel.app`

**Custom Domain:**
- In Vercel dashboard → Domains → Add `ddsolutions.in`
- Update DNS: CNAME → `cname.vercel-dns.com`

### Backend API → Render (Free Tier)

1. Create `backend/Procfile`:
   ```
   web: gunicorn app:app --bind 0.0.0.0:$PORT
   ```
2. Go to [render.com](https://render.com) → New Web Service
3. Connect GitHub repo → select `backend/` folder
4. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Add Environment Variables (from `.env`):
   - `SECRET_KEY`, `MONGO_URI`, `MAIL_USERNAME`, `MAIL_PASSWORD`
6. Deploy → API live at: `https://dd-solutions-api.onrender.com`

### Database → MongoDB Atlas (Free 512MB)

1. Sign up at [cloud.mongodb.com](https://cloud.mongodb.com)
2. Create free cluster (M0 Sandbox)
3. Create database user with read/write
4. Add IP `0.0.0.0/0` to Network Access
5. Copy connection string → paste in `.env` as `MONGO_URI`
6. Collections auto-created on first insert

---

## 🔑 API Endpoints

```
POST   /api/auth/register       Register new user
POST   /api/auth/login          Login → returns JWT token

GET    /api/user/profile        Get own profile (auth)
PUT    /api/user/profile        Update profile (auth)
GET    /api/user/progress       Get progress data (auth)
PUT    /api/user/progress       Update progress (auth)

GET    /api/resume              List resumes (auth)
POST   /api/resume              Create resume (auth)
PUT    /api/resume/:id          Update resume (auth)

GET    /api/records             List records (auth)
POST   /api/records             Add record (auth)

POST   /api/contact             Contact form (public)
POST   /api/newsletter/subscribe Subscribe (public)

GET    /api/blog                List blog posts (public)
POST   /api/admin/blog          Create post (admin only)
GET    /api/admin/users         List all users (admin only)
GET    /api/admin/stats         Dashboard stats (admin only)
GET    /api/admin/contacts      Contact submissions (admin only)

GET    /api/testimonials        Public testimonials
POST   /api/testimonials        Submit review (auth)

GET    /api/health              Health check
```

---

## 🔒 Authentication

All protected routes require:
```
Authorization: Bearer <JWT_TOKEN>
```

**Roles:**
- `student` — Access own dashboard, resume, records
- `professional` — Extended dashboard features
- `admin` — Full access including content management

---

## 🌍 Multi-Language Support

Built-in translations:
- **English** (default)
- **Telugu** (తెలుగు)
- **Hindi** (हिंदी)

To add more languages, extend the `translations` object in `index.html`.

---

## 📱 Instagram Bio Link

Once deployed, paste your Vercel URL in Instagram bio:
```
🎯 Empowering Students & Professionals
📚 Career Mentorship | Resume Builder | Job Placement
🔗 https://dd-solutions.vercel.app
```

---

## 🎨 Customization

### Change Colors
In `index.html` CSS `:root`:
```css
--accent-1: #6c63ff;    /* Primary purple */
--accent-2: #a855f7;    /* Secondary purple */
--accent-3: #38bdf8;    /* Accent blue */
```

### Add WhatsApp Number
Replace `+91XXXXXXXXXX` with your actual number in `index.html`.

### Add Instagram Handle
Replace `@ddsolutions.in` with your actual Instagram username.

---

## 📊 SEO Checklist

- [x] Meta title & description
- [x] Open Graph tags
- [x] Semantic HTML5 structure
- [x] Mobile responsive
- [x] Fast loading (no heavy dependencies in critical path)
- [ ] Add `sitemap.xml`
- [ ] Add `robots.txt`
- [ ] Submit to Google Search Console

---

## 💡 Future Enhancements

- [ ] Payment gateway (Razorpay) for premium plans
- [ ] Video mentorship (WebRTC / Daily.co)
- [ ] AI resume score (OpenAI API)
- [ ] Mobile app (React Native)
- [ ] Certificates with QR verification
- [ ] Referral program

---

*Built with ❤️ by Singothu Dinesh | DD-Solutions © 2025*
