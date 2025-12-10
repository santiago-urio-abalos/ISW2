from django import forms
from .models import Review

STAR_CHOICES = [
    (1, '★☆☆☆☆'),
    (2, '★★☆☆☆'),
    (3, '★★★☆☆'),
    (4, '★★★★☆'),
    (5, '★★★★★'),
]

class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(choices=STAR_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = Review
        fields = ['comment', 'rating']
