#! export FLASK_APP=server.py ; python -m flask run
from flask import Flask, request, render_template, redirect, url_for
from markupsafe import escape
import os
app = Flask(__name__, static_url_path='', static_folder='static')


def get_teams():
    result = {}
    for file in os.listdir('teams'):
        fn = os.path.join('teams', file)
        result[file] = open(fn, 'r').read().strip().split('\n')
    return result


def get_problems():
    result = {}
    for file in os.listdir('problems'):
        if file[-7:] == '.answer':
            continue
        ftext = os.path.join('problems', file)
        fansw = os.path.join('problems', file + '.answer')
        result[file] = {
            'text': open(ftext, 'r').read(),
            'answer': open(fansw, 'r').read() if os.path.exists(fansw) else None
        }
    return result
    

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', toptext="")


@app.route('/', methods=['POST'])
def index_post():
    teamcode = request.form['teamcode'] if request.form['teamcode'] else None
    if teamcode is not None:
        teams = get_teams()
        if teamcode not in teams:
            return render_template('index.html', toptext="Команды с таким кодом нет. Пожалуйста, введите заново. Регистр важен!")
        else:
            # redirect to first question
            return redirect(('/Q/' + teamcode + '/' + teams[teamcode][0]))
    else:
        return render_template('index.html', toptext="Вы не ввели код. Пожалуйста, введите заново. Регистр важен!")
        
        
@app.route('/Q/<teamcode>/<problemcode>', methods=['GET'])
def problem_show(teamcode, problemcode):
    # process problems
    if not teamcode:
        return redirect(url_for('/'))
        
    teams = get_teams()
    if not problemcode:
        teams = get_teams()
        if teamcode not in teams:
            return redirect(url_for('/'))
        else:
            return redirect(('/Q/' + teamcode + '/' + teams['teamcode'][0]))
    
    # show problem
    problems = get_problems()
    idx = teams[teamcode].index(problemcode)
    epic = idx == len(teams[teamcode]) - 1
    return render_template('problem.html', task=problems[problemcode]['text'], team=teamcode, epic=epic)


@app.route('/Q/<teamcode>/<problemcode>', methods=['POST'])
def problem_accept(teamcode, problemcode):
    # process problems
    if not teamcode:
        return redirect(url_for('/'))
    teams = get_teams()
    if not problemcode:
        if teamcode not in teams:
            return redirect(url_for('/'))
        else:
            return redirect(('/Q/' + teamcode + '/' + teams[teamcode][0]))
    
    print("!!!")
    problems = get_problems()
    ans = request.form['answer'] if 'answer' in request.form else None
    print(ans)
    if ans != problems[problemcode]['answer']:
        return render_template('problem.html', 
                task=problems[problemcode]['text'], 
                team=teamcode, 
                toptext="Кажется ответ неправильный. Попробуйте ещё раз" + problems[problemcode]['answer'])
    else:
        # correct guess
        idx = teams[teamcode].index(problemcode)
        nextcode = teams[teamcode][idx + 1]
        return redirect(('/Q/' + teamcode + '/' + nextcode))