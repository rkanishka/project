from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg
from .models import Recipe
from .forms import RecipeSearchForm
import matplotlib.pyplot as plt
import io
import urllib, base64

def home(request):
    return render(request, 'recipes/recipes_home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('recipes:recipe_list')
        else:
            return render(request, 'recipes/login.html', {'error': 'Invalid credentials'})
    return render(request, 'recipes/login.html')

def logout_view(request):
    logout(request)
    return render(request, 'recipes/success.html')

@login_required(login_url='recipes:login')
def recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})

@login_required(login_url='recipes:login')
def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})

@login_required(login_url='recipes:login')
def recipe_search(request):
    form = RecipeSearchForm(request.GET)
    results = Recipe.objects.all()

    if form.is_valid():
        search_term = form.cleaned_data.get('search_term')
        cooking_time = form.cleaned_data.get('cooking_time')
        difficulty = form.cleaned_data.get('difficulty')

        if search_term:
            results = results.filter(
                Q(name__icontains=search_term) | 
                Q(ingredients__icontains=search_term) |
                Q(instructions__icontains=search_term)
            )
        
        if cooking_time:
            results = results.filter(cooking_time__lte=cooking_time)
        
        if difficulty:
            results = results.filter(difficulty=difficulty)

    # Generate charts
    difficulty_chart = generate_difficulty_chart()
    cooking_time_chart = generate_cooking_time_chart()

    context = {
        'form': form,
        'results': results,
        'difficulty_chart': difficulty_chart,
        'cooking_time_chart': cooking_time_chart,
    }

    return render(request, 'recipes/recipe_search.html', context)

def generate_difficulty_chart():
    difficulties = Recipe.objects.values('difficulty').annotate(count=Count('id'))
    plt.figure(figsize=(8, 8))
    plt.pie([diff['count'] for diff in difficulties], labels=[diff['difficulty'] for diff in difficulties], autopct='%1.1f%%')
    plt.title('Distribution of Recipes by Difficulty')
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    
    plt.close()
    return graphic

def generate_cooking_time_chart():
    avg_cooking_times = Recipe.objects.values('difficulty').annotate(avg_time=Avg('cooking_time')).order_by('difficulty')
    plt.figure(figsize=(10, 5))
    plt.plot([diff['difficulty'] for diff in avg_cooking_times], [diff['avg_time'] for diff in avg_cooking_times], marker='o')
    plt.title('Average Cooking Time by Difficulty')
    plt.xlabel('Difficulty')
    plt.ylabel('Average Cooking Time (minutes)')
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    
    plt.close()
    return graphic