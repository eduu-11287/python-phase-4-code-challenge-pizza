from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants]), 200

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404

    # Include nested restaurant_pizzas and their pizzas
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

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404
    db.session.delete(restaurant)
    db.session.commit()
    return make_response('', 204)

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas]), 200

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()

    try:
        new_restaurant_pizza = RestaurantPizza(
            price=data['price'],
            restaurant_id=data['restaurant_id'],
            pizza_id=data['pizza_id']
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()
    except ValueError:
        # Update the error message to match the test case
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

if __name__ == "__main__":
    app.run(port=5555, debug=True)