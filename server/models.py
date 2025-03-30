from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    restaurant_pizzas = relationship('RestaurantPizza', back_populates='restaurant', cascade='all, delete-orphan')
    # add serialization rules
    serialize_rule = ('-restaurant_pizzas.restaurant',)

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship
    restaurant_pizzas = relationship('RestaurantPizza', back_populates='pizza', cascade='all, delete-orphan')

    # add serialization rules
    serialize_rule = ('-restaurant_pizzas.pizza',)
    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # add relationships
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)

    restaurant = relationship('Restaurant', back_populates='restaurant_pizzas')
    pizza = relationship('Pizza', back_populates='restaurant_pizzas')

    # add serialization rules

    serialize_rule = ('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas')


    # add validation
  
    @validates('price')
    def validate_price(self, key, value):
        if value < 1 or value > 30:
            raise ValueError ("validation error: price must be between 1 to 30")
        return value



    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"


