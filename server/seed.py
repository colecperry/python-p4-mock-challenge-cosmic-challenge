from random import randint, choice as rc

from faker import Faker

from app import app
from models import db, Planet, Scientist, Mission

fake = Faker()



def create_scientists():
    scientists = []
    for _ in range(100):
        s = Scientist(
            name=fake.name(),
            field_of_study=fake.sentence(),
            avatar=fake.sentence()
        )
        scientists.append(s)

    return scientists

def create_missions(scientists, planets):
    missions = []
    for _ in range(100):
        m = Mission(
            name=fake.name(),
            scientist_id=rc([scientist.id for scientist in scientists]),
            planet_id=rc([planet.id for planet in planets]),
        )
        missions.append(m)

    return missions

def create_planets():
    planets = []
    for _ in range(100):
        p = Planet(
            name=fake.name(),
            distance_from_earth=fake.sentence(),
            nearest_star=fake.name()
        )
        planets.append(p)

    return planets


if __name__ == '__main__':

    with app.app_context():
        print("Clearing db...")
        Planet.query.delete()
        Scientist.query.delete()
        Mission.query.delete()

        print("Seeding scientists...")
        scientists = create_scientists()
        db.session.add_all(scientists)
        db.session.commit()

        print("Seeding planets...")
        planets = create_planets()
        db.session.add_all(planets)
        db.session.commit()

        print("Seeding missions...")
        missions = create_missions(scientists, planets)
        db.session.add_all(missions)
        db.session.commit()

        print("Done seeding!")