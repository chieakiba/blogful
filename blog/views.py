from flask import render_template, request, redirect, url_for, flash, abort
from flask.ext.login import login_user, login_required, current_user, logout_user
from werkzeug.security import check_password_hash

from . import app
from .database import session, Entry, User


PAGINATE_BY = 20


def get_entry(id):
    """ get specific entry from DB """
    return session.query(Entry).get(id)
    
    
@app.route("/")
@app.route("/page/<int:page>")
def entries(page=1):
    """ route for root and specific page of entries """
    # Zero-indexed page
    if request.args.get('limit'):
        try:
            limit = int(request.args.get('limit'))
        except ValueError:
            limit = PAGINATE_BY
    else: 
        limit = PAGINATE_BY

    page_index = page - 1
    count = session.query(Entry).count()

    start = (page_index * limit) or 0
    end = start + limit

    total_pages = (count - 1) / limit + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]
    if limit == PAGINATE_BY:
        limit = None
        
    return render_template("entries.html",
        entries=entries,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages,
        limit=limit
    )
    
@app.route('/entry/add',methods=["GET"])
@login_required
def add_entry_get():
    """ add entry form """
    return render_template("add_entry.html")
    
@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    """ add entry to DB """
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
        author=current_user
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))

@app.route('/entry/<int:id>')
def single_entry_get(id):
    """ get single entry """
    entry = get_entry(id)
    if entry:
        return render_template("single_entry.html",
            entry=entry
            )
    else:
        abort(404)
        
@app.route('/entry/<int:id>/edit',methods=['GET'])
@login_required
def edit_entry(id):
    """ get form to edit single entry """
    
    entry = get_entry(id)
    if entry and entry.author and entry.author.id == current_user.id:
        return render_template("edit_entry.html",entry=entry)
    else:
        abort(404)
    
@app.route('/entry/<int:id>/edit',methods=['POST'])
@login_required
def update_entry(id):
    """ post route for editing entry """
    entry = get_entry(id)
    if not entry or not entry.author or entry.author.id != current_user.id:
         abort(404)
         
    entry.title = request.form["title"]
    entry.content =request.form["content"]
    session.commit()
    return redirect(url_for("single_entry_get",id=id))

@app.route('/entry/<int:id>/delete')
@login_required
def delete_entry(id):
    """ delete entry """
    entry = get_entry(id)
    if entry.author and entry.author.id == current_user.id:
        session.delete(entry)
        session.commit()
        return redirect(url_for("entries"))
    else:
        abort(404)
        
@app.errorhandler(404)
def error_route(e):
    """ return 404 """
    return render_template('404.html'), 404
    
@app.route("/login",methods=["GET"])
def login_get():
    """ return login template """
    return render_template("login.html")
    
@app.route('/login', methods=["POST"])
def login_post():
    """ check user credentials """
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))
    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))

@app.route('/logout')
def logout():
    """ logout current user """
    logout_user()
    return redirect(url_for('entries'))