from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app, storage, auth
import os.path

cred = credentials.Certificate("kazumirecipekey.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'kazumirecipe.appspot.com'})
bucket = storage.bucket()
app = Flask(__name__)
# cors = CORS(app, origins=["https://www.kazumirecipe.com", "https://kazumirecipe.com", "http://kazumirecipe.com", "http://www.kazumirecipe.com"])
cors = CORS(app)
db = firestore.client()
recipe_ref = db.collection('recipes')


@app.route('/', methods=['GET'])
def recipes():
    recipes = []
    recipes_data = list(recipe_ref.get())
    for recipe in recipes_data:
        recipes.append(recipe.to_dict())

    return jsonify(data=recipes)


# checks if the submitted username and password belongs to admin user
@app.route('/login', methods=['POST'])
def login():
    admin_ref = db.collection('admins')
    admin_list = list(admin_ref.get())
    username = request.form.get('username')
    password = request.form.get('password')
    for admin in admin_list:
        if username == admin.get('username') and password == admin.get('password'):
            uid = username
            token = auth.create_custom_token(uid)
            return jsonify(isAdmin=True, token=token.decode('utf-8'))
    return jsonify(isAdmin=False)


# form keys: name, image, directions (array), ingredients (array)
# adds recipe to database if the image is valid and the recipe is not already on the database
@app.route('/addRecipe', methods=['POST'])
def add_recipe():
    test_mode = False
    name = request.form.get('name')
    image = request.files['image']
    directions = request.form.getlist('directions')
    ingredients = request.form.getlist('ingredients')
    image_name = image.filename
    extension = os.path.splitext(image_name)[1]
    if extension in ['.jpg', '.jpeg', '.png'] and is_new_recipe(name) and not test_mode:
        blob = bucket.blob(image_name)
        blob.upload_from_file(image, content_type=('image/' + extension[1:]))
        blob.make_public()
        recipe_ref.add({'name': name, 'image': blob.public_url, 'directions': directions, 'ingredients': ingredients})
        return jsonify(message=('recipe added: ' + name)), 200
    return jsonify(message='Recipe not uploaded'), 400


# returns True if the recipe name is not in Firestore
def is_new_recipe(name):
    query = recipe_ref.where('name', '==', name)
    total = 0
    for repeat in query.stream():
        total += 1
    if total == 0:
        return True
    return False


if __name__ == '__main__':
    app.run()