from datetime import datetime

from pandas import ExcelWriter

from . import app
import pandas as pd

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app.forms import *
from app.models import *


# structure excel tables
provider_config = {1: {'skiprows': 6,
                       'game_name': 0,
                       'game_type': 1,
                       'table_id': 3,
                       'rtp': 5,
                       'rollout_date': 7,
                       'features': 6,
                       'status_name': 8,
                       },
                   2: {'skiprows': 6,
                       'game_name': 0,
                       'game_type': 1,
                       'table_id': 3,
                       'rtp': 5,
                       'rollout_date': 7,
                       'features': 6,
                       'status_name': 8,
                       },
                   3: {'skiprows': 6,
                       'game_name': 0,
                       'game_type': 1,
                       'table_id': 4,
                       'rtp': 6,
                       'rollout_date': 7,
                       'features': 8,
                       'status_name': 9,
                       },
                   }


def replace_rtp(rtp):
    result = str(rtp).strip()
    replace_chars = '?%@#$^&*() '
    for ch in replace_chars:
        result = result.replace(ch, '')
    if not result:
        return {'mode': 'list',
                'data': []}
    if '/' in result:
        result = list(map(lambda x: float(x.replace(',', '.')), result.split('/')))
        result = list(map(lambda x: x * 100 if x < 1 else x, result))
        return {'mode': 'list',
                'data': result}
    else:
        result = list(map(lambda x: float(x.replace(',', '.')), result.split('-')))
        result = list(map(lambda x: x * 100 if x < 1 else x, result))
        return {'mode': 'range',
                'data': result}


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@app.route('/index/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    items = Game.query.order_by(Game.name.asc()
                                ).paginate(page=page,
                                           per_page=app.config['ROWS_PER_PAGE'],
                                           error_out=False)
    return render_template('game_table.html',
                           items=items.items,
                           pagination=items)


def get_statuses():
    return [(s.id, s.name) for s in Status.query.order_by(
        Status.name.asc()).all()]


def get_providers():
    return [(p.id, p.name) for p in Provider.query.order_by(
        Provider.id.asc()).all()]


def get_types():
    return [(t.id, t.name) for t in GameType.query.order_by(
        GameType.name.asc()).all()]


@app.route('/games/create', methods=['GET', 'POST'])
@login_required
def game_create():
    form = GameForm()
    form.status.choices = get_statuses()
    form.provider.choices = get_providers()
    form.type.choices = get_types()
    if form.validate_on_submit():
        print(form.type.data)
        game = Game(provider_id=form.provider.data,
                    name=form.name.data,
                    type_id=form.type.data,
                    table_id=form.table_id.data,
                    features=form.features.data,
                    rollout_date=form.rollout_date.data,
                    status_id=form.status.data)
        db.session.add(game)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('data_form.html', form=form)


