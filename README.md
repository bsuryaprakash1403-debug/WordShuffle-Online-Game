# WordShuffle – Online Word Game

A responsive Flask website with solo play, shared friend challenges, timer, score saving and leaderboard.

## Run locally (Windows / VS Code)

1. Extract this ZIP and open the folder in VS Code.
2. Open Terminal in the project folder.
3. Run:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

4. Visit http://127.0.0.1:5000

## Friends challenge

Choose **Friends Challenge** → **Create & share challenge** → copy the link or share it on WhatsApp. Friends open the public link and solve the same word. Their scores are saved in the same leaderboard.

## Publish online

Push the project to GitHub and create a Render Web Service.
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Add `gunicorn` to requirements.txt before deploying.
- Configure a persistent disk and set `DATABASE_PATH` to a file on that disk (for example `/var/data/database.db`) so SQLite scores survive redeploys.
- A public HTTPS URL is required for WhatsApp friends to access the challenge.

Note: the local Flask server is only accessible on your own computer/network. Friends outside your network need the site deployed publicly.
