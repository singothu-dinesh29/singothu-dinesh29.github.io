# DD-Solutions MongoDB Schema
# Collection definitions and indexes

"""
DATABASE: ddsolutions

COLLECTIONS:
============

1. users
{
  _id: ObjectId,
  first_name: String,
  last_name: String,
  email: String (unique),
  password: String (bcrypt hashed),
  role: String ("student" | "professional" | "admin"),
  phone: String,
  college: String,
  bio: String,
  skills: [String],
  profile: {
    linkedin: String,
    github: String,
    website: String,
    city: String,
    state: String
  },
  progress: {
    career_readiness: Number (0-100),
    sessions: Number,
    skills_added: Number
  },
  avatar_url: String,
  is_active: Boolean (default: true),
  created_at: Date,
  updated_at: Date
}
INDEXES: email (unique), role, created_at

2. resumes
{
  _id: ObjectId,
  user_id: String (ref: users._id),
  title: String,
  template: String ("modern"|"classic"|"minimal"),
  version: Number,
  personal: {
    name: String, email: String, phone: String,
    linkedin: String, github: String, website: String,
    address: String, summary: String
  },
  education: [{
    institution: String, degree: String,
    field: String, start: String, end: String,
    gpa: String, achievements: String
  }],
  experience: [{
    company: String, title: String,
    start: String, end: String,
    description: String, tech_stack: [String]
  }],
  skills: [{ name: String, level: Number }],
  projects: [{
    name: String, description: String,
    tech: [String], url: String, github: String
  }],
  certifications: [{
    name: String, issuer: String,
    date: String, url: String
  }],
  is_public: Boolean,
  created_at: Date,
  updated_at: Date
}
INDEXES: user_id, created_at

3. records
{
  _id: ObjectId,
  user_id: String,
  type: String ("certificate"|"achievement"|"project"|"internship"),
  title: String,
  description: String,
  issuer: String,
  date: Date,
  file_url: String,
  tags: [String],
  created_at: Date
}
INDEXES: user_id, type

4. progress
{
  _id: ObjectId,
  user_id: String (unique),
  career_readiness: Number,
  skills: { communication: Number, technical: Number, leadership: Number, problem_solving: Number },
  sessions_attended: Number,
  sessions_booked: [{ mentor_id: String, date: Date, status: String }],
  jobs_applied: Number,
  resume_views: Number,
  weekly_goals: [{ goal: String, completed: Boolean }],
  updated_at: Date
}
INDEXES: user_id (unique)

5. contacts
{
  _id: ObjectId,
  name: String,
  email: String,
  phone: String,
  role: String,
  message: String,
  status: String ("new"|"read"|"replied"),
  created_at: Date
}
INDEXES: status, created_at

6. newsletter
{
  _id: ObjectId,
  email: String (unique),
  name: String,
  subscribed_at: Date,
  active: Boolean
}
INDEXES: email (unique)

7. blog
{
  _id: ObjectId,
  title: String,
  slug: String (unique),
  content: String,
  excerpt: String,
  tags: [String],
  cover_image: String,
  author_id: String,
  author_name: String,
  published: Boolean,
  views: Number,
  created_at: Date,
  updated_at: Date
}
INDEXES: slug (unique), published, tags

8. testimonials
{
  _id: ObjectId,
  user_id: String,
  name: String,
  role: String,
  text: String,
  rating: Number (1-5),
  avatar_color: String,
  approved: Boolean,
  created_at: Date
}
INDEXES: approved, created_at

9. sessions (mentor sessions)
{
  _id: ObjectId,
  student_id: String,
  mentor_id: String,
  scheduled_at: Date,
  duration: Number (minutes),
  type: String ("career"|"resume"|"mock_interview"|"general"),
  status: String ("booked"|"completed"|"cancelled"),
  notes: String,
  feedback: String,
  rating: Number,
  created_at: Date
}
INDEXES: student_id, mentor_id, scheduled_at, status
"""
