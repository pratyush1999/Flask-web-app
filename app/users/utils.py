import os
import secrets
from flask import current_app
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.split(form_picture.filename)
    picture_fn = 'profile_pics/' + random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

