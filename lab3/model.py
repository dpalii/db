from sqlalchemy import create_engine, Column, Integer, Time, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

engine = create_engine('postgres://postgres:1111@localhost:5432/lab1')
Base = declarative_base()


TABLE_COLUMNS = {
    'creatures': ['id', 'family_id', 'name', 'description'],
    'families': ['id', 'name', 'description'],
    'ingredients': ['id', 'name', 'in_inventory'],
    'potions': ['id', 'duration', 'effect', 'name'],
    'potion_against_creature': ['id', 'potion_id', 'creature_id'],
    'potion_ingredient': ['id', 'potion_id', 'ingredient_id']
}


class PotionIngredient(Base):
    __tablename__ = 'potion_ingredient'

    id = Column(Integer, primary_key=True)
    potion_id = Column(Integer, ForeignKey('potions.id'))
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'))

    def __init__(self, potion_id=None, ingredient_id=None):
        self.potion_id = potion_id
        self.ingredient_id = ingredient_id


class PotionAgainstCreature(Base):
    __tablename__ = 'potion_against_creature'

    id = Column(Integer, primary_key=True)
    potion_id = Column(Integer, ForeignKey('potions.id'))
    creature_id = Column(Integer, ForeignKey('creatures.id'))

    def __init__(self, potion_id=None, creature_id=None):
        self.potion_id = potion_id
        self.creature_id = creature_id


class Creature(Base):
    __tablename__ = 'creatures'

    id = Column(Integer, primary_key=True)
    family_id = Column(Integer, ForeignKey('families.id'))
    name = Column(Text)
    description = Column(Text)

    potions_against_creatures = relationship(PotionAgainstCreature)

    def __init__(self, family_id=None, name=None, description=None):
        self.family_id = family_id
        self.name = name
        self.description = description


class Family(Base):
    __tablename__ = 'families'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    description = Column(Text)

    creatures = relationship('Creature')

    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description


class Ingredient(Base):
    __tablename__ = 'ingredients'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    in_inventory = Column(Integer)

    potions_ingredients = relationship(PotionIngredient)

    def __init__(self, name=None, description=None, in_inventory=None):
        self.name = name
        self.description = description
        self.in_inventory = in_inventory


class Potion(Base):
    __tablename__ = 'potions'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    effect = Column(Text)
    duration = Column(Time)

    potions_ingredients = relationship(PotionIngredient)
    potions_against_creatures = relationship(PotionAgainstCreature)

    def __init__(self, name=None, duration=None, effect=None):
        self.name = name
        self.duration = duration
        self.effect = effect


session = sessionmaker(engine)()
Base.metadata.create_all(engine)

TABLES = {
    'creatures': Creature,
    'potions': Potion,
    'ingredients': Ingredient,
    'families': Family,
    'potion_ingredient': PotionIngredient,
    'potion_against_creature': PotionAgainstCreature
}


class Model:
    def pairs_from_str(self, string):
        lines = string.split(',')
        pairs = {}

        for line in lines:
            key, value = line.split('=')
            pairs[key.strip()] = value.strip()
        return pairs

    def filter_by_pairs(self, query, pairs, cls):
        for key, value in pairs.items():
            field = getattr(cls, key)
            query = query.filter(field == value)
        return query

    def get(self, tname, condition):
        object_class = TABLES[tname]

        query = session.query(object_class)

        if len(condition) > 0:
            pairs = self.pairs_from_str(condition)
            query = self.filter_by_pairs(query, pairs, object_class)

        return query.all()

    def insert(self, tname, columns, values):
        columns = [c.strip() for c in columns.split(',')]
        values = [v.strip() for v in values.split(',')]

        pairs = dict(zip(columns, values))
        object_class = TABLES[tname]
        obj = object_class(**pairs)

        session.add(obj)

    def commit(self):
        session.commit()

    def delete(self, tname, condition):
        pairs = self.pairs_from_str(condition)
        object_class = TABLES[tname]

        objects = session.query(object_class)
        objects = self.filter_by_pairs(objects, pairs, object_class)

        objects.delete()

    def update(self, tname, condition, statement):
        pairs = self.pairs_from_str(condition)
        new_values = self.pairs_from_str(statement)
        object_class = TABLES[tname]

        objects = session.query(object_class)
        objects = self.filter_by_pairs(objects, pairs, object_class)

        for obj in objects:
            for field_name, value in new_values.items():
                setattr(obj, field_name, value)

    def fill_potions_by_random_data(self):
        sql = f"""
        CREATE OR REPLACE FUNCTION randomPotions()
            RETURNS void AS $$
        DECLARE
            step integer  := 0;
        BEGIN
            LOOP EXIT WHEN step >= 10000;
                INSERT INTO potions (name, effect, duration)
                VALUES (
                    substring(md5(random()::text), 1, 10),
                    substring(md5(random()::text), 1, 15),
                    (random() * (time '00:00:00' - time '23:59:59'))::time
                );
                step := step + 1;
            END LOOP ;
        END;
        $$ LANGUAGE PLPGSQL;
        SELECT randomPotions();
        """
        try:
            session.execute(sql)
        finally:
            session.commit()
