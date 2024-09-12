# recipes/forms.py

from django import forms
from .models import Recipe

class RecipeSearchForm(forms.Form):
    search_term = forms.CharField(required=False)
    #category = forms.ChoiceField(choices=[('', 'All')] + list(set([(recipe.category, recipe.category) for recipe in Recipe.objects.all()])),required=False )
    cooking_time = forms.IntegerField(required=False, min_value=0, label="Max Cooking Time (minutes)")
    difficulty = forms.ChoiceField(choices=[('', 'All')] + Recipe.DIFFICULTY_CHOICES, required=False)