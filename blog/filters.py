from flask import Markup
import mistune as md

from . import app


@app.template_filter()
def markdown(text): 
    """ jinja filter for markdown text """
    return Markup(md.markdown(text,escape=True))

@app.template_filter()
def dateformat(date,format):
    """ format date """
    if not date:
        return None
    return date.strftime(format) 
    