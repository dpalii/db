from consolemenu import SelectionMenu

from model import Model
from view import View


TABLES_NAMES = ['creatures', 'families', 'ingredients', 'potions', 'potion_against_creature', 'potion_ingredient']

TABLES = {
    'creatures': ['id', 'family_id', 'name', 'description'],
    'families': ['id', 'name', 'description'],
    'ingredients': ['id', 'name', 'in_inventory'],
    'potions': ['id', 'duration', 'effect', 'name'],
    'potion_against_creature': ['id', 'potion_id', 'creature_id'],
    'potion_ingredient': ['id', 'potion_id', 'ingredient_id']
}


def get_input(msg, table_name=''):
    print(msg)
    if table_name:
        print(' | '.join(TABLES[table_name]), end='\n\n')
    return input()


def get_insert_input(msg, table_name):
    print(msg)
    print(' | '.join(TABLES[table_name]), end='\n\n')
    return input(), input()


def press_enter():
    input()


class Controller:
    def __init__(self):
        self.model = Model()
        self.view = View()

    def show_init_menu(self, msg=''):
        selection_menu = SelectionMenu(TABLES_NAMES + ['Find text where word is not included',
                                                       'Find text by full phrase',
                                                       'Find ingredients by potion effects',
                                                       'Fill table "potions" with random data'],
                                       title='Select the table to work with | command:',
                                       subtitle=msg)
        selection_menu.show()

        index = selection_menu.selected_option
        if index < len(TABLES_NAMES):
            table_name = TABLES_NAMES[index]
            self.show_entity_menu(table_name)
        elif index == len(TABLES_NAMES):
            self.fts_without_word()
        elif index == len(TABLES_NAMES) + 1:
            self.fts_phrase()
        elif index == len(TABLES_NAMES) + 2:
            self.search_ingredients_by_potion_effects()
        elif index == len(TABLES_NAMES) + 3:
            self.fill_by_random()
        else:
            print('Goodbye!')

    def show_entity_menu(self, table_name, msg=''):
        options = ['Get', 'Delete', 'Update', 'Insert']
        functions = [self.get, self.delete, self.update, self.insert]

        selection_menu = SelectionMenu(options, f'Name of table: {table_name}',
                                       exit_option_text='Back',
                                       subtitle=msg)
        selection_menu.show()
        try:
            function = functions[selection_menu.selected_option]
            function(table_name)
        except IndexError:
            self.show_init_menu()

    def get(self, table_name):
        try:
            condition = get_input(f'GET {table_name}\nEnter condition (SQL) or leave empty:', table_name)
            data = self.model.get(table_name, condition)
            self.view.print(data)
            press_enter()
            self.show_entity_menu(table_name)
        except Exception as err:
            self.show_entity_menu(table_name, str(err))

    def insert(self, table_name):
        try:
            columns, values = get_insert_input(f"INSERT {table_name}\nEnter columns divided with commas, then do the same for values in format: ['value1', 'value2', ...]",
                                               table_name)
            self.model.insert(table_name, columns, values)
            self.show_entity_menu(table_name, 'Insert is successful!')
        except Exception as err:
            self.show_entity_menu(table_name, str(err))

    def delete(self, table_name):
        try:
            condition = get_input(f'DELETE {table_name}\n Enter condition (SQL):', table_name)
            self.model.delete(table_name, condition)
            self.show_entity_menu(table_name, 'Delete is successful')
        except Exception as err:
            self.show_entity_menu(table_name, str(err))

    def update(self, table_name):
        try:
            condition = get_input(f'UPDATE {table_name}\nEnter condition (SQL):', table_name)
            statement = get_input("Enter SQL statement in format [<key>='<value>']", table_name)

            self.model.update(table_name, condition, statement)
            self.show_entity_menu(table_name, 'Update is successful')
        except Exception as err:
            self.show_entity_menu(table_name, str(err))

    def search_ingredients_by_potion_effects(self):
        try:
            effect = get_input('Search ingredients where potion\'s effect is: \nEnter effect:')
            data = self.model.search_ingredients_by_potion_effect(effect)
            self.view.print(data)
            press_enter()
            self.show_init_menu()
        except Exception as err:
            self.show_init_menu(str(err))

    def fts_without_word(self):
        try:
            word = get_input('Enter word:')
            data = self.model.fts_without_word(word)
            self.view.print(data)
            press_enter()
            self.show_init_menu()
        except Exception as err:
            self.show_init_menu(str(err))

    def fts_phrase(self):
        try:
            phrase = get_input('Enter phrase:')
            data = self.model.fts_phrase(phrase)
            self.view.print(data)
            press_enter()
            self.show_init_menu()
        except Exception as err:
            self.show_init_menu(str(err))

    def fill_by_random(self):
        amount = int(get_input('Enter the amount of entries to be generated:'))
        try:
            self.model.fill_potions_by_random_data(amount)
            self.show_init_menu(f'Generated successfully')

        except Exception as err:
            self.show_init_menu(str(err))
