# Academic Lens 📊

## Student Performance Analyzer

Academic Lens is a web-based **Student Performance Management System** developed using **Flask and MySQL**. It helps educational institutions manage student academic information, marks, attendance, and performance through an interactive and user-friendly dashboard.

The system provides separate interfaces for **administrators and students**, allowing academic data to be managed efficiently and presented through charts, statistics, and performance indicators.

---

## ✨ Features

### 👨‍💼 Admin Features

- Secure Admin Login
- Admin Dashboard
- Add Students
- View Students
- Delete Students
- Manage Student Marks
- Manage Student Attendance
- View Individual Student Performance
- Search Students
- View Academic Statistics
- Subject-wise Performance Analysis

### 👨‍🎓 Student Features

- Student Login
- Student Dashboard
- Student Profile
- View Performance
- View Attendance
- View Subjects
- View Academic Statistics
- Performance Status Badge

### 📈 Data Visualization

- Internal Examination Line Chart
- Attendance Pie Chart
- Subject-wise Marks
- Average Marks
- Attendance Percentage
- Total Subjects
- Performance Status

### 🎨 User Interface

- Modern Dashboard Design
- Responsive Layout
- Light Mode
- Dark Mode
- Interactive Cards
- Navigation Sidebar/Navbar
- Font Awesome Icons
- Bootstrap Components

---

## 🛠️ Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend Programming |
| Flask | Web Framework |
| MySQL | Database |
| HTML5 | Page Structure |
| CSS3 | Styling |
| JavaScript | Frontend Interactivity |
| Chart.js | Data Visualization |
| Bootstrap | Responsive UI |
| Font Awesome | Icons |
| Git & GitHub | Version Control |

---

## 📂 Project Structure

```text
academic-lens-student-performance-dashboard/
│
├── app.py
├── database.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── database/
│   └── academic_lens.sql
│
├── templates/
│   ├── login.html
│   ├── admin_dashboard.html
│   ├── student_dashboard.html
│   ├── add_student.html
│   ├── add_marks.html
│   ├── add_attendance.html
│   ├── students.html
│   ├── student_performance.html
│   ├── student_attendance.html
│   ├── student_subjects.html
│   └── student_profile.html
│
└── static/
    ├── style.css
    ├── script.js
    └── images/