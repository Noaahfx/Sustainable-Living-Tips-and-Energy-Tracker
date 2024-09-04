from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators, IntegerField, ValidationError, SelectField, \
    TextAreaField, FileField, Form, RadioField, DecimalField
from wtforms.validators import DataRequired, Email, NumberRange, InputRequired, Length, Regexp
from user import User
import re
from flask_wtf.file import FileField, FileAllowed

###############################(Karin(Start))###############################
class SignUpForm(FlaskForm):
    username = StringField('Username', [
        validators.Length(min=3, max=25),
        validators.Regexp('^[a-zA-Z0-9_]+$', message='Username must contain only letters, numbers, or underscores.')
    ])

    email = StringField('Email', [
        validators.Email(),
        validators.Length(max=50)
    ])

    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match'),
        validators.Length(min=8, message='Password must be at least 8 characters'),
        validators.Regexp(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&.])[A-Za-z\d@$!%*?&.]+$',
                          message='Password must contain at least 1 uppercase letter, 1 lowercase letter, 1 digit, and 1 special character')
    ])

    confirm = PasswordField('Confirm Password')

    def validate_username(self, field):
        existing_user = User.load_from_shelve(field.data)
        if existing_user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, field):
        existing_email_user = User.load_from_shelve_by_email(field.data)
        if existing_email_user:
            raise ValidationError('Email already in use. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=3, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])

    def validate(self):
        # Run the default validation logic
        if not super().validate():
            return False

        # Custom validation logic
        username = self.username.data
        password = self.password.data

        # Load the user from shelve
        user = User.load_from_shelve(username)

        if not user or not user.check_password(password):
            # Invalid credentials
            self.username.errors.append('Invalid credentials. Please try again.')
            self.password.errors.append('Invalid credentials. Please try again.')
            return False

        # Valid credentials
        return True

class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Hint: admin"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Hint: 123"})
    submit = SubmitField('Login')

    def validate(self):
        # Run the default validation logic
        if not super().validate():
            return False

        # Custom validation logic
        username = self.username.data
        password = self.password.data

        if username != 'admin' or password != '123':
            # Invalid admin credentials
            self.username.errors.append('Invalid admin credentials. Please use the provided hints.')
            self.password.errors.append('Invalid admin credentials. Please use the provided hints.')
            return False

        # Valid credentials
        return True

class ChangePasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[validators.DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        validators.DataRequired(),
        validators.EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')

    def validate_new_password(self, field):
        password = field.data

        # Use a regular expression to check password requirements
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&.])[A-Za-z\d@$!%*?&.]+$', password):
            raise ValidationError(
                'Password must have at least 8 characters, 1 uppercase letter, 1 lowercase letter, and 1 special character.'
            )
