#!/usr/bin/env python3

# make sure to import make_response and request from flask
from flask import Flask, make_response, request
from flask_migrate import Migrate

# Make sure to import your models and db from models.py
from models import db, Scientist, Mission, Planet

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return ''

@app.route('/scientists', methods=['GET', 'POST'])
# /scientists route GET scientists
def scientists():
    if request.method == 'GET':
        scientists = Scientist.query.all()


        scientists_dict = [scientist.to_dict(rules=("-planets", "-missions")) for scientist in scientists]
        # ^ Right off the bat, include the serialize rules for the relationship variables for the Scientist class,
        # "missions" and "planets" to avoid recursion error

        return scientists_dict, 200
    
    elif request.method == 'POST':
    # /scientists route - POST
        form_data = request.get_json()
        # ^ Since we are posting in Postman using raw JSON, use "request.get_json" to extract the JSON data submitted in the request

        # Use the JSON data to create a new scientist instance in the Scientist class, pulling fields from the request object
        try:
            scientist = Scientist(name=form_data.get('name'), field_of_study=form_data["field_of_study"], avatar=form_data.get('avatar'))
            db.session.add(scientist)
            db.session.commit()
            return scientist.to_dict(rules=("-planets", "-missions")), 201
        # ^ Use rules to return only return scientists, not scientist's planets and missions

        except ValueError as err:
            return {'error': '400: Validation Error'}, 400
        # ^ This error only returns if you hit a validation error in the Scientist class, i.e. "scientist must have a name"

@app.route('/scientists/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def scientists_by_id(id):
    #/scientists/id route for GET scientists by ID

    if request.method == 'GET':
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if scientist:
            missions_dict = [mission.to_dict(rules=('-planet', '-scientist')) for mission in scientist.missions if mission]
            # ^If a scientist exists with the passed in ID, return an array of missions for each scientist
            # Using scientists relationship variable "scientist.missions," iterate over each mission and return as a dict

            scientist_dict = {
                "id":scientist.id,
                "name":scientist.name,
                "field_of_study":scientist.field_of_study,
                "avatar":scientist.avatar,
                "missions":missions_dict,
            }
            # ^ Manually build out your scientist dictionary for your JSON response including the scientist fields and missions_dict
            response = make_response(scientist_dict, 200)
            return response
        else:
            return {"error": '404: Scientist not found'}, 404
        
    elif request.method == 'PATCH':
        #/scientists/id route for PATCH
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if scientist:
            try:
                form_data = request.get_json()
                for attr in form_data:
                    setattr(scientist, attr, form_data.get(attr))
                    # ^ If a scientist with a matching ID exists, return the JSON from the PATCH request, iterate over each attribute, setattr() is used to set the new value for each attribute of the 'scientist' object. The third argument in setattr() is the value to set the attribute to

                db.session.add(scientist)
                db.session.commit()

                scientist_dict = scientist.to_dict(rules=('-missions', '-planets'))

                response = make_response(
                    scientist_dict,
                    202
                )

                return response
            except: 
                return {"error": '400: Validation error'}, 400
                # ^ If the scientist if not updated successfully or hits a validation error
        return {"error": 'Scientist not found'}, 400
        # ^ If there is no scientist with the matching id found
            

    elif request.method == 'DELETE':
    #/scientists/id route for DELETE
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            db.session.delete(scientist)
            db.session.commit()
            return {"message": "Scientist successfully deleted"}, 204
        return {"error": "404: Scientist not found"}, 404
        # ^ If the scientist is successfully deleted return 204, if the passed in ID doesn't match return 404
    
@app.route('/planets', methods=['GET'])
#/planets route for GET
def planets():
    planets = Planet.query.all()
    planets_dict = [planet.to_dict(rules=("-missions", "-scientists", "-updated_at", "-created_at")) for planet in planets]

    response = make_response(
        planets_dict,
        200
    )

    return response

@app.route('/missions', methods=['POST'])
#/missions route for POST
# If created successfully, return a response with the planet associated with the new mission
def missions():
    form_data = request.get_json()
    # ^ Return the JSON from the POST request and set to variable form_data
    try:
        mission = Mission(
            name=form_data.get('name'), 
            scientist_id=form_data.get('scientist_id'),
            planet_id=form_data.get('planet_id'))
        # ^ Use the JSON data to create a new mission instance in the Mission class, pulling in new fields from the request object form_data
        db.session.add(mission)
        db.session.commit()
        return mission.planet.to_dict(rules=("-missions", "-scientists")), 201
        # Instead of returning the new mission, we want to return the newly created mission's planets
    except:
        return {"error": '400: Validation error'}, 400


if __name__ == '__main__':
    app.run(port=5555, debug=True)
