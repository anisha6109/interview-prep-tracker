from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Problem, Company, Application, Interview
import os
import csv
from io import StringIO
from datetime import datetime, date, timedelta
import PyPDF2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey_for_placement_tracker'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def update_streak(user):
    today = date.today()
    if user.last_login:
        if user.last_login == today - timedelta(days=1):
            user.streak += 1
        elif user.last_login < today - timedelta(days=1):
            user.streak = 1
    else:
        user.streak = 1
    user.last_login = today
    db.session.commit()

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('signup'))

        new_user = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))

        login_user(user, remember=remember)
        update_streak(user)
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    total_problems = Problem.query.filter_by(user_id=current_user.id).count()
    solved_problems = Problem.query.filter_by(user_id=current_user.id, status='Solved').count()
    total_applications = Application.query.filter_by(user_id=current_user.id).count()
    interviews_attended = Interview.query.filter_by(user_id=current_user.id).count()
    
    # Notifications/Reminders
    notifications = []
    if solved_problems == 0:
        notifications.append("You haven't solved any problems yet. Start practicing!")
    else:
        notifications.append(f"Great job! You've solved {solved_problems} problems.")

    # Gamification
    badges = []
    if solved_problems >= 10: badges.append("10 Problems Solved")
    if solved_problems >= 50: badges.append("50 Problems Solved")
    if current_user.streak >= 3: badges.append("3-Day Streak!")
    if current_user.streak >= 7: badges.append("1-Week Streak!!")

    # Heatmap setup
    all_solved = Problem.query.filter_by(user_id=current_user.id, status='Solved').all()
    activity_map = {}
    today = date.today()
    start_date = today - timedelta(days=364) # 52 weeks

    for prob in all_solved:
        prob_date = prob.date_solved.date()
        if prob_date >= start_date:
            d = prob_date.strftime('%Y-%m-%d')
            activity_map[d] = activity_map.get(d, 0) + 1

    heatmap_data = []
    for i in range(365):
        current_dt = start_date + timedelta(days=i)
        d_str = current_dt.strftime('%Y-%m-%d')
        heatmap_data.append({'date': d_str, 'count': activity_map.get(d_str, 0)})
    
    return render_template('dashboard.html', 
                           total_problems=total_problems,
                           solved_problems=solved_problems,
                           total_applications=total_applications,
                           interviews_attended=interviews_attended,
                           notifications=notifications,
                           badges=badges,
                           heatmap_data=heatmap_data)

@app.route('/dsa', methods=['GET', 'POST'])
@login_required
def dsa_tracker():
    if request.method == 'POST':
        title = request.form.get('title')
        platform = request.form.get('platform')
        difficulty = request.form.get('difficulty')
        topic = request.form.get('topic')
        status = request.form.get('status')
        
        new_prob = Problem(user_id=current_user.id, title=title, platform=platform, difficulty=difficulty, topic=topic, status=status)
        if status == 'Solved':
            current_user.points += 10 # gamification
        db.session.add(new_prob)
        db.session.commit()
        return redirect(url_for('dsa_tracker'))
        
    problems = Problem.query.filter_by(user_id=current_user.id).order_by(Problem.id.desc()).all()
    recommendations = ["Try solving an Array problem on LeetCode", "Review Dynamic Programming concepts"]
    
    return render_template('dsa_tracker.html', problems=problems, recommendations=recommendations)

@app.route('/dsa/delete/<int:id>')
@login_required
def delete_dsa(id):
    prob = Problem.query.get_or_404(id)
    if prob.user_id == current_user.id:
        db.session.delete(prob)
        db.session.commit()
    return redirect(url_for('dsa_tracker'))
    
@app.route('/dsa/update/<int:id>', methods=['POST'])
@login_required
def update_dsa(id):
    prob = Problem.query.get_or_404(id)
    if prob.user_id == current_user.id:
        prob.status = request.form.get('status')
        db.session.commit()
    return redirect(url_for('dsa_tracker'))

