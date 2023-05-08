from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
  "ix": "ix_%(column_0_label)s",
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    field_of_study = db.Column(db.String)
    avatar = db.Column(db.String)

    # Step 3: According to the README, a scientist has many missions, and has many planets through missions
    # Create the variables for the Scientist class - "missions" and "planets." Now link the Scientist and Mission classes
    # through db.relationship. For "Scientist.missions," point to the Mission class and back_populate with the
    # inverse relationship, the scientist variable in the Mission class
    # Step 6: Since a scientist has many planets through missions, and there is no scientist_id variable in the planets
    # class, we must use association_proxy to go through the missions table to get the scientist's planets. We create a 
    # variable planets, and reference our "missions" relationship which allows us to get to the missions table, and then
    # we need to reference our "planet" relationship which allows us to get from missions to our planets table
    missions = db.relationship("Mission", back_populates='scientist')
    planets = association_proxy("missions", "planet")

    # Step 7: For serialize rules, simply wite each relationship variable name from the current class you are in, and
    # then (.) the variable that corresponds to the current class you are in (can be plural or not plural)
    serialize_rules = ('-missions.scientist', '-planets.scientists', '-created_at', '-updated_at')

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    @validates('name')
    # Add validation the scientist must have a name
    # Add validation name's must be unique - included in column name, unique=True
    def validate_name(self, key, name):
        if name:
            return name
        raise ValueError("Name field is required")
    
    @validates('field_of_study')
    # Add validation the scientist must have a field_of_study
    def validate_field_of_study(self, key, field_of_study):
        if field_of_study:
            return field_of_study
        raise ValueError("Field of Study is required")

class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Step 1: Add Foreign Keys to the middle/through table
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))

    # Step 2: Start writing variables based on the README: in this example,
    # a mission belongs to a scientist, and belongs to a planet, so the
    # variables would be "scientist" and "planet" (Mission.scientist), (Mission.planet)
    # Step 4: For the inverse relationship "Mission.scientist," point towards the Scientist class
    # and backpopulate with the inverse relationship variable from the Scientist class, "missions"
    # Step 5: Repeat this process for relationships between the Mission and Planet classes
    scientist = db.relationship("Scientist", back_populates='missions')
    planet = db.relationship("Planet", back_populates='missions')

    serialize_rules = ('-scientist.missions', '-planet.missions', '-created_at', '-updated_at')

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    @validates('name')
    # Add validation the mission must have a name
    def validate_name(self, key, name):
        if name:
            return name
        raise ValueError('Mission must have name.')
    
    @validates('scientist_id')
    # Add validation the mission must have a scientist_id
    def validate_name(self, key, scientist_id):
        if scientist_id:
            return scientist_id
        raise ValueError('Mission must have scientist ID.')
    
    @validates('planet_id')
    # Add validation the mission must have a planet_id
    def validate_name(self, key, planet_id):
        if planet_id:
            return planet_id
        raise ValueError('Mission must have planet ID.')

class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.String)
    nearest_star = db.Column(db.String)
    image = db.Column(db.String)

    missions = db.relationship("Mission", back_populates='planet')
    scientists = association_proxy("missions", "scientist")

    serialize_rules = ('-missions.planet', '-scientists.planets', '-created_at', '-updated_at')

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

# add any models you may need. 