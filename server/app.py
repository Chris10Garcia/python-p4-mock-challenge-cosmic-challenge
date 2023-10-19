#!/usr/bin/env python3
from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
import os
from flask_marshmallow import Marshmallow
from marshmallow import fields

from models import db, Planet, Scientist, Mission



BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
ma = Marshmallow(app)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return ''

class Scientist_Schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Scientist
        load_instance = True

    missions = fields.List(fields.Nested(lambda: Mission_Schema))


class Planet_Schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Planet
        load_instance = True

class Mission_Schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mission
        load_instance = True
        # include_relationships = True
    planet = fields.Nested(Planet_Schema)
    scientist_id = ma.auto_field()
    planet_id = ma.auto_field()


scientist_schema = Scientist_Schema()
scientists_schema = Scientist_Schema(many=True, exclude=("missions",))

planet_schema = Planet_Schema()
planets_schema = Planet_Schema(many=True)

mission_schema = Mission_Schema()
missions_schema = Mission_Schema(many=True)


class Scientist_Index(Resource):
    def get(self):
        scientists = Scientist.query.all()
        response = make_response(
            scientists_schema.dump(scientists),
            200
        )
        return response
    
    def post(self):
        data = request.get_json()

        try:
            new_scientist = Scientist(**data)
            db.session.add(new_scientist)
            db.session.commit()
            
            code = 201
            response = make_response(
                scientist_schema.dump(new_scientist)
            )
        except ValueError:
            code = 400
            response = make_response(
                {"errors": ["validation errors"]},
                code
            )
        finally:
            return response
    
class Scientist_By_ID(Resource):
    def get(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        response = make_response(
            scientist_schema.dump(scientist),
            200
        )
        return response

    def patch(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()

        if not scientist:
            return {"error": "Scientist not found"}, 404

        try:
            [setattr(scientist, attr, request.json[attr]) for attr in request.get_json()]
            db.session.add(scientist)
            db.session.commit()
            
            code = 202
            response = make_response(
                scientist_schema.dump(scientist),
                code
            )
        except ValueError:
            code = 400
            response = make_response(
                {"errors": ["validation errors"]},
                code
            )
        finally:
            return response

    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()

        if not scientist:
            return {"error": "Scientist not found"}, 404   

        db.session.delete(scientist)
        db.session.commit()
        return make_response({}, 204)
    
class Mission_Index(Resource):
    def get(self):
        missions = Mission.query.all()
        response = make_response(
            missions_schema.dump(missions),
            200
        )
        return response
    
    def post(self):
        data = request.get_json()
        print(data)
        try:
            new_mission = Mission(**data)
            db.session.add(new_mission)
            db.session.commit()

            # new_mission.scientist_id = data["scientist_id"]
            # new_mission.planet_id = data["planet_id"]

            # print(new_mission.planet_id)
            # db.session.add(new_mission)
            # db.session.commit()
            
            code = 201
            response = make_response(
                mission_schema.dump(new_mission),
                code
            )
        except ValueError:
            code = 400
            response = make_response(
                {"errors": ["validation errors"]},
                code
            )
        finally:
            return response

    
class Mission_By_ID(Resource):
    def get(self, id):
        mission = Mission.query.filter(Mission.id == id).first()
        response = make_response(
            mission_schema(mission),
            200
        )
        return response
    

class Planets_Index(Resource):
    def get(self):
        planets = Planet.query.all()
        response = make_response(
            planets_schema.dump(planets),
            200
        )
        return response
    
class Planets_By_ID(Resource):
    def get(self, id):
        planet = planet.query.filter(Planet.id == id).first()
        response = make_response(
            planet_schema(planet),
            200
        )
        return response
    

api.add_resource(Scientist_Index, "/scientists")
api.add_resource(Scientist_By_ID, "/scientists/<int:id>")

api.add_resource(Mission_Index, "/missions")
api.add_resource(Mission_By_ID, "/missions/<int:id>")

api.add_resource(Planets_Index, "/planets")
api.add_resource(Planets_By_ID, "/planets/<int:id>")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
