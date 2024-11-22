import re
from prettytable import PrettyTable

tables = {}
command_parsers = {
    "CREATE": lambda cmd: ("CREATE", re.match(r"CREATE (\w+)\s*\((.+)\);", cmd).groups()),
    "INSERT": lambda cmd: ("INSERT", re.match(r"INSERT\s+(?:INTO\s+)?(\w+)\s*\((.+)\);", cmd).groups()),
    "SELECT": lambda cmd: ("SELECT", re.match(
        r"SELECT FROM (\w+)\s*(?:FULL_JOIN (\w+ ON \w+ = \w+))?\s*(?:WHERE (.+))?;", cmd
    ).groups())
}



def create_table(params):
    name, columns= params
    columns = [col.split()[0] for col in columns.split(",")]
    if name in tables:
        return "Помилка, таблиця з цією назвою вже існує :("
    tables[name] = {"columns": columns, "data": []}
    return f"Створена таблиця {name}:)"


def insert_into_table(params):
    name, value= params
    if name not in tables:
        return f"Помилка:( {name} такої таблиці не існує"
    value = [v.strip('"') for v in value.split(", \"")]
    if len(value)!= len(tables[name]["columns"]):
        return "Помилка кількість стовпчиків в створеній таблиці і при заповнені таблиці відрізняется:("
    tables[name]["data"].append(value)
    return f"Один рядок додан в таблицю {name}:)"

def select_from_table(params):
    name1, join_clause, where_clause = params
    if name1 not in tables:
        return f"Error: Table {name1} does not exist."
    columns = tables[name1]["columns"]
    rows = tables[name1]["data"]

    if join_clause:
        match = re.match(r"(\w+)\s* ON \s*(\w+)\s*=\s*(\w+)", join_clause)
        if not match:
            return "Помилка при вводі команди"
        name2, t1_col, t2_col = match.groups()


        if name2 not in tables:
            return f"Помилка таблиці з назвою {name2} не існує"
        

        if t1_col not in columns or t2_col not in tables[name2]["columns"]:
            return f"Помилка зі стовпчиками в таблицях"
        
        col_id1=columns.index(t1_col)
        col_id2=tables[name2]["columns"].index(t2_col)
        
        merged_rows = []
        for row1 in rows:
            found_match = False
            for row2 in tables[name2]["data"]:
                if row1[col_id1] == row2[col_id2]:
                    merged_rows.append(row1+row2)
                    found_match = True
            if not found_match:
                merged_rows.append(row1+[" "] * len(tables[name2]["columns"]))

        
        for row2 in tables[name2]["data"]:
            found_match = False
            for row1 in rows:
                if row1[col_id1] == row2[col_id2]:
                    found_match = True
                    break
            if not found_match:
                merged_rows.append([" "] * len(columns) + row2)


        columns = columns +tables[name2]["columns"]
        rows = merged_rows

    if where_clause:
       column, value = re.match(r"(\w+)\s*=\s*\"(.+)\"", where_clause).groups()
       if column not in columns:
            return f"Помилка стовчика {column} не існує {name1}."
       col_idx = columns.index(column)
       rows = [row for row in rows if row[col_idx] == value]

    table = PrettyTable(columns)
    for row in rows:
        table.add_row(row)
    return str(table) 


command_handlers = {
    "CREATE": create_table,
    "INSERT": insert_into_table,
    "SELECT": select_from_table,
}

def main():
    while True:
        command = input("Введіть команду: ").strip()
        command = command.replace("“", '"').replace("”", '"')

        for cmd_type, parser in command_parsers.items():
            if command.startswith(cmd_type):
                cmd_data = parser(command)
                action, params = cmd_data
                result = command_handlers[action](params)
                print(result)
                break
        else:
            print("Такої команди не існує або введена не коректно")

       

if __name__ == "__main__":
    main()
