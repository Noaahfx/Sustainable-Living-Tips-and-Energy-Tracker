import secrets

from _decimal import Decimal
from flask import Flask, render_template, redirect, url_for, request, flash, abort, session, get_flashed_messages
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
import uuid
import user
from forms import SignUpForm, LoginForm, AdminLoginForm, ChangePasswordForm, UpdateParticularsForm, EnergyQuizForm, \
    ElectricityEntryForm, EditElectricityEntryForm, EnquiryForm, CreateForumForm, CreateRewardForm, RedeemRewardForm, \
    CreateReviewsForm, UpdateProductForm, AddProductForm
from user import User
from datetime import datetime
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import shelve, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '123'

csrf = CSRFProtect(app)
####################################################(Karin(Start))####################################################
# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    # In a real application, you'd fetch the user from the database
    return User.load_from_shelve(user_id)

@app.route('/')
def firstpage():
    return redirect(url_for('login'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data

        user = User.load_from_shelve(username)

        if user and user.check_password(password):
            print("Login successful!")
            session['user_id'] = user.get_username()
            session['user_email'] = user.get_email()
            login_user(user)
            flash('Login successful!', 'success')
            print("Redirecting to login_success")
            return redirect(url_for('login_success'))
        else:
            print("Invalid credentials. Please try again.")
            flash('Invalid credentials. Please try again.', 'error')

    # If there are form validation errors, handle them here
    if form.errors:
        # You can check if the error is related to username and password mismatch
        if 'username' in form.errors and 'password' in form.errors:
            flash('Invalid username or password. Please try again.', 'error')
        else:
            # Handle other form validation errors as needed
            pass

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm(request.form)

    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Check if username already exists
        existing_user = User.load_from_shelve(username)
        if existing_user:
            flash('Username already taken. Choose a different one.', 'error')
            return redirect(url_for('signup'))

        # Check if email already in use
        existing_email_user = User.load_from_shelve_by_email(email)
        if existing_email_user:
            flash('Email already in use. Please choose a different one.', 'error')
            return redirect(url_for('signup'))

        # Password and username are valid, proceed with user creation
        new_user = User(username, email, password)
        User.save_to_shelve(new_user)

        # Log in the user
        login_user(new_user)

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('signup_success'))

    else:
        # Form validation failed
        print("Form validation errors:", form.errors)

    print("Rendering signup.html.")
    return render_template('signup.html', form=form)


@app.route('/login_success')
def login_success():
    if 'user_id' in session:
        username = session['user_id']
        return render_template('login_success.html', username=username)
    else:
        flash('You are not logged in. Please log in.', 'error')
        return redirect(url_for('login'))

@app.route('/signup_success', methods=['GET', 'POST'])
def signup_success():
    if current_user.is_authenticated:
        username = current_user.get_username()
        return render_template('signup_success.html', username=username)
    else:
        flash('You are not logged in. Please log in.', 'error')
        return redirect(url_for('login'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm(request.form)

    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data

        if username == 'admin' and password == '123':
            # Create a user object for the admin
            admin_user = User(username='admin', email='', password='123')  # You may need to provide a valid email for the admin

            # Log in the admin user
            login_user(admin_user, remember=True)

            # Set the is_admin flag in the session
            session['is_admin'] = True

            print("Redirecting to admin")
            return redirect(url_for('admin_home'))

    else:
        print("Form validation errors:", form.errors)

    print("Login function completed without redirecting to admin")  # Add this line
    return render_template('admin_login.html', form=form)

@app.route('/admin')
def admin():
    if 'is_admin' in session and session['is_admin']:
        users = User.get_all_users()
        return render_template('admin.html', users=users, current_user=current_user)  # Add current_user
    else:
        flash('You are not authorized to access this page.', 'error')
        return redirect(url_for('home'))

@app.route('/admin_home')
def admin_home():
    return render_template('admin_home.html')

@app.route('/delete_user_action/<username>', methods=['GET'])
def delete_user_action(username):
    if 'is_admin' in session and session['is_admin']:
        # Check if the logged-in user is an admin

        # Perform the user deletion logic
        if User.delete_user_from_shelve(username):
            flash(f'User {username} deleted successfully.', 'success')
        else:
            flash(f'User {username} not found.', 'error')

        users = User.get_all_users()  # Update the user list
        return render_template('admin.html', users=users)
    else:
        abort(403)  # If not an admin, return Forbidden status

@app.route('/account_settings')
def account_settings():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.load_from_shelve(user_id)  # Load the user from your storage (adjust the method accordingly)

        if user:
            user_name = user.get_name()
            user_age = user.get_age()
            user_street_name = user.get_street_name()
            user_unit_number = user.get_unit_number()
            user_country = user.get_country()

            return render_template('account_settings.html',
                                   user_name=user_name,
                                   user_age=user_age,
                                   user_street_name=user_street_name,
                                   user_unit_number=user_unit_number,
                                   user_country=user_country)

    # If the session doesn't contain 'user_id' or the user is not found, handle accordingly
    flash('User not found or not logged in', 'error')
    return redirect(url_for('login'))

@app.route('/view_personal_particulars')
def view_personal_particulars():
    print("Session:", session)

    if current_user.is_authenticated:
        user_email = current_user.get_email()
        user_username = current_user.get_username()
        user_name = current_user.get_name()
        user_age = current_user.get_age()
        user_street_name = current_user.get_street_name()
        user_unit_number = current_user.get_unit_number()
        user_country = current_user.get_country()

        print("User information:", user_email, user_name, user_age, user_street_name, user_unit_number, user_country)

        return render_template('view_personal_particulars.html',
                               user_email=user_email,
                               user_username=user_username,
                               user_name=user_name,
                               user_age=user_age,
                               user_street_name=user_street_name,
                               user_unit_number=user_unit_number,
                               user_country=user_country)

    flash('User not found or not logged in', 'error')
    return redirect(url_for('login'))


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data

        if new_password == confirm_password:
            # Update the user's password
            current_user.set_password(new_password)

            # Save the updated user object back to the admin database
            User.save_to_shelve(current_user)

            # Update the user's password in the admin view
            session['user_password'] = new_password  # Add this line

            flash('Password changed successfully!', 'success')
            return redirect(url_for('account_settings'))
        else:
            flash('Passwords must match', 'error')

    return render_template('change_password.html', form=form)

@app.route('/update_personal_particulars', methods=['GET', 'POST'])
def update_personal_particulars():
    form = UpdateParticularsForm(request.form)

    if request.method == 'POST' and form.validate():
        user_id = session.get('user_id')
        current_user = User.load_from_shelve(user_id)

        if current_user:
            # Update the user's particulars
            current_user.set_name(form.name.data)
            current_user.set_age(form.age.data)
            current_user.set_street_name(form.street_name.data)
            current_user.set_unit_number(form.unit_number.data)
            current_user.set_country(form.country.data)

            # Save the updated user object back to the storage
            User.save_to_shelve(current_user)

            # Update user information in the session
            session['user_name'] = current_user.get_name()
            session['user_age'] = current_user.get_age()
            session['user_street_name'] = current_user.get_street_name()
            session['user_unit_number'] = current_user.get_unit_number()
            session['user_country'] = current_user.get_country()

            flash('Personal particulars updated successfully!', 'success')
            return redirect(url_for('account_settings'))

    elif request.method == 'GET':
        user_id = session.get('user_id')

        if user_id:
            # Retrieve current user from the session
            current_user = User.load_from_shelve(user_id)

            # Pre-populate the form with current user's particulars
            form.name.data = current_user.get_name()
            form.age.data = current_user.get_age()
            form.street_name.data = current_user.get_street_name()
            form.unit_number.data = current_user.get_unit_number()
            form.country.data = current_user.get_country()
        else:
            flash('User not found or not logged in', 'error')
            return redirect(url_for('login'))

    return render_template('update_personal_particulars.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('user_name', None)  # Add other session variables if any
    cart_shelf = shelve.open('cart.db', writeback=True)
    cart_shelf.clear()
    cart_shelf.close()
    flash('Logout successful!', 'success')
    return redirect(url_for('login'))

questions = [
    {'id': 'question_1', 'question': 'How often do you turn off lights when leaving a room?',
     'options': ['Always', 'Sometimes', 'Rarely', 'Never']},

    {'id': 'question_2', 'question': 'What is your primary source of home heating?',
     'options': ['Gas', 'Electric', 'Oil', 'Other']},

    {'id': 'question_3', 'question': 'What is a good practice for conserving energy when doing laundry?',
     'options': ['Using a clothesline to air-dry clothes', 'Running the dryer for every small load', 'Washing clothes in hot water', 'Leaving the washing machine on standby mode']},

    {'id': 'question_4', 'question': 'What is a recommended way to reduce energy consumption in the kitchen?',
     'options': ['Using energy-efficient appliances', 'Leaving the refrigerator door open while deciding what to eat',
                 'Running the oven with the door open', 'Using the dishwasher for just a few dishes']},

    {'id': 'question_5', 'question': 'What is the most effective way to reduce standby power consumption in your home?',
     'options': ['Using smart power strips to cut off power to idle devices',
                 'Keeping electronics plugged in even when not in use', 'Running multiple electronic devices simultaneously',
                 'Using old, inefficient power strips']},

    {'id': 'question_6', 'question': 'How often do you turn off lights and electronic devices when leaving a room?',
     'options': ['Always', 'Sometimes', 'Rarely', 'Never']},

    {'id': 'question_7',
     'question': 'Do you unplug electronic devices when they are fully charged or not in use for an extended period?',
     'options': ['Always', 'Sometimes', 'Rarely', 'Never']},

]

sample_tips = {
    'question_1_Always': 'Great job! Conserving energy by turning off lights and unplugging devices helps reduce electricity consumption.',
    'question_1_Sometimes': 'You\'re on the right track, but there\'s room for improvement. Consider being more consistent in turning off lights and unplugging devices.',
    'question_1_Rarely': 'There is room for improvement. Try to develop the habit of turning off lights and unplugging devices when they are not in use.',
    'question_1_Never': 'Consider changing your habits to save energy. Turning off lights and unplugging devices can significantly reduce your electricity consumption.',

    'question_2_Gas': 'Gas heating is efficient, but make sure your system is well-maintained for optimal energy use.',
    'question_2_Electric': 'Electric heating can be costly. Consider using it sparingly and optimizing insulation.',
    'question_2_Oil': 'Oil heating can be efficient, but ensure your system is well-maintained to maximize energy efficiency.',
    'question_2_Other': 'Explore alternative heating sources for potential energy savings.',

    'question_3_Using a clothesline to air-dry clothes': 'Fantastic! Air-drying saves energy and helps preserve your clothes.',
    'question_3_Running the dryer for every small load': ' To save energy, wait until you have a full load before using the dryer.',
    'question_3_Washing clothes in hot water': 'Use cold water when possible to save energy and reduce utility costs.',
    'question_3_Leaving the washing machine on standby mode': 'Turn off appliances completely when not in use to save energy.',

    'question_4_Using energy-efficient appliances': 'Great choice! Energy-efficient appliances can significantly lower electricity usage.',
    'question_4_Leaving the refrigerator door open while deciding what to eat': 'Close the refrigerator door promptly to save energy and keep food cool.',
    'question_4_Running the oven with the door open': 'Keep the oven door closed to maintain temperature and save energy.',
    'question_4_Using the dishwasher for just a few dishes': 'Wait until you have a full load before running the dishwasher to maximize efficiency. Explore alternative heating sources for potential energy savings.',

    'question_5_Using smart power strips to cut off power to idle devices': 'Well done! Smart power strips are an effective solution for reducing standby power.',
    'question_5_Keeping electronics plugged in even when not in use': 'Unplug electronics to save energy, especially when not in use.',
    'question_5_Running multiple electronic devices simultaneously': 'Minimize simultaneous device usage to conserve energy. There is room for improvement. Consider recycling more frequently.',
    'question_5_Using old, inefficient power strips': 'Upgrade to energy-efficient power strips for better standby power management.',

    'question_6_Always': 'Great job! Consistently turning off lights and devices saves energy',
    'question_6_Sometimes': 'Remember to make it a habit to save energy by turning off lights and devices more consistently.',
    'question_6_Rarely': 'Consider being more mindful of energy consumption by turning off lights and devices more frequently.',
    'question_6_Never': 'Turning off lights and devices is essential for energy savings; try to adopt this habit consistently.',

    'question_7_Always': 'Excellent! Unplugging devices when not in use or fully charged helps save energy.',
    'question_7_Sometimes': 'Consider making it a habit to unplug devices more consistently for energy savings.',
    'question_7_Rarely': 'Unplugging devices when not in use is beneficial for energy efficiency; try doing it more often.',
    'question_7_Never': 'Unplugging devices is crucial for saving energy; aim to make it a regular practice.'
}

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    form = EnergyQuizForm()
    return render_template('quiz.html', form=form, questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    form = EnergyQuizForm()

    if form.is_submitted():
        selected_options = {
            key: request.form.get(key)
            for key in request.form.keys() if key.startswith('question_')
        }

        tips = {
            f'{key}_{selected_options[key]}': sample_tips.get(f'{key}_{selected_options[key]}', 'No tip available')
            for key in selected_options
        }

        # Calculate total score
        total_score = sum(get_score(key, selected_options[key]) for key in selected_options)

        return render_template('results.html', score=total_score, selected_options=selected_options, tips=tips)

    return "Form not submitted"

def get_score(question_id, selected_option):
    # Define a scoring mapping for each question
    score_mapping = {
        'question_1': {'Always': 4, 'Sometimes': 3, 'Rarely': 2, 'Never': 1},
        'question_2': {'Gas': 4, 'Electric': 3, 'Oil': 2, 'Other': 1},
        'question_3': {'Using a clothesline to air-dry clothes': 4, 'Running the dryer for every small load': 3,
                       'Washing clothes in hot water': 2, 'Leaving the washing machine on standby mode': 1},
        'question_4': {'Using energy-efficient appliances': 4,
                       'Leaving the refrigerator door open while deciding what to eat ': 3,
                       'Running the oven with the door open': 2,
                       'Using the dishwasher for just a few dishes': 1},
        'question_5': {'Using smart power strips to cut off power to idle devices': 4,
                       'Keeping electronics plugged in even when not in use': 3,
                       'Running multiple electronic devices simultaneously': 2,
                       'Using old, inefficient power strips': 1},
        'question_6': {'Always': 4, 'Sometimes': 3, 'Rarely': 2, 'Never': 1},
        'question_7': {'Always': 4, 'Sometimes': 3, 'Rarely': 2, 'Never': 1}
    }

    # Get the score for the selected option of the given question
    return score_mapping.get(question_id, {}).get(selected_option, 0)
####################################################(Karin(End))####################################################
####################################################(Noah(Start))###################################################
class ElectricityEntry:
    def __init__(self, username, year, month, usage):
        self.__username = username
        self.__year = year
        self.__month = month
        self.__usage = usage
        self.__update_date()

    def __update_date(self):
        self.__date = datetime.strptime(f'{self.__year} {self.__month}', '%Y %m')

    def get_date(self):
        return self.__date.strftime('%Y %B')

    def get_year(self):
        return self.__year

    def get_month(self):
        return self.__month

    def get_usage(self):
        return self.__usage

    def get_username(self):
        return self.__username

    def set_year(self, new_year):
        self.__year = new_year
        self.__update_date()

    def set_month(self, new_month):
        self.__month = new_month
        self.__update_date()

    def set_usage(self, new_usage):
        self.__usage = new_usage

    def update_usage(self, new_usage):
        self.__usage = new_usage
def save_electricity_entry(username, entry):
    entries = get_electricity_entries(username)
    entries.append(entry)
    save_electricity_entries(username, entries)


def get_electricity_entries(username):
    with shelve.open(f'electricity_entries_{username}.db', writeback=True) as db:
        entries_data = db.get('electricity_entries', [])

        entries = [
            ElectricityEntry(
                entry['_ElectricityEntry__username'],
                entry['_ElectricityEntry__year'],
                entry['_ElectricityEntry__month'],
                entry['_ElectricityEntry__usage']
            ) for entry in entries_data
        ]
        return entries

@app.route('/electricity_tracker', methods=['GET', 'POST'])
@login_required
def electricity_tracker():
    entry_form = ElectricityEntryForm()
    edit_form = EditElectricityEntryForm()

    if request.method == 'POST':
        if entry_form.validate_on_submit():
            year = int(entry_form.year.data)
            month = int(entry_form.month.data)
            usage = int(entry_form.usage.data)

            entry = ElectricityEntry(username=current_user.get_username(), year=year, month=month, usage=usage)

            # Check for duplicate entry before saving
            entries = get_electricity_entries(current_user.get_username())
            if not any(e.get_year() == entry.get_year() and e.get_month() == entry.get_month() for e in entries):
                save_electricity_entry(current_user.get_username(), entry)
                flash('Electricity entry added successfully!', 'success')
            else:
                flash('Duplicate entry! Entry not saved.', 'danger')

            # Redirect to the same page to reinitialize the form
            return redirect(url_for('electricity_tracker'))

    entries = get_electricity_entries(current_user.get_username())

    # Retrieve flash messages
    flash_messages = get_flashed_messages(with_categories=True)

    return render_template('electricity_tracker.html', entries=entries, entry_form=entry_form, edit_form=edit_form, flash_messages=flash_messages)

@app.route('/delete_electricity_entry/<int:index>', methods=['POST'])
@login_required
def delete_electricity_entry(index):
    entries = get_electricity_entries(current_user.get_username())

    if 0 <= index < len(entries):
        del entries[index]
        save_electricity_entries(current_user.get_username(), entries)
        flash('Electricity entry deleted successfully!', 'success')
    else:
        flash('Invalid index for deletion.', 'danger')

    return redirect(url_for('electricity_tracker'))

def save_electricity_entries(username, entries):
    with shelve.open(f'electricity_entries_{username}.db', writeback=True) as db:
        db['electricity_entries'] = [vars(entry) for entry in entries]


@app.route('/view_electricity_graph')
@login_required
def view_electricity_graph():
    entries = get_electricity_entries(current_user.get_username())

    # Sort entries in ascending order based on date
    entries.sort(key=lambda x: datetime.strptime(x.get_date(), '%Y %B'))

    # Extract dates and usages for the graph
    dates = [entry.get_date() for entry in entries]
    usages = [entry.get_usage() for entry in entries]

    # Create a line graph using Plotly
    fig = make_subplots(rows=1, cols=1, subplot_titles=['Energy Consumption Tracker'])

    fig.add_trace(
        go.Scatter(x=dates, y=usages, mode='lines+markers', line=dict(color='#6F8FAF'), marker=dict(size=10)),
        row=1, col=1
    )

    fig.update_layout(
        title_text='Energy Consumption Tracker',
        xaxis_title='Date',
        yaxis_title='Energy Usage (kWh)',
    )

    # Convert the Plotly figure to an HTML string
    graph_html = fig.to_html(full_html=False)

    return render_template('electricity_graph.html', graph_html=graph_html)


@app.route('/edit_electricity_entry/<int:index>', methods=['GET', 'POST'])
@login_required
def edit_electricity_entry(index):
    entries = get_electricity_entries(current_user.get_username())

    if 0 <= index < len(entries):
        entry = entries[index]

        # Create the form and populate it with the entry data
        edit_form = EditElectricityEntryForm(request.form, obj=entry)

        if request.method == 'POST' and edit_form.validate():
            # Update the entry with the new data
            new_usage = edit_form.edit_usage.data
            entry.update_usage(new_usage)

            new_year = int(edit_form.edit_year.data)
            new_month = int(edit_form.edit_month.data)

            # Check for duplicate entry before saving
            if not any(e.get_year() == new_year and e.get_month() == new_month and e != entry for e in entries):
                entry.set_year(new_year)
                entry.set_month(new_month)
                save_electricity_entries(current_user.get_username(), entries)
                flash('Electricity entry edited successfully!', 'success')
            else:
                flash('Duplicate entry! Entry not saved.', 'danger')

            # Redirect to electricity tracker after editing
            return redirect(url_for('electricity_tracker'))

            # Render the form on the 'GET' request
        return render_template('edit_electricity_entry.html', edit_form=edit_form)
    else:
        flash('Invalid index for editing.', 'danger')

    return redirect(url_for('electricity_tracker'))

#Enquiry#
class Enquiry:
    def __init__(self, username, name, email, subject, message):
        self.__username = username
        self.__name = name
        self.__email = email
        self.__subject = subject
        self.__message = message
        self.__timestamp = datetime.now()

    def get_name(self):
        return self.__name

    def get_email(self):
        return self.__email

    def get_subject(self):
        return self.__subject

    def get_message(self):
        return self.__message

    def get_timestamp(self):
        return self.__timestamp
    def get_username(self):
        return self.__username

    def set_name(self, name):
        self.__name = name

    def set_email(self, email):
        self.__email = email

    def set_subject(self, subject):
        self.__subject = subject

    def set_message(self, message):
        self.__message = message

    def save(self):
        with shelve.open('enquiries.db', writeback=True) as db:
            if 'enquiries' not in db:
                db['enquiries'] = []
            db['enquiries'].append(self)

def get_enquiries():
    with shelve.open('enquiries.db', writeback=True) as db:
        entries = db.get('enquiries', [])
        return [entry if isinstance(entry, Enquiry) else Enquiry(**entry) for entry in entries]

def save_enquiries(enquiries):
    with shelve.open('enquiries.db', writeback=True) as db:
        db['enquiries'] = enquiries

@app.route('/submit_enquiry', methods=['GET', 'POST'])
def submit_enquiry():
    form = EnquiryForm()
    if form.validate_on_submit():
        enquiry = Enquiry(
            username=current_user.get_username(),
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data
        )
        enquiry.save()
        flash('Enquiry submitted successfully!', 'success')
        # Redirect to the submission received page
        return redirect(url_for('submission_received', name=form.name.data))
    return render_template('submit_enquiry.html', form=form)


@app.route('/view_enquiries', methods=['GET', 'POST'])
def view_enquiries():
    form = EnquiryForm()  # Create an instance of EnquiryForm
    if request.method == 'POST':
        index = int(request.form.get('index', -1))
        if index != -1:
            enquiries = get_enquiries()
            if 0 <= index < len(enquiries):
                del enquiries[index]
                save_enquiries(enquiries)
                flash('Enquiry deleted successfully!', 'success')

    enquiries = get_enquiries()
    return render_template('view_enquiries.html', enquiries=enquiries, form=form)


# Route for deleting an enquiry
@app.route('/delete_enquiry/<int:index>', methods=['POST'])
def delete_enquiry(index):
    enquiries = get_enquiries()

    if 0 <= index < len(enquiries):
        del enquiries[index]
        save_enquiries(enquiries)
        flash('Enquiry deleted successfully!', 'success')

    return redirect(url_for('view_enquiries'))


@app.route('/submission_received/<name>')
def submission_received(name):
    # Retrieve the last submitted enquiry for the provided name
    enquiries = get_enquiries()
    enquiry = next((e for e in reversed(enquiries) if e.get_name() == name), None)

    if not enquiry:
        flash('Enquiry not found!', 'danger')
        return redirect(url_for('home'))

    return render_template('submission_received.html', enquiry=enquiry)

####################################################(Noah(End)))####################################################
####################################################(Keith(Start)))####################################################
app.config['UPLOAD_FOLDER'] = 'static/imageuploads'
class Forum:
    count_id = 0

    def __init__(self, username, title, content, image):
        Forum.count_id += 1
        self.__forum_id = Forum.count_id
        self.__username = username
        self.__title = title
        self.__content = content
        self.__image = image

    def set_forum_id(self, forum_id):
        self.__forum_id = forum_id

    def set_title(self, title):
        self.__title = title

    def set_content(self, content):
        self.__content = content

    def set_image(self, image):
        self.__image = image

    def get_forum_id(self):
        return self.__forum_id

    def get_title(self):
        return self.__title

    def get_content(self):
        return self.__content

    def get_image(self):
        return self.__image

    def set_username(self, username):
        self.__username = username

    def get_username(self):
        return self.__username


@app.route('/createforum', methods=['GET', 'POST'])
@login_required
def create_forum():
    create_forums_form = CreateForumForm(request.form)

    if request.method == 'POST' and create_forums_form.validate():
        db = shelve.open('forum.db', 'c')

        try:
            forum_dict = db.get('forums', {})
            count_id = db.get('count_id', 0)
        except:
            print("Error in retrieving forums from forum.db.")

        image_1 = request.files.get('image')
        filename = None  # Default filename to None if no image is provided

        if image_1 and image_1.filename != '':
            filename = secure_filename(image_1.filename)
            image_1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_forum = Forum(current_user.get_username(), create_forums_form.title.data, create_forums_form.content.data, filename)
        new_forum.set_forum_id(count_id + 1)  # Use the stored count_id
        forum_dict[new_forum.get_forum_id()] = new_forum

        # Update the count_id and forums in the database
        db['count_id'] = count_id + 1
        db['forums'] = forum_dict

        db.close()

        return redirect(url_for('forum_submitted',
                                title=new_forum.get_title(),
                                content=new_forum.get_content(),
                                image=new_forum.get_image()))
    return render_template('createforum.html', form=create_forums_form)



@app.route('/forum_submitted')
def forum_submitted():
    # Retrieve the forum details from the query parameters
    title = request.args.get('title')
    content = request.args.get('content')
    image = request.args.get('image')

    # Pass the forum details to the template
    return render_template('forum_submitted.html', title=title, content=content, image=image)


@app.route('/retrieveforum', methods=['GET', 'POST'])
def retrieve_forum():
    forum_dict = {}
    db = shelve.open('forum.db', 'r')
    forum_dict = db.get('forums', {})
    db.close()

    forum_list = []
    for key in forum_dict:
        current_forum = forum_dict.get(key)
        forum_list.append((current_forum, current_forum.get_username()))


    # Pass the current user's username to the template
    return render_template('retrieveforum.html', count=len(forum_list), forum_list=forum_list, current_username=current_user.get_username())




@app.route('/editforum/<int:id>/', methods=['GET', 'POST'])
@login_required
def update_forum(id):
    update_forum_form = CreateForumForm(request.form)
    forum_dict = {}

    if request.method == 'POST' and update_forum_form.validate():
        db = shelve.open('forum.db', 'w')
        forum_dict = db.get('forums', {})

        image_1 = request.files['image']
        if image_1.filename != '':
            filename = secure_filename(image_1.filename)
            image_1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = None

        current_forum = forum_dict.get(id)

        if current_user.get_username() == current_forum.get_username():
            current_forum.set_title(update_forum_form.title.data)
            current_forum.set_content(update_forum_form.content.data)
            current_forum.set_image(filename)

            db['forums'] = forum_dict
            db.close()

            return redirect('/retrieveforum')

    else:
        db = shelve.open('forum.db', 'r')
        forum_dict = db.get('forums', {})
        db.close()

        current_forum = forum_dict.get(id)

        if current_user.get_username() == current_forum.get_username():
            update_forum_form.title.data = current_forum.get_title()
            update_forum_form.content.data = current_forum.get_content()

            return render_template('editforum.html', form=update_forum_form, forum=current_forum)

    flash("You don't have permission to edit this post.", 'error')
    return redirect('/retrieveforum')

@app.route('/deleteforum/<int:id>/', methods=['POST'])
@login_required
def delete_forum(id):
    forum_dict = {}
    db = shelve.open('forum.db', 'w')
    forum_dict = db.get('forums', {})

    if id in forum_dict:
        current_forum = forum_dict[id]

        if current_user.get_username() == current_forum.get_username():
            del forum_dict[id]

            db['forums'] = forum_dict
            db.close()

            return redirect('/retrieveforum')

    flash("You don't have permission to delete this post.", 'error')
    return redirect('/retrieveforum')

@app.route('/admin/manage_forum')
def admin_manage_forum():
    if 'is_admin' in session and session['is_admin']:
        # Fetch and display the list of forums (you can modify this based on your implementation)
        forum_dict = {}
        db = shelve.open('forum.db', 'r')
        forum_dict = db.get('forums', {})
        db.close()

        forum_list = []
        for key in forum_dict:
            current_forum = forum_dict.get(key)
            forum_list.append((current_forum, current_forum.get_username()))

        return render_template('admin_manage_forum.html', count=len(forum_list), forum_list=forum_list)

    else:
        flash('You are not authorized to access this page.', 'error')
        return redirect(url_for('home'))

@app.route('/admindeleteforum/<int:id>/', methods=['POST'])
def admin_delete_forum(id):
    forum_dict = {}
    db = shelve.open('forum.db', 'w')
    forum_dict = db.get('forums', {})

    if id in forum_dict:
        current_forum = forum_dict[id]

        del forum_dict[id]

        db['forums'] = forum_dict
        db.close()

        return redirect('/admin/manage_forum')

    flash("You don't have permission to delete this post.", 'error')
    return redirect('/admin/manage_forum')

class Reviews:
    count_id = 0

    def __init__(self, username, title, content, image, rating):
        Reviews.count_id += 1
        self.__reviews_id = Reviews.count_id
        self.__username = username
        self.__title = title
        self.__content = content
        self.__image = image
        self.__rating = rating
    def set_reviews_id(self, reviews_id):
        self.__reviews_id = reviews_id

    def set_title(self, title):
        self.__title = title

    def set_content(self, content):
        self.__content = content

    def set_image(self, image):
        self.__image = image

    def set_rating(self, rating):
        self.__rating = rating
    def get_reviews_id(self):
        return self.__reviews_id

    def get_title(self):
        return self.__title

    def get_content(self):
        return self.__content

    def get_image(self):
        return self.__image

    def set_username(self, username):
        self.__username = username

    def get_username(self):
        return self.__username

    def get_rating(self):
        return self.__rating

@app.route('/createreviews', methods=['GET', 'POST'])
@login_required
def create_reviews():
    create_reviews_form = CreateReviewsForm(request.form)

    if request.method == 'POST' and create_reviews_form.validate():
        db = shelve.open('review.db', 'c')

        try:
            reviews_dict = db.get('reviews', {})
            count_id = db.get('count_id', 0)
        except:
            print("Error in retrieving reviews from review.db.")

        image = request.files.get('image')
        filename = None  # Default filename to None if no image is provided

        if image and image.filename != '':
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_review = Reviews(current_user.get_username(), create_reviews_form.title.data, create_reviews_form.content.data, filename, create_reviews_form.rating.data)
        new_review.set_reviews_id(count_id + 1)  # Use the stored count_id
        reviews_dict[new_review.get_reviews_id()] = new_review

        # Update the count_id and reviews in the database
        db['count_id'] = count_id + 1
        db['reviews'] = reviews_dict

        db.close()

        return redirect(url_for('review_submitted',
                                title=new_review.get_title(),
                                content=new_review.get_content(),
                                image=new_review.get_image(),
                                rating=new_review.get_rating()))
    return render_template('createreviews.html', form=create_reviews_form)

@app.route('/review_submitted')
def review_submitted():
    # Retrieve the review details from the query parameters
    title = request.args.get('title')
    content = request.args.get('content')
    image = request.args.get('image')
    rating = request.args.get('rating')

    # Pass the review details to the template
    return render_template('reviews_submitted.html', title=title, content=content, image=image, rating=rating)

@app.route('/retrievereviews', methods=['GET', 'POST'])
def retrieve_reviews():
    reviews_dict = {}
    db = shelve.open('review.db', 'r')
    reviews_dict = db.get('reviews', {})
    db.close()

    reviews_list = []
    for key in reviews_dict:
        current_review = reviews_dict.get(key)
        reviews_list.append((current_review, current_review.get_username()))

    # Pass the current user's username to the template
    return render_template('retrievereviews.html', count=len(reviews_list), reviews_list=reviews_list, current_username=current_user.get_username())

@app.route('/editreview/<int:id>/', methods=['GET', 'POST'])
@login_required
def update_reviews(id):
    update_reviews_form = CreateReviewsForm(request.form)
    reviews_dict = {}

    if request.method == 'POST' and update_reviews_form.validate():
        db = shelve.open('review.db', 'w')
        reviews_dict = db.get('reviews', {})

        image = request.files['image']
        if image.filename != '':
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = None

        current_review = reviews_dict.get(id)

        if current_user.get_username() == current_review.get_username():
            current_review.set_title(update_reviews_form.title.data)
            current_review.set_content(update_reviews_form.content.data)
            current_review.set_image(filename)
            current_review.set_rating(update_reviews_form.rating.data)  # Update the rating

            db['reviews'] = reviews_dict
            db.close()

            return redirect('/retrievereviews')

    else:
        db = shelve.open('review.db', 'r')
        reviews_dict = db.get('reviews', {})
        db.close()

        current_review = reviews_dict.get(id)

        if current_user.get_username() == current_review.get_username():
            update_reviews_form.title.data = current_review.get_title()
            update_reviews_form.content.data = current_review.get_content()
            update_reviews_form.rating.data = str(current_review.get_rating())

            return render_template('editreviews.html', form=update_reviews_form, review=current_review)

    flash("You don't have permission to edit this review.", 'error')
    return redirect('/retrievereviews')

@app.route('/deletereview/<int:id>/', methods=['POST'])
@login_required
def delete_reviews(id):
    reviews_dict = {}
    db = shelve.open('review.db', 'w')
    reviews_dict = db.get('reviews', {})

    if id in reviews_dict:
        current_review = reviews_dict[id]

        if current_user.get_username() == current_review.get_username():
            del reviews_dict[id]

            db['reviews'] = reviews_dict
            db.close()

            return redirect('/retrievereviews')

    flash("You don't have permission to delete this review.", 'error')
    return redirect('/retrievereviews')

@app.route('/admin/manage_reviews')
def admin_manage_reviews():
    if 'is_admin' in session and session['is_admin']:
        reviews_dict = {}
        db = shelve.open('review.db', 'r')
        reviews_dict = db.get('reviews', {})
        db.close()

        reviews_list = []
        for key in reviews_dict:
            current_review = reviews_dict.get(key)
            reviews_list.append((current_review, current_review.get_username()))
        print("Reviews List:", reviews_list)

        return render_template('admin_manage_reviews.html', count=len(reviews_list), reviews_list=reviews_list)
    else:
        flash('You are not authorized to access this page.', 'error')
        return redirect(url_for('home'))

@app.route('/admindeletereview/<int:id>/', methods=['POST'])
def admin_delete_reviews(id):
    reviews_dict = {}
    db = shelve.open('review.db', 'w')
    reviews_dict = db.get('reviews', {})

    if id in reviews_dict:
        del reviews_dict[id]
        db['reviews'] = reviews_dict
        db.close()
        return redirect('/admin/manage_reviews')

    flash("You don't have permission to delete this review.", 'error')
    return redirect('/admin/manage_reviews')
#########################(keith(end))#######################################

#########################(James)(Start)######################################
@app.route('/edit_points/<username>', methods=['POST'])
def edit_points(username):
    print("Reached edit_points route")  # Add this line for debugging

    # Retrieve the user from the database or wherever you store user data
    user = User.load_from_shelve(username)

    if user:
        # Get the new points value from the form
        new_points_str = request.form.get('new_points')

        try:
            # Convert the new_points value to an integer
            new_points = int(new_points_str)

            # Perform any necessary validation on the new_points value
            if new_points < 0:
                flash('Points cannot be negative.', 'error')
                return redirect(url_for('admin'))

            # Update the user's points
            user.set_points(new_points)
            User.save_to_shelve(user)

            # Print some debug information
            print(f'Points for {username} updated successfully.')

            # Redirect to the admin page or wherever you want to go after editing points
            flash(f'Points for {username} updated successfully.', 'success')
            return redirect(url_for('admin'))

        except ValueError:
            # Handle the case where the new_points value is not a valid integer
            flash('Please enter a valid integer for points.', 'error')
            return redirect(url_for('admin'))
    else:
        flash(f'User {username} not found.', 'error')
        return redirect(url_for('admin'))


class Reward:
    count_id = 0

    def __init__(self, name, points, desc):
        self.__id = str(uuid.uuid4())
        self.__name = name
        self.__points = points
        self.__desc = desc

    def set_id(self, reward_id):
        self.__id = reward_id

    def set_name(self, name):
        self.__name = name

    def set_points(self, points):
        self.__points = points

    def set_description(self, desc):
        self.__desc = desc

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def get_points(self):
        return self.__points

    def get_description(self):
        return self.__desc

    @classmethod
    def load_from_shelve(cls, reward_id):
        with shelve.open('reward.db', 'r') as db:
            rewards_dict = db.get('Rewards', {})
            return rewards_dict.get(reward_id)


@app.route('/retrieverewards')
def retrieve_rewards():
    rewards_dict = {}
    db = shelve.open('reward.db', 'r')
    rewards_dict = db['Rewards']
    db.close()

    rewards_list = []
    for key in rewards_dict:
        reward = rewards_dict.get(key)
        rewards_list.append(reward)

    return render_template('retrieverewards.html', count=len(rewards_list), rewards_list=rewards_list)
# Add this route to your Flask application

@app.route('/create_reward', methods=['GET', 'POST'])
def create_reward():
    create_reward_form = CreateRewardForm(request.form)

    if request.method == 'POST' and create_reward_form.validate():
        new_reward = Reward(
            name=create_reward_form.name.data,
            points=create_reward_form.points.data,
            desc=create_reward_form.description.data
        )

        # Use 'c' (create) flag to create a new db if it doesn't exist
        with shelve.open('reward.db', 'c') as db:
            rewards_dict = db.get('Rewards', {})
            rewards_dict[new_reward.get_id()] = new_reward
            db['Rewards'] = rewards_dict

        return redirect(url_for('retrieve_rewards'))

    return render_template('createreward.html', form=create_reward_form)


@app.route('/dropdown_rewards')
def dropdown_rewards():
    rewards_list = []  # Initialize an empty list to store rewards
    with shelve.open('reward.db', 'r') as db:
        rewards_dict = db.get('Rewards', {})
        for key, reward in rewards_dict.items():
            rewards_list.append(reward)

    redeem_form = RedeemRewardForm()

    return render_template('dropdown_rewards.html', rewards_list=rewards_list, redeem_form=redeem_form)

@app.route('/editreward/<id>/', methods=['GET', 'POST'])
def update_reward(id):
    update_reward_form = CreateRewardForm(request.form)

    if request.method == 'POST' and update_reward_form.validate():
        rewards_dict = {}
        db = shelve.open('reward.db', 'w')
        rewards_dict = db['Rewards']

        reward = rewards_dict.get(id)
        reward.set_name(update_reward_form.name.data)
        reward.set_points(update_reward_form.points.data)
        reward.set_description(update_reward_form.description.data)  # Set the description

        db['Rewards'] = rewards_dict
        db.close()

        return redirect(url_for('retrieve_rewards'))
    else:
        rewards_dict = {}
        db = shelve.open('reward.db', 'r')
        rewards_dict = db['Rewards']
        db.close()

        reward = rewards_dict.get(id)
        update_reward_form.name.data = reward.get_name()
        update_reward_form.points.data = reward.get_points()
        update_reward_form.description.data = reward.get_description()  # Populate the description field

        # Pass the id to the template
        return render_template('editreward.html', form=update_reward_form, reward_id=id)



@app.route('/delete_reward/<id>/', methods=['GET', 'POST'])
def delete_reward(id):
    rewards_dict = {}
    db = shelve.open('reward.db', 'w')

    if 'Rewards' in db:
        rewards_dict = db['Rewards']
        if id in rewards_dict:
            del rewards_dict[id]
            db['Rewards'] = rewards_dict

    db.close()

    return redirect('/retrieverewards')

@app.route('/redeem_reward/<reward_id>', methods=['POST'])
@login_required  # Ensure the user is logged in
def redeem_reward(reward_id):
    # Get the reward from the shelve
    reward = Reward.load_from_shelve(reward_id)

    if reward is None:
        flash('Reward not found.', 'error')
    else:
        # Check if the user has enough points to redeem the reward
        if current_user.get_points() >= reward.get_points():
            # Deduct points from the user's balance
            current_user_points = current_user.get_points() - reward.get_points()
            current_user.set_points(current_user_points)
            User.save_to_shelve(current_user)  # Save the updated user points to the database

            # Record the redeemed reward in the user's list
            if current_user.redeem_reward(reward):
                flash(f'Reward "{reward.get_name()}" redeemed successfully!', 'success')
            else:
                # If redeem_reward returns False, refund the deducted points
                current_user.set_points(current_user.get_points() + reward.get_points())
                User.save_to_shelve(current_user)  # Save the refunded points to the database
                flash('Failed to redeem the reward. Please try again.', 'error')
        else:
            flash('Insufficient points to redeem this reward.', 'error')

    return redirect(url_for('dropdown_rewards'))



@app.route('/redeemed_rewards')
def redeemed_rewards():
    # Retrieve the redeemed rewards for the current user (adjust accordingly)
    redeemed_rewards = current_user.get_redeemed_rewards()

    # Create an instance of the form you want to use in the template
    redeem_form = RedeemRewardForm()

    # Render the 'redeemed_rewards.html' template with the redeemed rewards and form
    return render_template('redeemed_rewards.html', redeemed_rewards=redeemed_rewards, form=redeem_form)


@app.route('/delete_redeemed_reward/<reward_id>', methods=['POST'])
@login_required  # Ensure the user is logged in
def delete_redeemed_reward(reward_id):
    print(f"Deleting redeemed reward with ID: {reward_id}")

    # Ensure the user is the correct type (User) before calling delete_redeemed_reward
    if isinstance(current_user, User):
        # Attempt to delete the redeemed reward
        if current_user.delete_redeemed_reward(reward_id):
            # Save the updated user information to the shelve
            User.save_to_shelve(current_user)
            flash('Redeemed reward deleted successfully!', 'success')
        else:
            flash('Redeemed reward not found or could not be deleted.', 'error')
    else:
        flash('Invalid user type.', 'error')

    return redirect(url_for('redeemed_rewards'))
#################(james(end))######################################
#################(darel(start))####################################
product_counter = 0


# Define where uploaded images will be stored
 # Allowed image types
app.config['ALLOWED_EXTENSIONS'] = ['png', 'jpg', 'jpeg']
# app.secret_key = secrets.token_hex(16)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

class Product:
    def __init__(self ,product_id, name, description, energy_saving_rating, image_filename=None, quantity=0, price=0.0):
        self.product_id = product_id  # Unique identifier for the product

        self.name = name
        self.description = description
        self.energy_saving_rating = energy_saving_rating
        self.quantity = quantity
        self.price = price
        self.image_filename = image_filename





sum_has_run = False

@app.route('/manage_products')
def admin_product_list():
    if 'is_admin' in session and session['is_admin']:
    # Read products from the shelf
        shelf = shelve.open('products.db')

        products = list(shelf.values())

        shelf.close()
        # product_list = []
        # for product in products:
        #     # Check if the user is logged in
        #     if current_user.is_authenticated:
        #         # Append each product along with the current user's username
        #         product_list.append((product, current_user.get_username()))
        #     else:
        #         # If user is anonymous, append None as username
        #         product_list.append((product, None))
        return render_template('manage_products.html', products=products, count=len(products))
    else:
        flash('You are not authorized to access this page.', 'error')
        return redirect(url_for('home'))

@app.route('/product_list', methods=['GET', 'POST'])
@login_required
def product_list():

    # Read products from the shelf
    shelf = shelve.open('products.db')

    products = list(shelf.values())

    shelf.close()
    # product_list = []
    # for product in products:
    #     # Append each product along with the current user's username
    #     product_list.append((product, current_user.get_username()))

    return render_template('product_list.html', products=products )

def get_highest_product_id():
    shelf = shelve.open('products.db')
    product_ids = [int(key) for key in shelf.keys()]
    shelf.close()
    if product_ids:
        return max(product_ids)
    else:
        return 0
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        product_id = get_highest_product_id() + 1  # Get the next available product ID

        name = form.name.data
        description = form.description.data
        energy_saving_rating = form.energy_saving_rating.data
        quantity = form.quantity.data
        price = form.price.data
        image = form.image.data

        if image:
            if not allowed_file(image.filename):
                flash('File extension not allowed. Allowed extensions are: png, jpg, jpeg', 'error')
                return redirect(url_for('add_product'))

            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename
        else:
            image_filename = None

        new_product = Product(product_id , name, description, energy_saving_rating, image_filename, quantity, price)

        with shelve.open('products.db', writeback=True) as products:
            products[str(product_id)] = new_product

        flash('Product added successfully!', 'success')
        return redirect(url_for('admin_product_list'))

    return render_template('add_product.html', form=form )

@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    with shelve.open('products.db', writeback=True) as products:
        product = products.get(str(product_id))
        if not product:
            flash("Product not found!", "error")
            return redirect(url_for('product_list'))

        form = UpdateProductForm(obj=product)

        if form.validate_on_submit():
            product.name = form.name.data
            product.description = form.description.data
            product.energy_saving_rating = form.energy_saving_rating.data
            product.quantity = form.quantity.data
            product.price = form.price.data
            image = form.image.data

            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product.image_filename = filename

            products[str(product_id)] = product

            flash('Product updated successfully!', 'success')
            return redirect(url_for('admin_product_list'))

    return render_template('update_product.html', form=form, product=product  )

@app.route('/delete_product/<product_id>')

def delete_product(product_id):

    with shelve.open('products.db', writeback=True) as products:
        # Convert product_id to string before using it as a key
        product_id_str = product_id

        if product_id_str in products:
            del products[product_id_str]

    return redirect(url_for('admin_product_list'))

# Add to Cart
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    # Read product from products shelf
    product_shelf = shelve.open('products.db')
    product = product_shelf.get(str(product_id))

    product_shelf.close()
    # cart_shelf = shelve.open('cart.db', writeback=True)
    # cart_id = len(cart_shelf) + 1
    # cart_shelf[str(cart_id)] = product
    # cart_shelf.close()
    if product and product.quantity > 0:
        # Save the product to the cart shelf
        cart_shelf = shelve.open('cart.db', writeback=True)
        cart_id = len(cart_shelf) + 1
        cart_shelf[str(cart_id)] = product
        cart_shelf.close()

        return redirect(url_for('product_list'))
    else:
        flash('This product is currently out of stock.', 'error')
        return redirect(url_for('product_list'))


# View Cart
@app.route('/view_cart')
@login_required
def view_cart():
    # Read products from the cart shelf
    cart_shelf = shelve.open('cart.db')
    cart_products = list(cart_shelf.values())

    cart_shelf.close()
    form = UpdateProductForm(obj=cart_products)
    total_price = sum(Decimal(product.price) for product in cart_products)

    return render_template('view_cart.html', cart_products=cart_products , form=form , total_price = total_price)

# Remove from Cart
@app.route('/remove_from_cart/<int:cart_id>')
@login_required
def remove_from_cart(cart_id):
    # Open the cart shelf
    cart_shelf = shelve.open('cart.db', writeback=True)

    # Ensure the cart_id is in string format
    cart_key = str(cart_id)

    if cart_key in cart_shelf:
        # Remove the item from the cart
        del cart_shelf[cart_key]
        flash('Item removed from cart successfully.', 'success')

        # Update the remaining cart item IDs
        for key in cart_shelf.keys():
            if int(key) > cart_id:
                new_key = str(int(key) - 1)
                cart_shelf[new_key] = cart_shelf[key]
                del cart_shelf[key]

    else:
        flash('Item not found in the cart.', 'error')

    # Close the cart shelf
    cart_shelf.close()

    # Redirect to view_cart route
    return redirect(url_for('view_cart'))


# Buy Item
@app.route('/buy_items', methods=['POST'])

def buy_items():

        # Read products from the cart shelf
        cart_shelf = shelve.open('cart.db')
        cart_products = list(cart_shelf.values())

        cart_shelf.close()

        # Check if there are items in the cart
        if not cart_products:
            flash('Your cart is empty. Please add items before purchasing.', 'error')
            return redirect(url_for('view_cart'))

        # total_amount = sum(Decimal(item['price']) * item['quantity'] for item in items_bought)
        total_points_earned = 0
        total_price = 0

        # Calculate total points earned based on price and quantity of each item
        for product in cart_products:
            product_id = product.product_id
            requested_quantity = int(request.form.get(f'quantity_{product_id}', 0))

            # Calculate points earned for this item
            points_earned_for_item = product.price * requested_quantity
            total_price = product.price * requested_quantity
            total_points_earned += points_earned_for_item

            # Update quantity of the product (if necessary)
        total_points_earned = round(total_points_earned)
       

        # Update the user's point balance in the database
        if current_user.is_authenticated:
            current_user_points = current_user.get_points() + total_points_earned
            current_user.set_points(current_user_points)
            User.save_to_shelve(current_user)

        flash(f'Total price: ${total_price} ,Total points earned: {total_points_earned}.', 'success')
        quantities_to_deduct = {}

        # Check if any item has a quantity of 0 or exceeds available quantity
        for product in cart_products:
            product_id = product.product_id
            requested_quantity = int(request.form.get(f'quantity_{product_id}', 0))

            if requested_quantity == 0:
                flash(f'Quantity cannot be 0 for {product.name}. Please update the quantity.', 'error')
                return redirect(url_for('view_cart'))

            if requested_quantity > product.quantity:
                flash(f'You cannot buy more than {product.quantity} of {product.name}.', 'error')
                return redirect(url_for('view_cart'))

            quantities_to_deduct[product_id] = requested_quantity

        # Deduct purchased quantity from products.db
        with shelve.open('products.db', writeback=True) as products:
            for product_id, quantity_to_deduct in quantities_to_deduct.items():
                product_in_db = products.get(str(product_id))
                if product_in_db:
                    product_in_db.quantity -= quantity_to_deduct

        # Save purchased items to the items_bought shelf
        user_items_bought_db = f'items_bought_{current_user.get_username()}.db'  # User-specific items bought db
        items_bought_shelf = shelve.open(user_items_bought_db, writeback=True)

        for product in cart_products:
            items_bought_id = len(items_bought_shelf) + 1

            # Create a dictionary to represent the bought item
            bought_item = {
                'username':  current_user.get_username if current_user.is_authenticated else 'Anonymous',
                'product_id': product.product_id,
                'name': product.name,
                'description': product.description,
                'energy_saving_rating': product.energy_saving_rating,
                'quantity': quantities_to_deduct[product.product_id],  # Use the purchased quantity
                'price': product.price,
                'image_filename': product.image_filename
            }

            items_bought_shelf[str(items_bought_id)] = bought_item
        items_bought_shelf.close()

        # Clear the cart after buying items
        cart_shelf = shelve.open('cart.db', writeback=True)
        cart_shelf.clear()
        cart_shelf.close()

        return redirect(url_for('items_bought'))





@app.route('/items_bought', methods=['GET', 'POST'])
def items_bought():
    username = current_user.get_username() if current_user.is_authenticated else None
    if username:
        user_items_bought_db = f'items_bought_{username}.db'  # User-specific items bought db
        # Read purchased items from the user-specific items_bought shelf
        items_bought_shelf = shelve.open(user_items_bought_db)
        items_bought = list(items_bought_shelf.values())
        items_bought_shelf.close()

        # Calculate the total amount
        total_amount = sum(Decimal(item['price']) * item['quantity'] for item in items_bought)



        return render_template('items_bought.html', items_bought=items_bought, total_amount=total_amount, username=username )
    else:
        flash('Please log in to view your purchased items.', 'error')
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)