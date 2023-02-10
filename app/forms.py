from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, BooleanField, PasswordField, DateField, TextAreaField, \
    FloatField
from wtforms.validators import DataRequired, Length, Optional


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Submit')


class GameForm(FlaskForm):
    provider = SelectField('Provider', choices=[], validate_choice=True, coerce=int)
    name = StringField('Game name', validators=[DataRequired()])
    type = SelectField('Game type', choices=[], validate_choice=True, coerce=int)
    table_id = StringField('Table id', validators=[DataRequired()])
    features = TextAreaField('Features', validators=[Length(max=255)])
    rollout_date = DateField('Rollout date', validators=(Optional(),))
    status = SelectField('Status', choices=[], validate_choice=True, coerce=int)
    submit = SubmitField('Submit')


class ImportForm(FlaskForm):
    provider = SelectField('Provider', choices=[], validate_choice=True, coerce=int)
    mode = SelectField('Change mode', choices=[(1, 'Rewrite'), (2, 'Ignore')], default=1,
                       validate_choice=True, coerce=int)
    clear = BooleanField('Clear data before upload')
    submit = SubmitField('Submit')


class RTPForm(FlaskForm):
    min = FloatField('Min', default=0, validators=[DataRequired()])
    max = FloatField('Min', default=0, validators=[DataRequired()])
    submit = SubmitField('Submit')

