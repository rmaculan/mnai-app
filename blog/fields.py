from django.db import models
from django.forms import FileField
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_svg_or_image(value):
    """Custom validator to accept both SVG and regular image files"""
    import os
    from PIL import Image
    
    ext = os.path.splitext(value.name)[1].lower()
    
    # If it's an SVG, let it pass
    if ext == '.svg':
        return
    
    # Otherwise, try to open it as an image
    try:
        Image.open(value)
    except Exception:
        raise ValidationError(_('File must be a valid image or SVG.'))

class SVGAndImageField(models.FileField):
    """A field that validates uploaded files are either SVG or regular images."""
    
    def __init__(self, *args, **kwargs):
        # Add SVG validator
        kwargs.setdefault('validators', []).append(validate_svg_or_image)
        super().__init__(*args, **kwargs)
