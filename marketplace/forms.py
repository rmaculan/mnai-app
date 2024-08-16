from django import forms
from .models import Item

class ItemPostForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'name', 
            'description', 
            'price', 
            'quantity', 
            'image', 
            'condition', 
            'category'
            ]
        
