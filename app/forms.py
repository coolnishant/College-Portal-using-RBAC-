from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('EmailId', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    # remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class SignupForm(FlaskForm):
    username = StringField('Full Name', validators=[DataRequired()])
    emailid = StringField('Emailid', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    # remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign Up')

class AddStudentForm(FlaskForm):
    submit = SubmitField('Add Students')

class AddTAForm(FlaskForm):
    submit = SubmitField('Add TA')

class RemoveTAForm(FlaskForm):
    submit = SubmitField('Remove TA')

class AddEditStudentMarksForm(FlaskForm):
    submit = SubmitField('Change Student Marks')

class DeleteStudentMarksForm(FlaskForm):
    submit = SubmitField('Delete Student Marks')

class CreatingCoursesForm(FlaskForm):
    idcourses = StringField('Course ID (eg:C102)', validators=[DataRequired()])
    coursename = StringField('Course Name', validators=[DataRequired()])
    submit = SubmitField('Add New Course')

class AccountApprovalForm(FlaskForm):
    submit = SubmitField('Role Assignment')

class AssignFacultyCourseForm(FlaskForm):
    submit = SubmitField('Assign to ')
