import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from database import get_db_connection


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "development-secret-key"
)


# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return decorated_function


# =========================================================
# ROLE CHECK
# =========================================================

def student_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        if session.get("role") != "student":
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return decorated_function


def admin_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        if session.get("role") != "admin":
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return decorated_function


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return redirect(url_for("login"))


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        connection = None
        cursor = None

        try:

            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            # -------------------------------------------------
            # CHECK STUDENT
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT *
                FROM students
                WHERE email = %s
                AND password = %s
                """,
                (email, password)
            )

            student = cursor.fetchone()

            if student:

                session.clear()

                session["user_id"] = student["id"]
                session["user_name"] = student["name"]
                session["role"] = "student"

                return redirect(url_for("student_dashboard"))

            # -------------------------------------------------
            # CHECK ADMIN
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT *
                FROM admins
                WHERE username = %s
                AND password = %s
                """,
                (email, password)
            )

            admin = cursor.fetchone()

            if admin:

                session.clear()

                session["user_id"] = admin["id"]
                session["user_name"] = admin["username"]
                session["role"] = "admin"

                return redirect(url_for("admin_dashboard"))

            return render_template(
                "login.html",
                error="Invalid username/email or password"
            )

        except Exception as e:

            print("LOGIN ERROR:", e)

            return render_template(
                "login.html",
                error="Database error. Check your MySQL connection."
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@app.route("/student/dashboard")
@student_required
def student_dashboard():

    student_id = session["user_id"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # -----------------------------------------------------
    # STUDENT DETAILS
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT *
        FROM students
        WHERE id = %s
        """,
        (student_id,)
    )

    student = cursor.fetchone()

    if not student:

        cursor.close()
        connection.close()

        session.clear()

        return redirect(url_for("login"))

    # -----------------------------------------------------
    # MARKS
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT
            subjects.subject_name,
            marks.internal1,
            marks.internal2,
            marks.final_marks

        FROM marks

        JOIN subjects
            ON marks.subject_id = subjects.id

        WHERE marks.student_id = %s

        ORDER BY subjects.subject_name
        """,
        (student_id,)
    )

    marks = cursor.fetchall()

    # -----------------------------------------------------
    # ATTENDANCE
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT
            subjects.subject_name,
            attendance.total_classes,
            attendance.attended_classes

        FROM attendance

        JOIN subjects
            ON attendance.subject_id = subjects.id

        WHERE attendance.student_id = %s

        ORDER BY subjects.subject_name
        """,
        (student_id,)
    )

    attendance = cursor.fetchall()

    cursor.close()
    connection.close()

    # -----------------------------------------------------
    # AVERAGE MARKS
    # -----------------------------------------------------

    if marks:

        average_marks = sum(
            float(item["final_marks"] or 0)
            for item in marks
        ) / len(marks)

    else:

        average_marks = 0

    # -----------------------------------------------------
    # ATTENDANCE
    # -----------------------------------------------------

    total_classes = sum(
        int(item["total_classes"] or 0)
        for item in attendance
    )

    attended_classes = sum(
        int(item["attended_classes"] or 0)
        for item in attendance
    )

    absent_classes = total_classes - attended_classes

    if total_classes > 0:

        attendance_percentage = (
            attended_classes / total_classes
        ) * 100

    else:

        attendance_percentage = 0

    # -----------------------------------------------------
    # PERFORMANCE STATUS
    # -----------------------------------------------------

    if average_marks >= 75:

        status = "Excellent"

    elif average_marks >= 60:

        status = "Good"

    elif average_marks >= 40:

        status = "Average"

    else:

        status = "Needs Improvement"

    # -----------------------------------------------------
    # IMPROVEMENT SUBJECTS
    # -----------------------------------------------------

    improvement_subjects = [

        item["subject_name"]

        for item in marks

        if float(item["final_marks"] or 0) < 50

    ]

    return render_template(
        "student_dashboard.html",

        student=student,

        marks=marks,

        attendance=attendance,

        average_marks=round(
            average_marks,
            2
        ),

        attendance_percentage=round(
            attendance_percentage,
            2
        ),

        total_classes=total_classes,

        attended_classes=attended_classes,

        absent_classes=absent_classes,

        status=status,

        improvement_subjects=improvement_subjects
    )


# =========================================================
# STUDENT PERFORMANCE PAGE
# IMPORTANT:
# Endpoint name = student_performance_page
# =========================================================

# =========================================================
# STUDENT PERFORMANCE PAGE
# =========================================================

# =========================================================
# STUDENT PERFORMANCE PAGE
# =========================================================

@app.route("/student/performance")
@login_required
def student_performance_page():

    if session.get("role") != "student":
        return redirect(url_for("login"))

    student_id = session.get("user_id")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # STUDENT DETAILS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                course,
                semester
            FROM students
            WHERE id = %s
            """,
            (student_id,)
        )

        student = cursor.fetchone()

        if not student:
            return "Student not found", 404

        # -------------------------------------------------
        # MARKS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                subjects.subject_name,
                marks.internal1,
                marks.internal2,
                marks.final_marks

            FROM marks

            INNER JOIN subjects
                ON marks.subject_id = subjects.id

            WHERE marks.student_id = %s

            ORDER BY subjects.subject_name
            """,
            (student_id,)
        )

        marks = cursor.fetchall()

        # -------------------------------------------------
        # AVERAGE MARKS
        # -------------------------------------------------

        if marks:

            average_marks = round(
                sum(
                    float(mark["final_marks"] or 0)
                    for mark in marks
                ) / len(marks),
                2
            )

        else:

            average_marks = 0

        # -------------------------------------------------
        # PERFORMANCE STATUS
        # -------------------------------------------------

        if average_marks >= 75:
            status = "Excellent"

        elif average_marks >= 60:
            status = "Good"

        elif average_marks >= 40:
            status = "Average"

        else:
            status = "Needs Improvement"

        # -------------------------------------------------
        # CHART DATA
        # -------------------------------------------------

        chart_data = {

            "subjects": [
                mark["subject_name"]
                for mark in marks
            ],

            "internal1": [
                float(mark["internal1"] or 0)
                for mark in marks
            ],

            "internal2": [
                float(mark["internal2"] or 0)
                for mark in marks
            ],

            "final_marks": [
                float(mark["final_marks"] or 0)
                for mark in marks
            ]
        }

        return render_template(
            "student_performance_page.html",

            student=student,
            marks=marks,

            average_marks=average_marks,
            status=status,

            chart_data=chart_data
        )

    finally:

        cursor.close()
        connection.close()
# =========================================================
# STUDENT ATTENDANCE PAGE
# =========================================================

# =========================================================
# STUDENT ATTENDANCE PAGE
# =========================================================

@app.route("/student/attendance")
@login_required
def student_attendance():

    if session.get("role") != "student":
        return redirect(url_for("login"))

    student_id = session.get("user_id")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # STUDENT DETAILS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                course,
                semester
            FROM students
            WHERE id = %s
            """,
            (student_id,)
        )

        student = cursor.fetchone()

        if not student:
            return "Student not found", 404

        # -------------------------------------------------
        # ATTENDANCE
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                subjects.subject_name,
                attendance.total_classes,
                attendance.attended_classes

            FROM attendance

            INNER JOIN subjects
                ON attendance.subject_id = subjects.id

            WHERE attendance.student_id = %s

            ORDER BY subjects.subject_name
            """,
            (student_id,)
        )

        attendance = cursor.fetchall()

        # -------------------------------------------------
        # CALCULATE ATTENDANCE
        # -------------------------------------------------

        total_classes = sum(
            int(item["total_classes"] or 0)
            for item in attendance
        )

        attended_classes = sum(
            int(item["attended_classes"] or 0)
            for item in attendance
        )

        absent_classes = (
            total_classes - attended_classes
        )

        if total_classes > 0:

            attendance_percentage = round(
                (
                    attended_classes /
                    total_classes
                ) * 100,
                2
            )

        else:

            attendance_percentage = 0

        return render_template(
            "student_attendance.html",

            student=student,
            attendance=attendance,

            total_classes=total_classes,
            attended_classes=attended_classes,
            absent_classes=absent_classes,

            attendance_percentage=attendance_percentage
        )

    finally:

        cursor.close()
        connection.close()


# =========================================================
# STUDENT SUBJECTS PAGE
# =========================================================

@app.route("/student/subjects")
@student_required
def student_subjects():

    student_id = session["user_id"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT DISTINCT
            subjects.id,
            subjects.subject_name

        FROM subjects

        JOIN marks
            ON marks.subject_id = subjects.id

        WHERE marks.student_id = %s

        ORDER BY subjects.subject_name
        """,
        (student_id,)
    )

    subjects = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "student_subjects.html",
        subjects=subjects
    )