@app.route('/games/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def game_edit(id):
    game = Game.query.get_or_404(id)
    form = GameForm()
    form.status.choices = get_statuses()
    form.provider.choices = get_providers()
    form.type.choices = get_types()
    if form.validate_on_submit():
        game.provider_id = form.provider.data
        game.name = form.name.data
        game.type_id = form.type.data
        game.table_id = form.table_id.data
        game.features = form.features.data
        game.rollout_date = form.rollout_date.data
        game.status_id = form.status.data
        db.session.commit()
        return redirect(url_for('index', **request.args))
    elif request.method == 'GET':
        form.provider.default = game.provider_id
        form.status.default = game.status_id
        form.type.default = game.type_id
        form.process()
        form.name.data = game.name
        form.type.data = game.type_id
        form.table_id.data = game.table_id
        form.features.data = game.features
        form.rollout_date.data = game.rollout_date
    return render_template('data_form.html', form=form)


@app.route('/games/delete/<int:id>')
@login_required
def game_delete(id):
    game = Game.query.get_or_404(id)
    db.session.delete(game)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/import/', methods=['GET', 'POST'])
@login_required
def import_excel():
    form = ImportForm()
    form.provider.choices = get_providers()
    if form.validate_on_submit():
        mode = form.mode.data
        provider_id = form.provider.data
        config = provider_config.get(provider_id, None)
        if config:
            provider = Provider.query.get_or_404(provider_id)
            sheetname = f'{provider.name}_All_Slots'
            skiprows = config.get('skiprows', 7)
        else:
            flash(f'No config for provider with ID {provider_id}')
            return redirect(url_for('import_excel'))
        df = pd.read_excel('OSS RoG.xlsx', engine='openpyxl', sheet_name=sheetname, skiprows=skiprows)
        if form.clear.data:
            Game.query.delete()
            RTP.query.delete()
        count_import = 0
        count_update = 0
        for row in df.fillna(value='').itertuples(index=False):
            if row[0]:
                game_name = row[config.get('game_name')].strip()
                game_type_name = row[config.get('game_type')].strip()
                table_id = row[config.get('table_id')].strip()
                rollout_date = row[config.get('rollout_date')]
                if rollout_date and not isinstance(rollout_date, datetime):
                    try:
                        rollout_date = datetime.strptime(rollout_date.strip(), "%d.%m.%Y").date()
                    except ValueError:
                        rollout_date = None
                features = row[config.get('features')].strip()
                status_name = row[config.get('status_name')].strip()
                rtp_string = row[config.get('rtp')]
                status = Status.query.filter_by(name=status_name).first()
                if not status:
                    status = Status(name=status_name)
                    db.session.add(status)
                    db.session.flush()
                game_type = GameType.query.filter_by(name=game_type_name).first()
                if not game_type:
                    game_type = GameType(name=game_type_name)
                    db.session.add(game_type)
                    db.session.flush()
                game = Game.query.filter_by(table_id=table_id).first()
                if game:
                    if mode == 1:
                        game.provider_id = provider_id
                        game.name = game_name
                        game.type_id = game_type.id
                        game.table_id = table_id
                        game.features = features
                        if rollout_date:
                            game.rollout_date = rollout_date
                        game.status_id = status.id
                        db.session.flush()
                        count_update += 1
                    elif mode == 2:
                        continue
                else:
                    game_param = {'provider_id': provider_id,
                                  'name': game_name,
                                  'type_id': game_type.id,
                                  'table_id': table_id,
                                  'features': features,
                                  'status_id': status.id}
                    if rollout_date:
                        game_param['rollout_date'] = rollout_date
                    game = Game(**game_param)
                    db.session.add(game)
                    db.session.flush()
                    count_import += 1
                if rtp_string:
                    for game_rtp in game.rtp:
                        rtp_id = RTP.query.get(game_rtp.id)
                        db.session.delete(rtp_id)
                    db.session.flush()
                    list_rtp = replace_rtp(rtp_string)
                    if len(list_rtp.get('data')) > 1:
                        if list_rtp.get('mode') == 'range':
                            rtp_min = list_rtp.get('data')[0]
                            rtp_max = list_rtp.get('data')[1]
                            rtp = RTP(game_id=game.id,
                                      min=rtp_min,
                                      max=rtp_max)
                            db.session.add(rtp)
                            db.session.flush()
                        elif list_rtp.get('mode') == 'list':
                            for r in list_rtp.get('data'):
                                rtp_min = rtp_max = r
                                rtp = RTP(game_id=game.id,
                                          min=rtp_min,
                                          max=rtp_max)
                                db.session.add(rtp)
                                db.session.flush()
                    else:
                        if list_rtp.get('data'):
                            rtp_min = rtp_max = list_rtp.get('data')[0]
                            rtp = RTP(game_id=game.id,
                                      min=rtp_min,
                                      max=rtp_max)
                            db.session.add(rtp)
                            db.session.flush()
        if count_import + count_update > 0:
            db.session.commit()
            flash(f'Загружено {count_import} строк. Обновлено {count_update} строк')
        return redirect(url_for('index'))
    return render_template('data_form.html', form=form)


@app.route('/export/', methods=['GET', 'POST'])
@login_required
def export():
    mode = request.args.get('mode', 'xls')
    df = pd.DataFrame([(d.name, d.type, d.table_id) for d in Game.query.all()],
                      columns=['Game name', 'Game type', 'Table ID'])
    if mode == 'xls':
        print(1)
        writer = ExcelWriter('VlookUpExport.xlsx')
        df.to_excel(writer, 'Sheet1')
        writer.save()
    elif mode == 'csv':
        df.to_csv('vlookup_export.csv', sep=';', encoding='utf-8')
    return redirect(url_for('index'))


@app.route('/rtp/')
@login_required
def rtp():
    page = request.args.get('page', 1, type=int)
    game_id = request.args.get('game_id', None)
    if not game_id:
        flash('Incorrect request')
        return redirect(url_for('index'))
    game = Game.query.get_or_404(game_id)
    param = {'game_id': game_id}
    items = RTP.query.filter_by(**param).paginate(page=page,
                                                  per_page=app.config['ROWS_PER_PAGE'],
                                                  error_out=False)
    return render_template('rtp_table.html',
                           items=items.items,
                           pagination=items,
                           game=game)


@app.route('/rtp/create', methods=['GET', 'POST'])
@login_required
def rtp_create():
    game_id = request.args.get('game_id', None)
    form = RTPForm()
    if form.validate_on_submit():
        game = RTP(game_id=game_id,
                   min=form.min.data,
                   max=form.max.data)
        db.session.add(game)
        db.session.commit()
        return redirect(url_for('rtp', **request.args))
    return render_template('data_form.html', form=form)


@app.route('/rtp/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def rtp_edit(id):
    rtp = RTP.query.get_or_404(id)
    form = RTPForm()
    if form.validate_on_submit():
        rtp.min = form.min.data
        rtp.max = form.max.data
        db.session.commit()
        return redirect(url_for('rtp', **request.args))
    elif request.method == 'GET':
        form = RTPForm(obj=rtp)
    return render_template('data_form.html', form=form)


@app.route('/rtp/delete/<int:id>')
@login_required
def rtp_delete(id):
    rtp = RTP.query.get_or_404(id)
    db.session.delete(rtp)
    db.session.commit()
    return redirect(url_for('rtp', **request.args))
