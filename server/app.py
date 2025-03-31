# importing modules from the project directory
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
import os

# difining the base directory and the data base url
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__) # a flask application instance

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE # cofiguring the database 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # THIS disables the sqlalchemy modification tracking
app.json.compact = False # this sets the json output be more compact

migrate = Migrate(app, db) # this initializes flask migrate extention
db.init_app(app) # initializes sqlalchemy with the flask application

# aplication routes 
@app.route('/restaurants', methods=['GET']) # route with the method 
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants]), 200 #converts each restaurant object to a dict and return a json

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404

    restaurant_data = {
        'id': restaurant.id,
        'name': restaurant.name,
        'address': restaurant.address,
        'restaurant_pizzas': [
            {
                'id': rp.id,
                'price': rp.price,
                'pizza': {
                    'id': rp.pizza.id,
                    'name': rp.pizza.name,
                    'ingredients': rp.pizza.ingredients
                }
            }
            for rp in restaurant.restaurant_pizzas
        ]
    }

    return jsonify(restaurant_data), 200


# route for deleting restaurant with id
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404
    db.session.delete(restaurant)
    db.session.commit()
    return make_response('', 204)

# route for geting all pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas]), 200


# route for creating new restaurant_pizza
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()

    try: #create new restaurant with the data
        new_restaurant_pizza = RestaurantPizza(
            price=data['price'],
            restaurant_id=data['restaurant_id'],
            pizza_id=data['pizza_id']
        ) # commiting to a database
        db.session.add(new_restaurant_pizza)
        db.session.commit()
    except ValueError:

        return jsonify({"errors": ["validation errors"]}), 400

    restaurant_pizza_data = {
        'id': new_restaurant_pizza.id,
        'price': new_restaurant_pizza.price,
        'restaurant_id': new_restaurant_pizza.restaurant_id,
        'pizza_id': new_restaurant_pizza.pizza_id,
        'restaurant': {
            'id': new_restaurant_pizza.restaurant.id,
            'name': new_restaurant_pizza.restaurant.name,
            'address': new_restaurant_pizza.restaurant.address
        },
        'pizza': {
            'id': new_restaurant_pizza.pizza.id,
            'name': new_restaurant_pizza.pizza.name,
            'ingredients': new_restaurant_pizza.pizza.ingredients
        }
    }

    return jsonify(restaurant_pizza_data), 201

# running the flask app
if __name__ == "__main__":
    app.run(port=5555, debug=True)