from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)
# db = SQLAlchemy()

class Planet(db.Model):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship
    scientists = db.relationship("Scientist", secondary="missions", back_populates="planets")
    missions = db.relationship("Mission", back_populates="planet", overlaps="scientists", cascade="delete")
    # Add serialization rules

    # serialize_rules=('-scientists', "-missions",) #this is correct
    
class Scientist(db.Model):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    field_of_study = db.Column(db.String)

    # Add relationship

    planets = db.relationship("Planet", secondary="missions", back_populates="scientists", overlaps="missions")
    missions = db.relationship("Mission", back_populates="scientist", overlaps="planets,scientists", cascade="delete")
    # Add serialization rules

    # serialize_rules = ("-planets.scientists", "-missions.scientist",)
    # Add validation

    @validates("name")
    def test_name(self, key, address):
        if address == "" or address == None:
            raise ValueError("Please include name")
        return address
    
    @validates("field_of_study")
    def test_fod(self, key, address):
        if address == "" or address == None:
            raise ValueError("Please include field of study")
        return address
    


class Mission(db.Model):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    scientist_id = db.Column(db.Integer, db.ForeignKey("scientists.id"))
    planet_id = db.Column(db.Integer, db.ForeignKey("planets.id"))

    # Add relationships
    planet = db.relationship("Planet", back_populates="missions", overlaps="planets,scientists")
    scientist = db.relationship("Scientist", back_populates="missions", overlaps="planets,scientists")

    # Add serialization rules
    # serialize_rules = ("-planet.missions", "-scientist.missions")
    # Add validation

    @validates("name")
    def test_name(self, key, address):
        if address == "" or address == None:
            raise ValueError("Must provide Name")
        return address

    @validates("scientist_id")
    def test_scientist(self, key, address):
        if address == "" or address == None:
            raise ValueError("Must provide Scientist")
        return address
        
    @validates("planet_id")
    def test_planet(self, key, address):
        if address == "" or address == None:
            raise ValueError("Must provide Planet")
        return address

# add any models you may need.