# =========================================================
# STUDENT PROFILE PAGE
# =========================================================

@app.route("/student/profile")
@student_required
def student_profile():

    student_id = session["user_id"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM students
        WHERE id = %s
        """,
        (student_id,)
    )

    student = cursor.fetchone()

    cursor.close()
    connection.close()

    if not student:

        return "Student not found", 404

    return render_template(
        "student_profile.html",
        student=student
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # -----------------------------------------------------
    # ALL STUDENTS
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT
            id,
            name,
            email,
            course,
            semester

        FROM students

        ORDER BY name
        """
    )

    students = cursor.fetchall()

    # -----------------------------------------------------
    # MARKS COUNT
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM marks
        """
    )

    marks_count = cursor.fetchone()["total"]

    # -----------------------------------------------------
    # CALCULATE STUDENT PERFORMANCE
    # -----------------------------------------------------

    for student in students:

        cursor.execute(
            """
            SELECT
                AVG(final_marks) AS average_marks

            FROM marks

            WHERE student_id = %s
            """,
            (student["id"],)
        )

        result = cursor.fetchone()

        if result and result["average_marks"] is not None:

            student["average_marks"] = round(
                float(result["average_marks"]),
                2
            )

        else:

            student["average_marks"] = None

        # -------------------------------------------------
        # ATTENDANCE
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                SUM(total_classes) AS total_classes,
                SUM(attended_classes) AS attended_classes

            FROM attendance

            WHERE student_id = %s
            """,
            (student["id"],)
        )

        attendance = cursor.fetchone()

        if (
            attendance
            and attendance["total_classes"]
            and attendance["total_classes"] > 0
        ):

            student["attendance_percentage"] = round(

                (
                    float(
                        attendance["attended_classes"] or 0
                    )
                    /
                    float(
                        attendance["total_classes"]
                    )
                ) * 100,

                2
            )

        else:

            student["attendance_percentage"] = None

    # -----------------------------------------------------
    # AVERAGE ATTENDANCE
    # -----------------------------------------------------

    attendance_values = [

        student["attendance_percentage"]

        for student in students

        if student["attendance_percentage"] is not None

    ]

    if attendance_values:

        average_attendance = round(

            sum(attendance_values)
            /
            len(attendance_values),

            2
        )

    else:

        average_attendance = 0

    # -----------------------------------------------------
    # STUDENTS NEEDING IMPROVEMENT
    # -----------------------------------------------------

    improvement_count = sum(

        1

        for student in students

        if (
            student["average_marks"] is not None
            and student["average_marks"] < 50
        )

    )

    cursor.close()
    connection.close()

    return render_template(

        "admin_dashboard.html",

        students=students,

        total_students=len(students),

        marks_count=marks_count,

        average_attendance=average_attendance,

        improvement_count=improvement_count
    )


