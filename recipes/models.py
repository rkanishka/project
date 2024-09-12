from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import uuid

class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Intermediate', 'Intermediate'),
        ('Hard', 'Hard'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    ingredients = models.TextField()
    cooking_time = models.PositiveIntegerField(help_text="in minutes")
    instructions = models.TextField(default="No instructions provided.")
    image = models.ImageField(upload_to='recipe_images/', default='default_recipe.jpg')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Easy')
    #category = models.CharField(max_length=100)  
    #created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    
    def calculate_difficulty(self):
        ingredients_count = len(self.ingredients.split(','))
        if self.cooking_time < 10 and ingredients_count < 4:
            return 'Easy'
        elif self.cooking_time < 10 and ingredients_count >= 4:
            return 'Medium'
        elif self.cooking_time >= 10 and ingredients_count < 4:
            return 'Intermediate'
        else:
            return 'Hard'

    def save(self, *args, **kwargs):
        if not self.difficulty:
            self.difficulty = self.calculate_difficulty()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('recipes:recipe_detail', args=[str(self.id)])

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']