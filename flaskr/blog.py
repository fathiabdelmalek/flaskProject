from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    blogs = db.execute(
        'SELECT p.id, p.title, p.body, p.created, p.author_id, u.username'
        ' FROM blog p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', blogs=blogs)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is None:
            try:
                db = get_db()
                db.execute(
                    'INSERT INTO blog (title, body, author_id)'
                    ' VALUES (?, ?, ?)',
                    (title, body, g.user['id'])
                )
                db.commit()
            except db.IntegrityError:
                error = f"Blog with this title already exists."
            else:
                flash("Blog created successfully", "success")
                return redirect(url_for('blog.index'))

        flash(error)

    return render_template('blog/create.html')


def read(id, check_author=True):
    blog = get_db().execute(
        'SELECT p.id, p.title, p.body, p.created, p.author_id, u.username'
        ' FROM blog p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if blog is None:
        abort(404, f"Bost id {id} doesn't exist.")

    if check_author and blog['author_id'] != g.user['id']:
        abort(403)

    return blog


@bp.route('/<int:id>')
def blog_page(id):
    blog = read(id, False)
    return render_template('blog/blog.html', blog=blog)


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    blog = read(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is None:
            try:
                db = get_db()
                db.execute(
                    'UPDATE blog SET title = ?, body = ?'
                    ' WHERE id = ?',
                    (title, body, id)
                )
                db.commit()
            except db.IntegrityError:
                error = f"Blog with this title already exists."
            else:
                flash("Blog updated successfully", "success")
                return redirect(url_for('blog.index'))

        flash(error, "error")

    return render_template('blog/update.html', blog=blog)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    read(id)
    db = get_db()
    try:
        db.execute('DELETE FROM blog WHERE id = ?', (id,))
        db.commit()
    except db.Error:
        flash("Failed to delete blog", "error")
    else:
        flash("Blog deleted successfully", "success")
    return redirect(url_for('blog.index'))
