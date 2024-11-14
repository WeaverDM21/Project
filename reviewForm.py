from flask_wtf import FlaskForm
from wtforms.fields import SelectField, TextAreaField, SubmitField
from wtforms.validators import InputRequired

# define our own FlaskForm subclass for our form
class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])
    text = TextAreaField('Review', validators = [InputRequired()])
    submit = SubmitField("Submit")