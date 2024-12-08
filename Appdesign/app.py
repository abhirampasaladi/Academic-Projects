from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField
from wtforms.validators import DataRequired, Email
import sqlite3
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

class FeedbackForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    feedback = RadioField(
        'Feedback',
        choices=[('good', 'Good'), ('bad', 'Bad'), ('very_good', 'Very Good'), ('very_bad', 'Very Bad')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Submit')


@app.route('/feedbacks', methods=['GET'])
def list_feedbacks():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, feedback FROM feedback')
    feedbacks = cursor.fetchall()
    conn.close()
    return render_template('list_feedbacks.html', feedbacks=feedbacks)


@app.route('/edit_feedback/<int:feedback_id>', methods=['GET', 'POST'])
def edit_feedback(feedback_id):
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        feedback = request.form['feedback']
        cursor.execute(
            'UPDATE feedback SET name = ?, email = ?, feedback = ? WHERE id = ?',
            (name, email, feedback, feedback_id)
        )
        conn.commit()
        conn.close()
        flash('Feedback updated successfully!')
        return redirect(url_for('list_feedbacks'))

    cursor.execute('SELECT id, name, email, feedback FROM feedback WHERE id = ?', (feedback_id,))
    feedback = cursor.fetchone()
    conn.close()
    return render_template('edit_feedback.html', feedback=feedback)


@app.route('/delete_feedback/<int:feedback_id>', methods=['POST'])
def delete_feedback(feedback_id):
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM feedback WHERE id = ?', (feedback_id,))
    conn.commit()
    conn.close()
    flash('Feedback deleted successfully!')
    return redirect(url_for('list_feedbacks'))

def init_db():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            feedback TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        conn = sqlite3.connect('feedback.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO feedback (name, email, feedback) VALUES (?, ?, ?)',
                       (form.name.data, form.email.data, form.feedback.data))
        conn.commit()
        conn.close()
        flash("Thank you for submitting the form!")  # Add this line
        return redirect(url_for('home'))
    return render_template('feedback.html', form=form)



@app.route('/chart')
def chart():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute('SELECT feedback, COUNT(*) FROM feedback GROUP BY feedback')
    data = cursor.fetchall()
    conn.close()

    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    # Generate chart
    plt.figure(figsize=(6, 4))
    plt.bar(labels, values, color=['green', 'red', 'blue', 'orange'])
    plt.title('Feedback Distribution')
    plt.xlabel('Feedback')
    plt.ylabel('Count')
    plt.savefig('static/chart.png')

    return render_template('chart.html', chart_url='static/chart.png')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
