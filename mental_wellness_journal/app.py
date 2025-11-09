from flask import Flask, render_template, request, redirect, send_file
import sqlite3
from datetime import datetime
from collections import Counter
import csv
import os

app = Flask(__name__)

QUOTES = [
    "Take a deep breath. You've got this.",
    "It's okay to not be okay.",
    "Every day may not be good... but there is something good in every day."
]


def init_db():
    conn = sqlite3.connect('journal.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS entries
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  mood TEXT,
                  activity TEXT,
                  note TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('journal.db')
    c = conn.cursor()
    c.execute("SELECT * FROM entries ORDER BY date DESC")
    entries = c.fetchall()
    moods = [entry[2] for entry in entries]
    mood_counts = dict(Counter(moods))
    latest_mood = moods[0] if moods else "Happy"
    mood_image = {
        "Happy": "happy.jpg",
        "Sad": "sad.jpg",
        "Angry": "angry.jpg",
        "Anxious": "anxious.jpg",
        "Tired": "tired.jpg"
    }.get(latest_mood, "happy.jpg")
    quote = QUOTES[len(entries) % len(QUOTES)]
    conn.close()
    return render_template('index.html', entries=entries, mood_counts=mood_counts, mood_image=mood_image, quote=quote)

@app.route('/add', methods=['POST'])
def add_entry():
    mood = request.form['mood']
    activity = request.form['activity']
    note = request.form['note']
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('journal.db')
    c = conn.cursor()
    c.execute("INSERT INTO entries (date, mood, activity, note) VALUES (?, ?, ?, ?)", (date, mood, activity, note))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/export')
def export():
    conn = sqlite3.connect('journal.db')
    c = conn.cursor()
    c.execute("SELECT * FROM entries")
    entries = c.fetchall()
    conn.close()
    filepath = 'journal_export.csv'
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Date', 'Mood', 'Activity', 'Note'])
        writer.writerows(entries)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
