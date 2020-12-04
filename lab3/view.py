class View:
    def print(self, data):
        columns, rows = data

        line_len = 30 * len(columns)
        self.print_separator(line_len)
        self.print_columns(columns)
        self.print_separator(line_len)

        for row in rows:
            self.print_row(vars(row), columns)
        self.print_separator(line_len)

    def print_columns(self, columns):
        for col in columns:
            print(str(col).rjust(26, ' ') + '   |', end='')
        print('')

    def print_row(self, row, columns):
        for col in columns:
            print(str(row[col]).rjust(26, ' ') + '   |', end='')
        print('')

    def print_separator(self, length):
        print('-' * length)
