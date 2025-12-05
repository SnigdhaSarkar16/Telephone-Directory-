# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from config import get_connection

app = Flask(__name__)
app.secret_key = 'dev-secret-key'  

@app.route('/')
def index():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Contacts ORDER BY last_name, first_name")
    contacts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', contacts=contacts)

@app.route('/add', methods=['POST'])
def add_contact():
    first = request.form.get('first_name', '').strip()
    last = request.form.get('last_name', '').strip()
    phone = request.form.get('phone_number', '').strip()
    email = request.form.get('email', '').strip()
    address = request.form.get('address', '').strip()

    if not first or not phone:
        flash('First name and phone number are required.', 'error')
        return redirect(url_for('index'))

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO Contacts (first_name, last_name, phone_number, email, address)
            VALUES (%s, %s, %s, %s, %s)
        """, (first, last, phone, email, address))
        conn.commit()
        flash('Contact added successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error adding contact: {e}', 'error')
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_contact(id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    if request.method == 'POST':
        first = request.form.get('first_name', '').strip()
        last = request.form.get('last_name', '').strip()
        phone = request.form.get('phone_number', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        try:
            cur.execute("""
                UPDATE Contacts
                SET first_name=%s, last_name=%s, phone_number=%s, email=%s, address=%s
                WHERE contact_id=%s
            """, (first, last, phone, email, address, id))
            conn.commit()
            flash('Contact updated.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error updating contact: {e}', 'error')
        finally:
            cur.close()
            conn.close()
        return redirect(url_for('index'))

    cur.execute("SELECT * FROM Contacts WHERE contact_id=%s", (id,))
    contact = cur.fetchone()
    cur.close()
    conn.close()
    if not contact:
        flash('Contact not found.', 'error')
        return redirect(url_for('index'))
    return render_template('edit.html', contact=contact)

@app.route('/delete/<int:id>')
def delete_contact(id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Contacts WHERE contact_id=%s", (id,))
        conn.commit()
        flash('Contact deleted.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting contact: {e}', 'error')
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    query = ''
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if query:
            like = f"%{query}%"
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT * FROM Contacts
                WHERE first_name LIKE %s OR last_name LIKE %s OR phone_number LIKE %s
                ORDER BY last_name, first_name
            """, (like, like, like))
            results = cur.fetchall()
            cur.close()
            conn.close()
    return render_template('search.html', results=results, query=query)

if __name__ == '__main__':
    app.run(debug=True)
