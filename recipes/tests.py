from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Recipe
from django.contrib.auth.models import User
import uuid

class RecipeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user
        test_user = User.objects.create_user(username='testuser', password='12345')
        
        Recipe.objects.create(
            name="Test Recipe",
            cooking_time=30,
            ingredients="Ingredient 1, Ingredient 2",
            instructions="This is a test recipe description.",
            difficulty="Easy",
            author=test_user
        )

    def test_recipe_creation(self):
        recipe = Recipe.objects.get(name="Test Recipe")
        self.assertTrue(isinstance(recipe, Recipe))
        self.assertEqual(str(recipe), recipe.name)

    def test_name_max_length(self):
        recipe = Recipe.objects.get(name="Test Recipe")
        max_length = recipe._meta.get_field('name').max_length
        self.assertEqual(max_length, 100)  # Updated to match the new max_length

    def test_cooking_time_help_text(self):
        recipe = Recipe.objects.get(name="Test Recipe")
        help_text = recipe._meta.get_field('cooking_time').help_text
        self.assertEqual(help_text, "in minutes")  # Updated to match the new help_text

    def test_recipe_ordering(self):
        Recipe.objects.create(
            name="Another Recipe",
            cooking_time=45,
            ingredients="Ingredient 3, Ingredient 4",
            instructions="Another test recipe.",
            difficulty="Medium"
        )
        recipes = Recipe.objects.all()
        self.assertEqual(recipes[0].name, "Another Recipe")
        self.assertEqual(recipes[1].name, "Test Recipe")

    def test_recipe_fields(self):
        recipe = Recipe.objects.get(name="Test Recipe")
        self.assertEqual(recipe.name, "Test Recipe")
        self.assertEqual(recipe.cooking_time, 30)
        self.assertEqual(recipe.ingredients, "Ingredient 1, Ingredient 2")
        self.assertEqual(recipe.instructions, "This is a test recipe description.")
        self.assertEqual(recipe.difficulty, "Easy")

    def test_blank_name(self):
        with self.assertRaises(ValidationError):
            recipe = Recipe(
                name="",
                cooking_time=30,
                ingredients="Test",
                instructions="Test",
                difficulty="Easy"
            )
            recipe.full_clean()

    def test_uuid_primary_key(self):
        recipe = Recipe.objects.get(name="Test Recipe")
        self.assertIsInstance(recipe.id, uuid.UUID)

    def test_author_relationship(self):
        recipe = Recipe.objects.get(name="Test Recipe")
        self.assertEqual(recipe.author.username, "testuser")

    def test_difficulty_choices(self):
        recipe = Recipe.objects.get(name="Test Recipe")
        self.assertIn(recipe.difficulty, dict(Recipe.DIFFICULTY_CHOICES))

    def test_get_absolute_url(self):
        recipe = Recipe.objects.get(name="Test Recipe")
        expected_url = f'/recipes/{recipe.id}/'
        self.assertEqual(recipe.get_absolute_url(), expected_url)

    def test_calculate_difficulty(self):
        recipe = Recipe.objects.create(
            name="Easy Recipe",
            cooking_time=5,
            ingredients="Ingredient 1, Ingredient 2",
            instructions="Easy instructions",
            difficulty="Easy"
        )
        self.assertEqual(recipe.calculate_difficulty(), "Easy")

        recipe = Recipe.objects.create(
            name="Hard Recipe",
            cooking_time=60,
            ingredients="Ingredient 1, Ingredient 2, Ingredient 3, Ingredient 4, Ingredient 5",
            instructions="Hard instructions",
            difficulty="Hard"
        )
        self.assertEqual(recipe.calculate_difficulty(), "Hard")

    # New test for image field
    def test_image_upload(self):
        recipe = Recipe.objects.get(name="Test Recipe")
        self.assertEqual(recipe.image.name, 'default_recipe.jpg')

    # Modified test for auto-increment (now testing UUID)
    def test_uuid_generation(self):
        recipe1 = Recipe.objects.get(name="Test Recipe")
        recipe2 = Recipe.objects.create(
            name="Second Recipe",
            cooking_time=45,
            ingredients="Ingredient 5, Ingredient 6",
            instructions="Second test recipe instructions.",
            difficulty="Medium"
        )
        self.assertNotEqual(recipe1.id, recipe2.id)
        self.assertIsInstance(recipe1.id, uuid.UUID)
        self.assertIsInstance(recipe2.id, uuid.UUID)