@app.route('/companies', methods=['GET', 'POST'])
@login_required
def companies():
    if request.method == 'POST':
        company_name = request.form.get('company_name')
        status = request.form.get('status')
        notes = request.form.get('notes')
        comp = Company(user_id=current_user.id, company_name=company_name, status=status, notes=notes)
        db.session.add(comp)
        db.session.commit()
        return redirect(url_for('companies'))
    
    comps = Company.query.filter_by(user_id=current_user.id).all()
    return render_template('companies.html', companies=comps)

@app.route('/companies/delete/<int:id>')
@login_required
def delete_company(id):
    comp = Company.query.get_or_404(id)
    if comp.user_id == current_user.id:
        db.session.delete(comp)
        db.session.commit()
    return redirect(url_for('companies'))

@app.route('/applications', methods=['GET', 'POST'])
@login_required
def applications():
    if request.method == 'POST':
        company = request.form.get('company')
        role = request.form.get('role')
        date_str = request.form.get('date')
        status = request.form.get('status')
        
        try:
            app_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format.")
            return redirect(url_for('applications'))

        new_app = Application(user_id=current_user.id, company=company, role=role, date=app_date, status=status)
        db.session.add(new_app)
        db.session.commit()
        return redirect(url_for('applications'))
        
    apps = Application.query.filter_by(user_id=current_user.id).all()
    return render_template('applications.html', applications=apps)

@app.route('/applications/delete/<int:id>')
@login_required
def delete_application(id):
    app = Application.query.get_or_404(id)
    if app.user_id == current_user.id:
        db.session.delete(app)
        db.session.commit()
    return redirect(url_for('applications'))

@app.route('/interviews', methods=['GET', 'POST'])
@login_required
def interviews():
    if request.method == 'POST':
        company = request.form.get('company')
        questions = request.form.get('questions')
        experience = request.form.get('experience')
        tips = request.form.get('tips')
        
        new_int = Interview(user_id=current_user.id, company=company, questions=questions, experience=experience, tips=tips)
        db.session.add(new_int)
        db.session.commit()
        return redirect(url_for('interviews'))
        
    ints = Interview.query.filter_by(user_id=current_user.id).all()
    return render_template('interviews.html', interviews=ints)

@app.route('/interviews/delete/<int:id>')
@login_required
def delete_interview(id):
    intv = Interview.query.get_or_404(id)
    if intv.user_id == current_user.id:
        db.session.delete(intv)
        db.session.commit()
    return redirect(url_for('interviews'))

@app.route('/api/chart-data')
@login_required
def chart_data():
    topics = db.session.query(Problem.topic, db.func.count(Problem.id)).filter_by(user_id=current_user.id).group_by(Problem.topic).all()
    topic_labels = [t[0] if t[0] else 'General' for t in topics]
    topic_data = [t[1] for t in topics]
    
    return jsonify({
        'topics': {'labels': topic_labels, 'data': topic_data}
    })

@app.route('/resume-analyzer', methods=['GET', 'POST'])
@login_required
def resume_analyzer():
    result = None
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['resume']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and file.filename.endswith('.pdf'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            text = ""
            try:
                with open(filepath, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted
            except Exception as e:
                flash(f"Error parsing PDF: {e}")
                
            text = text.lower()
            keywords = ['python', 'java', 'c++', 'react', 'node', 'sql', 'machine learning', 'aws', 'docker', 'flask', 'javascript', 'html', 'css', 'data structures', 'algorithms']
            found_keywords = [kw for kw in keywords if kw in text]
            
            result = {
                'extracted_skills': found_keywords,
                'suggestion': "Consider adding keywords matching your target job descriptions (e.g., specific framework names, tools)."
            }
            
    return render_template('resume.html', result=result)

@app.route('/export')
@login_required
def export():
    def generate():
        data = StringIO()
        writer = csv.writer(data)
        
        writer.writerow(('Type', 'Details', 'Status', 'Date/Info'))
        
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)
        
        for p in Problem.query.filter_by(user_id=current_user.id).all():
            writer.writerow(('Problem', p.title, p.status, p.difficulty))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)
            
        for a in Application.query.filter_by(user_id=current_user.id).all():
            writer.writerow(('Application', f"{a.company} - {a.role}", a.status, a.date))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)
            
    return app.response_class(generate(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=progress.csv'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
