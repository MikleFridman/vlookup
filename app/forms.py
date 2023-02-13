from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, BooleanField, PasswordField, DateField, TextAreaField, \
    FloatField
from wtforms.validators import DataRequired, Length, Optional, ValidationError


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Submit')


class GameForm(FlaskForm):
    provider = SelectField('Provider', choices=[], validate_choice=True, coerce=int)
    name = StringField('Game name', validators=[DataRequired()])
    type = SelectField('Game type', choices=[], validate_choice=True, coerce=int)
    type_new = StringField('Create new type', validators=[Length(max=32)])
    table_id = StringField('Table id', validators=[DataRequired()])
    features = TextAreaField('Features', validators=[Length(max=255)])
    rtp = StringField('RTP', validators=[Length(max=64)])
    rollout_date = DateField('Rollout date', validators=(Optional(),))
    status = SelectField('Status', choices=[], validate_choice=True, coerce=int)
    submit = SubmitField('Submit')

    def validate_provider(self, field):
        if self.provider.data == 0:
            raise ValidationError('Select provider')

    def validate_status(self, field):
        if self.status.data == 0:
            raise ValidationError('Select status')

    def validate_type(self, field):
        if field.data == 0 and len(self.type_new.data.strip()) == 0:
            raise ValidationError('Enter new type')

    def validate_type_new(self, field):
        if self.type.data != 0 and len(field.data.strip()) != 0:
            raise ValidationError('Multiple choice of game type')


class ImportForm(FlaskForm):
    provider = SelectField('Provider', choices=[], validate_choice=True, coerce=int)
    mode = SelectField('Change mode', choices=[(1, 'Rewrite'), (2, 'Ignore')], default=1,
                       validate_choice=True, coerce=int)
    clear = BooleanField('Clear data before upload')
    submit = SubmitField('Submit')

    def validate_provider(self):
        if self.provider.data == 0:
            raise ValidationError('Select provider')


class RTPForm(FlaskForm):
    min = FloatField('Min', default=0, validators=[DataRequired()])
    max = FloatField('Max', default=0, validators=[DataRequired()])
    submit = SubmitField('Submit')

