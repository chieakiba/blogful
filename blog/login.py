from flask.ext.login import LoginManager

import app
from .database import session, User


login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login_get"
login_manager.login_message_category = "danger"

@login_manager.user_loader
def load_user(id):
    """ get user from DB """
    return session.query(User).get(int(id))