# =========================================================
# ADMIN - ADD STUDENT
# =========================================================

@app.route("/admin/add-student", methods=["GET", "POST"])
@admin_required
def add_student():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        course = request.form.get("course", "").strip()
        semester = request.form.get("semester", "").strip()

        connection = get_db_connection()
        cursor = connection.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO students
                (
                    name,
                    email,
                    password,
                    course,
                    semester
                )

                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    name,
                    email,
                    password,
                    course,
                    semester
                )
            )

            connection.commit()

            flash(
                "Student added successfully!",
                "success"
            )

        except Exception as e:

            connection.rollback()

            print("ADD STUDENT ERROR:", e)

            flash(
                "Unable to add student.",
                "error"
            )

        finally:

            cursor.close()
            connection.close()

        return redirect(url_for("view_students"))

    return render_template("add_student.html")


# =========================================================
# ADMIN - VIEW STUDENTS
# =========================================================

@app.route("/admin/students")
@admin_required
def view_students():

    search = request.args.get(
        "search",
        ""
    ).strip()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if search:

        cursor.execute(
            """
            SELECT *
            FROM students

            WHERE name LIKE %s
            OR email LIKE %s

            ORDER BY name
            """,
            (
                "%" + search + "%",
                "%" + search + "%"
            )
        )

    else:

        cursor.execute(
            """
            SELECT *
            FROM students
            ORDER BY name
            """
        )

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "view_students.html",

        students=students,

        search=search
    )

  


# =========================================================
# ADMIN - INDIVIDUAL STUDENT PERFORMANCE
#
# IMPORTANT:
# Function name is student_performance
# so existing admin template links using
# url_for('student_performance', student_id=...)
# will work.
# =========================================================