class UpdateParticularsForm(FlaskForm):
    name = StringField('Name', validators=[validators.DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    street_name = StringField('Street Name', validators=[validators.DataRequired()])
    unit_number = StringField('Unit Number', validators=[validators.DataRequired()])
    country = StringField('Country', validators=[validators.DataRequired()])
    submit = SubmitField('Update Particulars')

    def validate_age(self, field):
        if field.data is None or (field.data and field.data < 21):
            raise ValidationError('Age must be 21 or greater.')

    def validate_unit_number(self, field):
        if not re.match(r'^#\d+-\d+$', field.data):
            raise ValidationError('Unit number must be in the format #XX-XX.')


class EnergyQuizForm(FlaskForm):
    question_1 = SelectField('How often do you turn off lights when leaving a room?',
                             choices=[('Always', 'Always'), ('Sometimes', 'Sometimes'),
                                      ('Rarely', 'Rarely'), ('Never', 'Never')])

    question_2 = SelectField('What is your primary source of home heating?',
                             choices=[('Gas', 'Gas'), ('Electric', 'Electric'),
                                      ('Oil', 'Oil'), ('Other', 'Other')])
    question_3 = SelectField('What is a good practice for conserving energy when doing laundry?',
                             choices=[
                                 ('Using a clothesline to air-dry clothes', 'Using a clothesline to air-dry clothes'),
                                 ('Running the dryer for every small load', 'Running the dryer for every small load'),
                                 ('Washing clothes in hot water', 'Washing clothes in hot water'), (
                                 'Leaving the washing machine on standby mode',
                                 'Leaving the washing machine on standby mode')])

    question_4 = SelectField('What is a recommended way to reduce energy consumption in the kitchen?',
                             choices=[('Using energy-efficient appliances', 'Using energy-efficient appliances'), ('Leaving the refrigerator door open while deciding what to eat ', 'Leaving the refrigerator door open while deciding what to eat '),
                                      ('Running the oven with the door open', 'Running the oven with the door open'),
                                      ('Using the dishwasher for just a few dishes', 'Using the dishwasher for just a few dishes')])

    question_5 = SelectField('What is the most effective way to reduce standby power consumption in your home?',
                             choices=[('Using smart power strips to cut off power to idle devices',
                                       'Using smart power strips to cut off power to idle devices'), (
                                      'Keeping electronics plugged in even when not in use',
                                      'Keeping electronics plugged in even when not in use'),
                                      ('Running multiple electronic devices simultaneously', 'Running multiple electronic devices simultaneously'),
                                      ('Using old, inefficient power stripsNever', 'Using old, inefficient power strips ')])

    question_6 = SelectField( 'How often do you turn off lights and electronic devices when leaving a room?',
                            choices=[('Always', 'Always'), ('Sometimes', 'Sometimes'), ('Rarely', 'Rarely'), ('Never', 'Never')])

    question_7 = SelectField( 'Do you unplug electronic devices when they are fully charged or not in use for an extended period?',
        choices=[('Always', 'Always'), ('Sometimes', 'Sometimes'),
                 ('Rarely', 'Rarely'), ('Never', 'Never')])

    # Add more questions as needed

    submit = SubmitField('Submit')
###############################(Karin(End))###############################
###############################(Noah(Start))##############################

class ElectricityEntryForm(FlaskForm):
    year = IntegerField('Year', validators=[InputRequired()], render_kw={'min': '2000', 'max': '2024', 'pattern': '[0-9]+'})
    month = SelectField('Month', choices=[(str(i), month) for i, month in enumerate(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], 1)], validators=[InputRequired()])
    usage = IntegerField('Energy Usage (kWh)', validators=[InputRequired(), NumberRange(min=0, max=9999)], render_kw={'min': '0', 'data-error': 'Usage must be greater than 0.'})
    submit = SubmitField('Add Entry')

class EditElectricityEntryForm(FlaskForm):
    edit_year = IntegerField('Year', validators=[InputRequired()], render_kw={'min': '2000', 'max': '2024', 'pattern': '[0-9]+'})
    edit_month = SelectField('Month', choices=[(str(i), month) for i, month in enumerate(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], 1)], validators=[InputRequired()])
    edit_usage = IntegerField('Energy Usage (kWh)', validators=[InputRequired(), NumberRange(min=0, max=9999)], render_kw={'min': '0', 'data-error': 'Usage must be greater than 0.'})
    submit = SubmitField('Save Changes')
    csrf_token = StringField('CSRF Token')

class EnquiryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=320)])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=50)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=4000)])
    submit = SubmitField('Submit')

###############################(Noah(End))##############################
###############################(Keith(Start))##############################
class CreateForumForm(FlaskForm):
    title = StringField('Title', [validators.Length(min=1, max=100), validators.DataRequired()])
    content = TextAreaField('Comment', [validators.Length(min=1, max=200), validators.DataRequired()])
    image = FileField('Attach Relevant Image')
class CreateReviewsForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    image = FileField('Attach Relevant Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    rating = RadioField('Rating', choices=[('1', '1 star'), ('2', '2 stars'), ('3', '3 stars'), ('4', '4 stars'), ('5', '5 stars')], default='5')
###############################(Keith(End))##############################
###############################(James(Start))##############################

class CreateRewardForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    points = IntegerField('Points', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Submit')
class RedeemRewardForm(FlaskForm):
    submit = SubmitField('Redeem Reward')
class AddProductForm(FlaskForm):
    name = StringField('Name', validators=[ Length(min=1, max=150),
        DataRequired(),
        Regexp('^[A-Za-z0-9 ]*$', message="Name must contain only letters, numbers, and spaces.")
    ])
    description = TextAreaField('Description', validators=[Length(min=1, max=350),
        DataRequired(),
        Regexp('^[A-Za-z0-9 ,.!?]*$', message="Description must contain only letters, numbers, spaces, and basic punctuation.")
    ])
    energy_saving_rating = IntegerField('Energy Saving Rating', validators=[DataRequired(), NumberRange(min=1, max=5, message="Please enter a value between 1 and 5.")])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1,message="Please enter at least a postive value.")])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=1, message="Please enter at least a postive value.")])


#Define WTForm For Update
class UpdateProductForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(),
        Regexp('^[A-Za-z0-9 ]*$', message="Name must contain only letters, numbers, and spaces.")
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Regexp('^[A-Za-z0-9 ,.!?]*$', message="Description must contain only letters, numbers, spaces, and basic punctuation.")
    ])
    energy_saving_rating = IntegerField('Energy Saving Rating', validators=[DataRequired(),NumberRange(min=1, max=5, message="Please enter a value between 1 and 5.")])
    quantity = IntegerField('Quantity', validators=[DataRequired() , NumberRange(min=1, message="Please enter at least a postive value.")])
    price = DecimalField('Price', validators=[DataRequired() ,  NumberRange(min=1, message="Please enter at least a postive value.")])
    image = FileField('Image' ,validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])