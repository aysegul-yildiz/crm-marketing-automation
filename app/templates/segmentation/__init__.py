from flask import Blueprint

segmentation_bp = Blueprint(
    "segmentation",
    __name__,
    url_prefix="/segmentation"
)

from . import routes