# =========================================================
# ADMIN - INDIVIDUAL STUDENT PERFORMANCE
# =========================================================

@app.route("/admin/student/<int:student_id>")
@admin_required
def student_performance(student_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # 1. GET STUDENT DETAILS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                course,
                semester
            FROM students
            WHERE id = %s
            """,
            (student_id,)
        )

        student = cursor.fetchone()

        if not student:
            return redirect(url_for("view_students"))


        # -------------------------------------------------
        # 2. GET MARKS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                subjects.subject_name,
                marks.internal1,
                marks.internal2,
                marks.final_marks
            FROM marks

            JOIN subjects
                ON marks.subject_id = subjects.id

            WHERE marks.student_id = %s

            ORDER BY subjects.subject_name
            """,
            (student_id,)
        )

        marks = cursor.fetchall()


        # -------------------------------------------------
        # 3. GET ATTENDANCE
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                subjects.subject_name,
                attendance.total_classes,
                attendance.attended_classes
            FROM attendance

            JOIN subjects
                ON attendance.subject_id = subjects.id

            WHERE attendance.student_id = %s

            ORDER BY subjects.subject_name
            """,
            (student_id,)
        )

        attendance = cursor.fetchall()


        # -------------------------------------------------
        # 4. CALCULATE AVERAGE MARKS
        # -------------------------------------------------

        if marks:

            valid_marks = [
                float(item["final_marks"] or 0)
                for item in marks
            ]

            average_marks = round(
                sum(valid_marks) / len(valid_marks),
                2
            )

        else:

            average_marks = 0


        # -------------------------------------------------
        # 5. CALCULATE ATTENDANCE
        # -------------------------------------------------

        total_classes = sum(
            int(item["total_classes"] or 0)
            for item in attendance
        )

        attended_classes = sum(
            int(item["attended_classes"] or 0)
            for item in attendance
        )

        absent_classes = (
            total_classes - attended_classes
        )


        if total_classes > 0:

            attendance_percentage = round(
                (
                    attended_classes /
                    total_classes
                ) * 100,
                2
            )

        else:

            attendance_percentage = 0


        # -------------------------------------------------
        # 6. PERFORMANCE STATUS
        # -------------------------------------------------

        if average_marks >= 75:

            status = "Excellent"

        elif average_marks >= 60:

            status = "Good"

        elif average_marks >= 40:

            status = "Average"

        else:

            status = "Needs Improvement"


        # -------------------------------------------------
        # 7. SUBJECTS NEEDING IMPROVEMENT
        # -------------------------------------------------

        improvement_subjects = [
            item["subject_name"]
            for item in marks
            if float(item["final_marks"] or 0) < 50
        ]


        # -------------------------------------------------
        # 8. CREATE CHART DATA
        # -------------------------------------------------

        chart_data = {

            "subjects": [
                str(item["subject_name"] or "")
                for item in marks
            ],

            "internal1": [
                float(item["internal1"] or 0)
                for item in marks
            ],

            "internal2": [
                float(item["internal2"] or 0)
                for item in marks
            ],

            "final_marks": [
                float(item["final_marks"] or 0)
                for item in marks
            ]

        }


        # -------------------------------------------------
        # 9. SEND EVERYTHING TO TEMPLATE
        # -------------------------------------------------

        return render_template(
            "student_performance_page.html",

            student=student,

            marks=marks,

            attendance=attendance,

            average_marks=average_marks,

            attendance_percentage=attendance_percentage,

            total_classes=total_classes,

            attended_classes=attended_classes,

            absent_classes=absent_classes,

            status=status,

            improvement_subjects=improvement_subjects,

            chart_data=chart_data
        )


    except Exception as e:

        print("ADMIN STUDENT PERFORMANCE ERROR:", e)

        return "Error loading student performance. Check the terminal.", 500


    finally:

        cursor.close()
        connection.close()


# =========================================================
# ADMIN - ADD MARKS
# =========================================================

@app.route("/admin/add-marks", methods=["GET", "POST"])
@admin_required
def add_marks():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        student_id = request.form.get("student_id")
        subject_id = request.form.get("subject_id")
        internal1 = request.form.get("internal1")
        internal2 = request.form.get("internal2")
        final_marks = request.form.get("final_marks")

        try:

            # -------------------------------------------------
            # CHECK EXISTING RECORD
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT id
                FROM marks

                WHERE student_id = %s
                AND subject_id = %s
                """,
                (
                    student_id,
                    subject_id
                )
            )

            existing = cursor.fetchone()

            if existing:

                # UPDATE

                cursor.execute(
                    """
                    UPDATE marks

                    SET
                        internal1 = %s,
                        internal2 = %s,
                        final_marks = %s

                    WHERE student_id = %s
                    AND subject_id = %s
                    """,
                    (
                        internal1,
                        internal2,
                        final_marks,
                        student_id,
                        subject_id
                    )
                )

            else:

                # INSERT

                cursor.execute(
                    """
                    INSERT INTO marks
                    (
                        student_id,
                        subject_id,
                        internal1,
                        internal2,
                        final_marks
                    )

                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        student_id,
                        subject_id,
                        internal1,
                        internal2,
                        final_marks
                    )
                )

            connection.commit()

            flash(
                "Marks saved successfully!",
                "success"
            )

        except Exception as e:

            connection.rollback()

            print("ADD MARKS ERROR:", e)

            flash(
                "Unable to save marks.",
                "error"
            )

        finally:

            cursor.close()
            connection.close()

        return redirect(url_for("admin_dashboard"))

    # -----------------------------------------------------
    # STUDENTS
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT
            id,
            name

        FROM students

        ORDER BY name
        """
    )

    students = cursor.fetchall()

    # -----------------------------------------------------
    # SUBJECTS
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT
            id,
            subject_name

        FROM subjects

        ORDER BY subject_name
        """
    )

    subjects = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(

        "add_marks.html",

        students=students,

        subjects=subjects
    )


# =========================================================
# ADMIN - ADD ATTENDANCE
# =========================================================

@app.route("/admin/add-attendance", methods=["GET", "POST"])
@admin_required
def add_attendance():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        student_id = request.form.get("student_id")
        subject_id = request.form.get("subject_id")
        total_classes = request.form.get("total_classes")
        attended_classes = request.form.get("attended_classes")

        try:

            # -------------------------------------------------
            # CHECK EXISTING RECORD
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT id
                FROM attendance

                WHERE student_id = %s
                AND subject_id = %s
                """,
                (
                    student_id,
                    subject_id
                )
            )

            existing = cursor.fetchone()

            if existing:

                # UPDATE

                cursor.execute(
                    """
                    UPDATE attendance

                    SET
                        total_classes = %s,
                        attended_classes = %s

                    WHERE student_id = %s
                    AND subject_id = %s
                    """,
                    (
                        total_classes,
                        attended_classes,
                        student_id,
                        subject_id
                    )
                )

            else:

                # INSERT

                cursor.execute(
                    """
                    INSERT INTO attendance
                    (
                        student_id,
                        subject_id,
                        total_classes,
                        attended_classes
                    )

                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        student_id,
                        subject_id,
                        total_classes,
                        attended_classes
                    )
                )

            connection.commit()

            flash(
                "Attendance saved successfully!",
                "success"
            )

        except Exception as e:

            connection.rollback()

            print("ATTENDANCE ERROR:", e)

            flash(
                "Unable to save attendance.",
                "error"
            )

        finally:

            cursor.close()
            connection.close()

        return redirect(url_for("admin_dashboard"))

    # -----------------------------------------------------
    # STUDENTS
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT
            id,
            name

        FROM students

        ORDER BY name
        """
    )

    students = cursor.fetchall()

    # -----------------------------------------------------
    # SUBJECTS
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT
            id,
            subject_name

        FROM subjects

        ORDER BY subject_name
        """
    )

    subjects = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(

        "add_attendance.html",

        students=students,

        subjects=subjects
    )


# ---------------------------------------
# Delete Student
# ---------------------------------------

@app.route("/admin/delete-student/<int:student_id>", methods=["POST"])
@login_required
def delete_student(student_id):

    # Only admin can delete students
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        # Delete marks of the student
        cursor.execute(
            """
            DELETE FROM marks
            WHERE student_id = %s
            """,
            (student_id,)
        )

        # Delete attendance of the student
        cursor.execute(
            """
            DELETE FROM attendance
            WHERE student_id = %s
            """,
            (student_id,)
        )

        # Delete the student
        cursor.execute(
            """
            DELETE FROM students
            WHERE id = %s
            """,
            (student_id,)
        )

        connection.commit()

        flash(
            "Student deleted successfully.",
            "success"
        )

    except Exception as e:

        connection.rollback()

        print("Error deleting student:", e)

        flash(
            "Unable to delete student.",
            "error"
        )

    finally:

        cursor.close()
        connection.close()

    return redirect(url_for("admin_dashboard"))


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)