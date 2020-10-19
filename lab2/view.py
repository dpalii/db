class View:
    def print(self, data):
        if len(data) == 3:
            columns, rows, time = data
        else:
            columns, rows = data

        line_len = 30 * len(columns)
        self.print_separator(line_len)
        self.print_row(columns)
        self.print_separator(line_len)

        for row in rows:
            self.print_row(row)
        self.print_separator(line_len)
        if len(data) == 3:
            print(f'Execution time: {time}ms')
            self.print_separator(line_len)

    def print_row(self, row):
        for col in row:
            print(str(col).rjust(26, ' ') + '   |', end='')
        print('')

    def print_separator(self, length):
        print('-' * length)
