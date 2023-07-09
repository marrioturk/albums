from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date
import os

app = Flask(__name__)
DATABASE = os.path.join(os.getcwd(), 'albums.db')

def create_table():
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS albums (artist TEXT, album TEXT, entry_date TEXT)")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"An error occurred while creating the table: {str(e)}")

@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        search_term = request.args.get('search')  # Get the search term from the query parameters
        sort_by = request.args.get('sort')  # Get the sort option from the query parameters

        if search_term:
            c.execute("SELECT rowid, * FROM albums WHERE artist LIKE ? OR album LIKE ?",
                      ('%' + search_term + '%', '%' + search_term + '%'))  # Filter albums based on search term
        else:
            if sort_by == 'artist':
                c.execute("SELECT rowid, * FROM albums ORDER BY artist ASC")  # Sort albums alphabetically by artist
            elif sort_by == 'date':
                c.execute("SELECT rowid, * FROM albums ORDER BY date(entry_date) ASC")  # Sort albums by entry date
            else:
                c.execute("SELECT rowid, * FROM albums")

        albums = c.fetchall()
        conn.close()
        return render_template('index.html', albums=albums, search_term=search_term, sort_by=sort_by)
    except Exception as e:
        print(f"An error occurred in the home route: {str(e)}")

@app.route('/add', methods=['GET', 'POST'])
def add_album():
    try:
        if request.method == 'POST':
            artist = request.form['artist']
            album = request.form['album']
            entry_date = date.today().strftime("%d/%m/%Y")  # Automatically add today's date as the entry date
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute("INSERT INTO albums (artist, album, entry_date) VALUES (?, ?, ?)",
                      (artist, album, entry_date))
            conn.commit()
            conn.close()
            return redirect('/')
        return render_template('add.html')
    except Exception as e:
        print(f"An error occurred in the add_album route: {str(e)}")

@app.route('/delete/<int:album_id>', methods=['POST', 'DELETE'])
def delete_album(album_id):
    try:
        if request.method in ['POST', 'DELETE']:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute("SELECT album FROM albums WHERE rowid=?", (album_id,))
            album = c.fetchone()
            if album:
                c.execute("DELETE FROM albums WHERE rowid=?", (album_id,))
                conn.commit()
                conn.close()
                return redirect('/')
        return redirect('/')
    except Exception as e:
        print(f"An error occurred in the delete_album route: {str(e)}")

if __name__ == '__main__':
    try:
        create_table()
        app.run(debug=True)
    except Exception as e:
        print(f"An error occurred while running the application: {str(e)}")
