import random
import os, sys

import flask
from flask_sqlalchemy import SQLAlchemy



app = flask.Flask(__name__)

# Database

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hangman.db'
db = SQLAlchemy(app)

# Model

def random_pk():
    return random.randint(1e9, 1e10)

class Game(db.Model):
    pk = db.Column(db.Integer, primary_key=True, default=random_pk)
    word = db.Column(db.String(50), default='')
    tried = db.Column(db.String(50), default='')
    player = db.Column(db.String(50))
    time = db.Column(db.String(50))

    def __init__(self, player):
        self.player = player

    @property
    def errors(self):
        return ''.join(set(self.tried) - set(self.word))

    @property
    def current(self):
        return ''.join([c if c in self.tried else '_' for c in self.word])

    @property
    def points(self):
        return 100 + 2*len(set(self.word)) + len(self.word) - 10*len(self.errors)

    @property
    def tried_letters(self):
        return self.tried

    def set_time(self, time):
        self.time = time


    # Play

    def try_letter(self, letter):
        if not self.finished and letter not in self.tried:
            self.tried += letter
            db.session.commit()
            return True
        else:
            return False

    # Game status

    @property
    def won(self):
        return self.current == self.word

    @property
    def lost(self):
        return len(self.errors) == 6

    @property
    def finished(self):
        return self.won or self.lost


# Controller

@app.route('/')
def home():
    games = sorted(
        [game for game in Game.query.all() if game.won],
        key=lambda game: -game.points)[:10]
    return flask.render_template('home.html', games=games)


@app.route('/play')
def new_game():

    # get game mode and player name
    player = flask.request.args.get('player')
    mode = flask.request.args.get('mode')
    # print(player, mode)

    game = Game(player)
    db.session.add(game)

    # based on the mode, randomly choose a word
    list_of_words = []
    if (int(mode) == 0):
        # easy mode = length of word (0, 5]
        list_of_words = [line.strip() for line in open('words.txt') if len(line.strip()) > 0 and len(line.strip()) <= 5]
    elif (int(mode) == 1):
        # medium mode = length of word [6, 10]
        list_of_words = [line.strip() for line in open('words.txt') if len(line.strip()) > 5 and len(line.strip()) < 11]
    else:
        # hard mode = length of word [11, 15]
        list_of_words = [line.strip() for line in open('words.txt') if len(line.strip()) > 10 and len(line.strip()) < 16]

    # print(list_of_words)
    word = random.choice(list_of_words).upper()
    game.word = word
    # print(word)
    db.session.commit()
    # print(game.pk, game.word)
    return flask.redirect(flask.url_for('play', game_id=game.pk))


@app.route('/play/<game_id>', methods=['GET', 'POST'])
def play(game_id):
    game = Game.query.get_or_404(game_id)

    if flask.request.method == 'POST':
        # get time and the letter chosen by the user if it's a post request
        letter = flask.request.form['letter'].upper().split('=')[1]
        time = flask.request.form['time']


        # check if the letter chosen by the user is in the hidden word or not
        old_length = len(game.errors)
        correct = True
        repeat = False
        if len(letter) == 1 and letter.isalpha():
            tried = game.try_letter(letter)
            # if tried already, then repeat = true
            if not tried: repeat = True

            if old_length < len(game.errors):
                # wrong letter
                correct = False

        if game.won:
            # set time and word
            if (time.strip() == '00:00:00'):
                time = 'N/A'        # timer setting not activated
            game.set_time(time)
            db.session.commit()

        return flask.jsonify(current=game.current,
                             errors=game.errors,
                             finished=game.finished,
                             correct=correct,
                             repeat=repeat)

    else:

        # pass the letters dictionary to jinja template
        # key is the character
        # the value of the dictionary comprises of a tuple
        # where 0th index is the index and 1st index indicate whether the letter was correctly chosen
        # or if the letter was never chosen or the letter was chosen correctly
        letters = {}
        for i in range(26):
            c = chr(i + ord('A'))
            errors = game.errors
            tried = game.tried_letters
            if c in tried:
                if c in errors:
                    letters[c] = (i, 1)
                else: letters[c] = (i, -1)
            else: letters[c] = (i, 0)

        return flask.render_template('play.html', game=game, letters=letters)


def base_path(path):
    if getattr(sys, 'frozen', None):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)


# Main
if __name__ == '__main__':
    os.chdir(base_path(''))
    app.run(host='0.0.0.0', debug=True)
