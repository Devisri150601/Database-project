import csv

column_names = []
data = []
functional_dependencies = {
    # "StudentId": ["FirstName", "LastName"],
    # "Course": ["CourseStart", "CourseEnd", "ClassRoom"],
    # "Professor": ["ClassRoom", "ProfessorEmail"]
}
multi_valued_dependencies = {}
# composite_key = ["StudentId", "Course"]
composite_key = []

table_definitions = {}
dependenciesMap = {}
bcnfremovedItems = []



def input_parser():
    # Read the CSV file and extract column names and data
    file_name = input("Input Dataset: ")
    with open(file_name, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        column_names = next(csv_reader)  # Read the first row as column names
        for row in csv_reader:
            data.append(row)

    # Display the table with column names as headers and values
    print("Table:")
    for i in range(len(column_names)):
        print("{:<15}{}".format(column_names[i], [row[i] for row in data]))

    
    print("\nInput Functional Dependencies (type 'exit' and hit enter to complete your dependency list):")
    while True:
        dependency = input(">>> ")
        if dependency.lower() == 'exit':
            break

        # Split the input into left-hand side and right-hand side
        left, right = map(str.strip, dependency.split('->'))
        # Split the left-hand side into individual attributes
        left_attributes = [attr.strip() for attr in left.split(',')]
        right_attributes = [attr.strip() for attr in right.split(',')]
        # Accumulate values for left attribute if it already exists
        for left_attr in left_attributes:
            if left_attr in functional_dependencies:
                functional_dependencies[left_attr].extend(right_attributes)
            else:
                functional_dependencies[left_attr] = right_attributes[:]

    # Example of accessing the functional dependencies
    for left, rights in functional_dependencies.items():
        print(f"Left Attribute: {left}")
        print(f"Right Attribute(s): {', '.join(rights)}")

    
    # Input multi-valued dependencies
    print("\nInput Multi-valued Dependencies (type 'exit' and hit enter to complete your dependency list):")
    while True:
        dependency = input(">>> ")
        if dependency.lower() == 'exit':
            break
        # Split the input into left-hand side and right-hand side
        left, right = map(str.strip, dependency.split('->>'))
        # Split the left-hand side into individual attributes
        left_attributes = [attr.strip() for attr in left.split(',')]
        right_attributes = [attr.strip() for attr in right.split(',')]
        # Accumulate values for left attribute if it already exists
        for left_attr in left_attributes:
            if left_attr in multi_valued_dependencies:
                multi_valued_dependencies[left_attr].extend(right_attributes)
            else:
                multi_valued_dependencies[left_attr] = right_attributes[:]

    # Example of accessing the functional dependencies
    for left, rights in multi_valued_dependencies.items():
        print(f"Left Attribute: {left}")
        print(f"Right Attribute(s): {', '.join(rights)}")
    

    print("\nChoose the highest normal form to reach (1: 1NF, 2: 2NF, 3: 3NF, B: BCNF, 4: 4NF, 5: 5NF):")
    normalForm = input(">>> ")

    key_input = input("Key (can be composite): ")
    composite_key = [k.strip() for k in key_input.split(',')]
    
    return normalForm, column_names, data, functional_dependencies, multi_valued_dependencies, composite_key

def is_1nf():
    # Check if the relation is in 1NF
    for key in functional_dependencies:
        if key not in column_names:
            return False
        for attr in functional_dependencies[key]:
            if attr not in column_names:
                return False
    return True

def is_2nf(functional_dependencies, composite_key):
    checkFor1NF = is_1nf()
    # Check for partial dependency
    # Create a set of all attributes in the composite key
    composite_attributes = set(composite_key)

    # Check for partial dependencies
    for key, values in functional_dependencies.items():
        if key in composite_attributes:
            for value in values:
                if value not in composite_attributes and dependenciesMap[value] == 1:
                    return False

    return checkFor1NF & True

def is_3nf(functional_dependencies, composite_key):
    checkFor2NF = is_2nf(functional_dependencies, composite_key)

    # Check for transitive dependencies
    for value in table_definitions['Details']:
        if value in dependenciesMap and dependenciesMap[value] == 1:
            return False
           
    return checkFor2NF & True

def is_bcnf(functional_dependencies, composite_key):
    checkfor3NF = is_3nf(functional_dependencies, composite_key)

    for value in table_definitions['Details']:
        if value in dependenciesMap and dependenciesMap[value] == 2:
            return False

    return checkfor3NF & True
            
def is_4nf(functional_dependencies, composite_key):
    checkfor3nf = is_3nf(functional_dependencies, composite_key)
    return checkfor3nf

def is_5nf(functional_dependencies, composite_key):
    checkfor4nf = is_4nf(functional_dependencies, composite_key)
    return checkfor4nf

def resolve_partial_dependencies(column_names, functional_dependencies, composite_key):
    normalized_tables = []
    all_columns = set(column_names)
    composite_attributes = set(composite_key)

    for key, values in functional_dependencies.items():
        tableValues = []
        if key in composite_attributes:
            all_columns.discard(key)
            create_table_sql = f"CREATE TABLE {key}Table ({key} (PRIMARY KEY)"
            for value in values:
                if dependenciesMap[value] == 1:
                    tableValues.append(value)
                    all_columns.discard(value)
                    attributes_str = f", {value}"
                    create_table_sql = f"{create_table_sql} {attributes_str}"
            create_table_sql = f"{create_table_sql})"
            normalized_tables.append(create_table_sql)
            table_definitions[key] = tableValues

    if (all_columns):
        create_table_sql = f"CREATE TABLE Details("
        tableValues = []
        for c_key in composite_attributes:
            tableValues.append(c_key)
            create_table_sql = f"{create_table_sql} {c_key} (COMPOSITE KEY),"
        
        for column in all_columns:
            tableValues.append(column)
            create_table_sql = f"{create_table_sql} {column}, "
        create_table_sql = f"{create_table_sql})"

    table_definitions['Details'] = tableValues
    normalized_tables.append(create_table_sql)

    return normalized_tables

def resolve_transitive_dependencies():    
    # Check for transitive dependencies
    for value in table_definitions['Details']:
        if value in dependenciesMap and dependenciesMap[value] == 1:
            table_definitions['Details'].remove(value)
            for key, values in functional_dependencies.items():
                for item in values:
                    if (item == value):
                        if key in table_definitions:
                            table_definitions[key] = table_definitions[key].append(value)
                        else:
                            table_definitions[key] = [value]

def resolve_bcnf_anomolies():
    for value in table_definitions['Details']:
        if value in dependenciesMap and dependenciesMap[value] == 2:
            table_definitions['Details'].remove(value)
            bcnfremovedItems.append(value)
    
    for value in bcnfremovedItems:
        key = value+'Details'
        newItem = []
        newItem.append(value)
        for v in composite_key:
            newItem.append(v)
        table_definitions[key] = newItem


def dependency_builder():
    for key, values in functional_dependencies.items():
        for value in values:
            if value in dependenciesMap:
                dependenciesMap[value] = dependenciesMap[value] + 1
            else:
                dependenciesMap[value] = 1

def sqlQueries():
    queries = []
    for key, values in table_definitions.items():
        if not 'Details' in key:
            create_table_sql = f"CREATE TABLE {key}Table ({key} (PRIMARY KEY)"
            for value in values:
                create_table_sql = f"{create_table_sql}, {value}"
            create_table_sql = f"{create_table_sql})"
            queries.append(create_table_sql)
    for key, values in table_definitions.items():
        create_table_sql = f"CREATE TABLE {key}("
        if 'Details' in key:
            for value in table_definitions[key]:
                create_table_sql = f"{create_table_sql} {value}"
                if value in composite_key:
                    create_table_sql = f"{create_table_sql} (COMPOSITE KEY)"
                create_table_sql = f"{create_table_sql},"
            create_table_sql = f"{create_table_sql})"
            queries.append(create_table_sql)
    return queries


if __name__ == "__main__":
    result = input_parser()
    normalForm = result[0]
    column_names = result[1]
    data = result[2] 
    functional_dependencies = result[3]
    multi_valued_dependencies = result[4]
    composite_key = result[5]

    
    dependency_builder()
    if normalForm == '1':
        if not is_1nf():
            print("The relation is not in 1NF")
        else:
            print("Relation is in 1NF")
        table_definitions['Details']=column_names
    elif normalForm == '2':
        table_definitions={}
        if not is_2nf(functional_dependencies, composite_key):
            print("The relation is not in 2NF")
            resolve_partial_dependencies(column_names, functional_dependencies, composite_key)
        else:
            print("The relation is in 1NF")
    elif normalForm == '3':
        resolve_partial_dependencies(column_names, functional_dependencies, composite_key)
        if not is_3nf(functional_dependencies, composite_key):
            print("The relation is not in 3NF")
            resolve_transitive_dependencies()
        else:
            print("The relation is in 3NF")
    elif normalForm == 'B':
        resolve_partial_dependencies(column_names, functional_dependencies, composite_key)
        resolve_transitive_dependencies()
        if not is_bcnf(functional_dependencies, composite_key):
            print("The relation is not in BCNF")
            resolve_bcnf_anomolies()
        else:
            print("The realtion is in BCNF")
    elif normalForm == '4':
        resolve_partial_dependencies(column_names, functional_dependencies, composite_key)
        resolve_transitive_dependencies()
        resolve_bcnf_anomolies()
        if not is_4nf(functional_dependencies, composite_key):
            print("The relation is not in 4NF")
        else:
            print("The realtion is in 4NF")
    elif normalForm == '5':
        resolve_partial_dependencies(column_names, functional_dependencies, composite_key)
        resolve_transitive_dependencies()
        resolve_bcnf_anomolies()
        if not is_5nf(functional_dependencies, composite_key):
            print("The relation is not in 5NF")
        else:
            print("The realtion is in 5NF")

    queries = sqlQueries()
    for query in queries:
        print(query)