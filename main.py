from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app



cred = credentials.Certificate("kazumirecipekey.json")
firebase_admin.initialize_app(cred)

app = Flask(__name__)
# app.route('/addRecipe', methods='POST')

db = firestore.client()

recipe_ref = db.collection('recipes')


@app.route('/', methods=['GET'])
def recipes():
    recipes = []
    recipes_data = list(recipe_ref.get())
    for recipe in recipes_data:
        recipes.append(recipe.to_dict())

    return jsonify(data=recipes)


if __name__ == '__main__':
    app.run()