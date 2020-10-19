import psycopg2
import time


class Model:
    def __init__(self):
        try:
            self.connection = psycopg2.connect(host="localhost", port="5432",
                                               database='lab1', user='postgres', password='1111')
            self.cursor = self.connection.cursor()
        except (Exception, psycopg2.Error) as error:
            print("Помилка при з'єднанні з PostgreSQL", error)

    def get_col_names(self):
        return [d[0] for d in self.cursor.description]

    def create_db(self):
        f = open("create_db.txt", "r")

        self.cursor.execute(f.read())
        self.connection.commit()

    def get(self, tname, condition):
        try:
            query = f'SELECT * FROM {tname}'
            if condition:
                query += ' WHERE ' + condition

            self.cursor.execute(query)
            return self.get_col_names(), self.cursor.fetchall()
        finally:
            self.connection.commit()

    def insert(self, tname, columns, values):
        try:
            query = f'INSERT INTO {tname} ({columns}) VALUES ({values});'

            self.cursor.execute(query)
        finally:
            self.connection.commit()

    def delete(self, tname, condition):
        try:
            query = f'DELETE FROM {tname} WHERE {condition};'

            self.cursor.execute(query)
        finally:
            self.connection.commit()

    def update(self, tname, condition, statement):
        try:
            query = f'UPDATE {tname} SET {statement} WHERE {condition}'

            self.cursor.execute(query)
        finally:
            self.connection.commit()

    def search_ingredients_by_potion_effect(self, effect):
        try:
            query = f'''
            SELECT * from ingredients
            WHERE id in(
                SELECT ingredient_id FROM potion_ingredient
                JOIN potions on potion_ingredient.potion_id=potions.id
                WHERE LOWER(effect) LIKE '%{effect.lower()}%'
            );'''
            start = int(round(time.time() * 1000))
            self.cursor.execute(query)
            end = int(round(time.time() * 1000)) - start
            return self.get_col_names(), self.cursor.fetchall(), end
        finally:
            self.connection.commit()

    def fts_without_word(self, word):
        query = f'''
        select family_name, creature_name, creature_description 
        from (
        select
            f.name as family_name,
            creatures.name as creature_name,
            creatures.description as creature_description,
            to_tsvector(f.name) ||
            to_tsvector(creatures.name) ||
            to_tsvector(creatures.description) as document,
            to_tsquery('!{word}') as query
        from creatures
        join families f on creatures.family_id = f.id
        ) search
        where document @@ query;
        '''
        try:
            start = int(round(time.time() * 1000))
            self.cursor.execute(query)
            end = int(round(time.time() * 1000)) - start
            return self.get_col_names(), self.cursor.fetchall(), end
        finally:
            self.connection.commit()

    def fts_phrase(self, phrase):
        query = f'''
        select
        ts_headline(family_name, query, 'StartSel=\033[94m, StopSel=\033[0m') as family_name,
        ts_headline(creature_name, query, 'StartSel=\033[94m, StopSel=\033[0m') as creature_name,
        ts_headline(creature_description, query, 'StartSel=\033[94m, StopSel=\033[0m') as creature_description

        from (
        select
            f.name as family_name,
            creatures.name as creature_name,
            creatures.description as creature_description,
            to_tsvector(f.name) ||
            to_tsvector(creatures.name) ||
            to_tsvector(creatures.description) as document,
            phraseto_tsquery('{phrase}') as query
        from creatures
        join families f on creatures.family_id = f.id
        ) search
        where document @@ query;
        '''
        try:
            start = int(round(time.time() * 1000))
            self.cursor.execute(query)
            end = int(round(time.time() * 1000)) - start
            return self.get_col_names(), self.cursor.fetchall(), end
        finally:
            self.connection.commit()

    def fill_potions_by_random_data(self, amount):
        sql = f"""
        CREATE OR REPLACE FUNCTION randomPotions()
            RETURNS void AS $$
        DECLARE
            step integer  := 0;
        BEGIN
            LOOP EXIT WHEN step >= {amount};
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
            self.cursor.execute(sql)
        finally:
            self.connection.commit()
