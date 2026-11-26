from flask import Flask, render_template, request, jsonify, abort
import random, sqlite3, secrets, os

app = Flask(__name__)
DB = os.environ.get("DATABASE_PATH", "database.db")

WORDS = [
    ("APPLE","A fruit that can be red or green.","Easy"),
    ("PLANT","A living thing that grows in soil.","Easy"),
    ("CHAIR","Furniture you sit on.","Easy"),
    ("ORANGE","A citrus fruit and a colour.","Easy"),
    ("PYTHON","A popular programming language.","Medium"),
    ("SCHOOL","A place where students learn.","Medium"),
    ("PUZZLE","A game that tests your thinking.","Medium"),
    ("LIBRARY","A place filled with books.","Medium"),
    ("COMPUTER","An electronic device used for computing.","Hard"),
    ("KEYBOARD","You type using this device.","Hard"),
    ("EDUCATION","The process of learning.","Hard"),
    ("CREATIVE","Using imagination to make something new.","Hard")
]

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT NOT NULL, score INTEGER NOT NULL,
            mode TEXT NOT NULL DEFAULT 'individual',
            challenge_token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS challenges (
            token TEXT PRIMARY KEY, word TEXT NOT NULL, scrambled TEXT NOT NULL,
            hint TEXT NOT NULL, level TEXT NOT NULL, creator TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

def make_scramble(word):
    letters=list(word)
    for _ in range(30):
        random.shuffle(letters)
        mixed="".join(letters)
        if mixed != word:
            return mixed
    return word[::-1]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/word")
def get_word():
    level=request.args.get("level","Easy")
    choices=[w for w in WORDS if w[2]==level]
    word,hint,lvl=random.choice(choices or [w for w in WORDS if w[2]=="Easy"])
    return jsonify(word=word, scrambled=make_scramble(word), hint=hint, level=lvl)

@app.route("/api/challenge", methods=["POST"])
def create_challenge():
    data=request.get_json() or {}
    level=data.get("level","Easy")
    creator=(data.get("player") or "A friend").strip()[:24] or "A friend"
    choices=[w for w in WORDS if w[2]==level]
    word,hint,lvl=random.choice(choices or WORDS)
    mixed=make_scramble(word)
    token=secrets.token_urlsafe(7)
    with db() as con:
        con.execute("INSERT INTO challenges(token,word,scrambled,hint,level,creator) VALUES(?,?,?,?,?,?)",
                    (token,word,mixed,hint,lvl,creator))
    return jsonify(url=request.host_url.rstrip("/")+"/challenge/"+token, token=token)

@app.route("/challenge/<token>")
def challenge(token):
    with db() as con:
        row=con.execute("SELECT token,word,scrambled,hint,level,creator FROM challenges WHERE token=?",(token,)).fetchone()
    if not row: abort(404)
    return render_template("index.html", challenge=dict(row))

@app.route("/api/challenge/<token>")
def challenge_data(token):
    with db() as con:
        row=con.execute("SELECT word,scrambled,hint,level,creator FROM challenges WHERE token=?",(token,)).fetchone()
    if not row: return jsonify(error="Challenge not found"),404
    return jsonify(dict(row))

@app.route("/api/score", methods=["POST"])
def save_score():
    data=request.get_json() or {}
    player=(data.get("player") or "Player").strip()[:24] or "Player"
    score=max(0,min(100000,int(data.get("score",0))))
    token=data.get("challenge_token")
    mode="challenge" if token else "individual"
    with db() as con:
        if token and not con.execute("SELECT 1 FROM challenges WHERE token=?",(token,)).fetchone():
            return jsonify(error="Invalid challenge"),404
        con.execute("INSERT INTO scores(player,score,mode,challenge_token) VALUES (?,?,?,?)",
                    (player,score,mode,token))
    return jsonify(ok=True)

@app.route("/api/leaderboard")
def leaderboard_data():
    token=request.args.get("challenge")
    with db() as con:
        if token:
            rows=con.execute("SELECT player,score FROM scores WHERE challenge_token=? ORDER BY score DESC, id ASC LIMIT 20",(token,)).fetchall()
        else:
            rows=con.execute("SELECT player,score FROM scores ORDER BY score DESC, id ASC LIMIT 20").fetchall()
    return jsonify(rows=[dict(r) for r in rows])

@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")

@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"),404

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)), debug=True)
