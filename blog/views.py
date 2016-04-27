from flask import render_template, request, redirect, url_for

from . import app
from .database import session, Entry


PAGINATE_BY = 20


def get_entry(id):
    return session.query(Entry).get(id)
    
    
@app.route("/")
@app.route("/page/<int:page>")
def entries(page=1):
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
def add_entry_get():
    return render_template("add_entry.html")
    
@app.route("/entry/add", methods=["POST"])
def add_entry_post():
    entry = Entry(title=request.form["title"],
        content=request.form["content"]
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))

@app.route('/entry/<int:id>')
def single_entry_get(id):
    entry = get_entry(id)
    if entry:
        return render_template("single_entry.html",
            entry=entry
            )
    else:
        return redirect(url_for("error_route"))
        
@app.route('/entry/<int:id>/edit',methods=['GET'])
def edit_entry(id):
    entry = get_entry(id)
    if entry:
        return render_template("edit_entry.html",entry=entry)
    else:
        return redirect(url_for("error_route"))
    
@app.route('/entry/<int:id>/edit',methods=['POST'])
def update_entry(id):
    entry = get_entry(id)
    entry.title = request.form["title"]
    entry.content =request.form["content"]
    session.commit()
    return redirect(url_for("single_entry_get",id=id))

@app.route('/entry/<int:id>/delete')
def delete_entry(id):
    entry = get_entry(id)
    session.delete(entry)
    session.commit()
    return redirect(url_for("entries"))

@app.route('/404')
def error_route():
    return render_template("404.html")