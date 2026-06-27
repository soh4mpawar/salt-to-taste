import os
from PIL import Image, ImageDraw, ImageFont

img_dir = "tests/test_images"
os.makedirs(img_dir, exist_ok=True)

try:
    font = ImageFont.truetype("arial.ttf", 20)
except:
    font = ImageFont.load_default()

def create_image(filename, text, size=(600, 400), bg_color="white", text_color="black"):
    img = Image.new("RGB", size, color=bg_color)
    d = ImageDraw.Draw(img)
    d.text((20, 20), text, fill=text_color, font=font)
    img.save(os.path.join(img_dir, filename))

webpage_text = """Garlic Bread Recipe

Ingredients:
- 1 loaf French bread
- 1/2 cup butter
- 3 cloves garlic, minced
- 1 tbsp parsley
- salt to taste

Directions:
1. Slice bread.
2. Mix butter, garlic, parsley.
3. Spread on bread and bake at 350F for 10 min."""
create_image("recipe_webpage_screenshot.png", webpage_text, bg_color="#f0f8ff")

cookbook_text = """CHICKEN SOUP
Serves 6

Ingredients:
* 1 whole chicken
* 2 carrots, chopped
* 2 celery stalks
* 1 onion
* 2 tsp kosher salt (Morton)
* 8 cups water

Instructions:
Simmer all ingredients in a large pot for 2 hours."""
create_image("cookbook_page_photo.jpg", cookbook_text, bg_color="#fffdd0")

typed_text = """SCRAMBLED EGGS

2 eggs
1 tbsp butter
Pinch of salt

Whisk eggs. Melt butter. Cook eggs."""
create_image("typed_recipe.png", typed_text)
