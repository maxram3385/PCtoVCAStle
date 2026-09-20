# Name: Max Ramos
# Date: 09/20/2026
# Assignment: Cassandra CRUD Application
# Purpose: Create a Python application that performs CRUD operations
# on an Amazon Cassandra database using review data from a JSON file.

import json
from cassandra.cluster import Cluster


# ---------------------------------------------------------
# CONNECT TO CASSANDRA
# ---------------------------------------------------------

print("Connecting to local Cassandra database...")

cluster = Cluster()
session = cluster.connect()


# ---------------------------------------------------------
# CREATE AMAZON KEYSPACE
# ---------------------------------------------------------

keyspace = '''
CREATE KEYSPACE IF NOT EXISTS Amazon
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};
'''

session.execute(keyspace)

# Connect to the Amazon keyspace
session.set_keyspace('amazon')


# ---------------------------------------------------------
# CREATE REVIEWS TABLE
# ---------------------------------------------------------

reviews_table = '''
CREATE TABLE IF NOT EXISTS Reviews (
    review_id text PRIMARY KEY,
    product_id text,
    reviewer_id text,
    stars int,
    review_body text,
    review_title text,
    product_category text
);
'''

session.execute(reviews_table)


# ---------------------------------------------------------
# CREATE PRODUCTCATEGORIES TABLE
# ---------------------------------------------------------

categories_table = '''
CREATE TABLE IF NOT EXISTS ProductCategories (
    product_id text,
    stars int,
    language text,
    product_category text,
    PRIMARY KEY ((product_category), stars, product_id)
);
'''

session.execute(categories_table)


# ---------------------------------------------------------
# IMPORT DATA FROM JSON FILE
# ---------------------------------------------------------

print("Importing data from JSON file...")

with open('dataset_en_dev.json', 'r') as file:

    for line in file:

        dataSet = json.loads(line)

        # Insert each JSON record into the Reviews table
        session.execute(
            '''
            INSERT INTO Reviews (
                review_id,
                product_id,
                reviewer_id,
                stars,
                review_body,
                review_title,
                product_category
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            ''',
            [
                dataSet["review_id"],
                dataSet["product_id"],
                dataSet["reviewer_id"],
                int(dataSet["stars"]),
                dataSet["review_body"],
                dataSet["review_title"],
                dataSet["product_category"]
            ]
        )

        # Insert each JSON record into the ProductCategories table
        session.execute(
            '''
            INSERT INTO ProductCategories (
                product_id,
                stars,
                language,
                product_category
            )
            VALUES (%s, %s, %s, %s);
            ''',
            [
                dataSet["product_id"],
                int(dataSet["stars"]),
                dataSet["language"],
                dataSet["product_category"]
            ]
        )


print("Data imported successfully!")


# ---------------------------------------------------------
# DISPLAY DISTINCT PRODUCT CATEGORIES
# ---------------------------------------------------------

def show_categories():

    print("\n--- DISTINCT PRODUCT CATEGORIES ---")

    try:

        results = session.execute(
            "SELECT DISTINCT product_category "
            "FROM ProductCategories;"
        )

        categories = sorted(
            row.product_category
            for row in results
        )

        for category in categories:
            print(category)

    except Exception as error:
        print("Unable to display categories:", error)


# ---------------------------------------------------------
# COUNT 4-STAR AND HIGHER REVIEWS
# ---------------------------------------------------------

def count_high_reviews():

    print("\n--- 4-STAR AND HIGHER REVIEWS ---")

    category = input(
        "Enter a product category: "
    ).strip().lower()

    query = '''
    SELECT COUNT(*)
    FROM Reviews
    WHERE product_category = %s
    AND stars >= 4
    ALLOW FILTERING;
    '''

    try:

        results = session.execute(
            query,
            [category]
        )

        count = results.one()[0]

        print(
            "\nNumber of 4-star and higher reviews for "
            + category
            + ": "
            + str(count)
        )

    except Exception as error:
        print("Unable to count reviews:", error)


# ---------------------------------------------------------
# COUNT 1-STAR REVIEWS
# ---------------------------------------------------------

def count_one_star_reviews():

    print("\n--- 1-STAR REVIEWS ---")

    category = input(
        "Enter a product category: "
    ).strip().lower()

    query = '''
    SELECT COUNT(*)
    FROM Reviews
    WHERE product_category = %s
    AND stars = 1
    ALLOW FILTERING;
    '''

    try:

        results = session.execute(
            query,
            [category]
        )

        count = results.one()[0]

        print(
            "\nNumber of 1-star reviews for "
            + category
            + ": "
            + str(count)
        )

    except Exception as error:
        print("Unable to count reviews:", error)


# ---------------------------------------------------------
# USER-ENTERED SELECT STATEMENT
# ---------------------------------------------------------

def custom_select():

    print("\n--- CUSTOM SELECT STATEMENT ---")

    print(
        "Example: SELECT * FROM Reviews LIMIT 10;"
    )

    query = input("Enter a CQL SELECT statement: ").strip()

    # Only allow SELECT statements for this menu option
    if not query.lower().startswith("select"):

        print(
            "Only SELECT statements are allowed "
            "with this option."
        )

        return

    try:

        results = session.execute(query)

        print("\n--- QUERY RESULTS ---")

        found_rows = False

        for row in results:

            print(row)

            found_rows = True

        if not found_rows:
            print("No rows returned.")

    except Exception as error:

        print("Query error:", error)


# ---------------------------------------------------------
# CHOOSE TABLE
# ---------------------------------------------------------

def choose_table():

    print("\nChoose a table:")
    print("1. Reviews")
    print("2. ProductCategories")

    choice = input(
        "Enter your choice: "
    ).strip()

    if choice == "1":
        return "Reviews"

    elif choice == "2":
        return "ProductCategories"

    else:

        print("Invalid table selection.")

        return None


# ---------------------------------------------------------
# ADD COLUMN
# ---------------------------------------------------------

def add_column():

    print("\n--- ADD COLUMN ---")

    table = choose_table()

    if table is None:
        return

    column = input(
        "Enter the new column name: "
    ).strip()

    # Make sure the column name is a simple valid identifier
    if not column.isidentifier():

        print("Invalid column name.")

        return

    print("\nAvailable data types:")
    print("text")
    print("int")
    print("decimal")
    print("float")
    print("boolean")
    print("timestamp")

    data_type = input(
        "Enter the column data type: "
    ).strip().lower()

    allowed_types = [
        "text",
        "int",
        "decimal",
        "float",
        "boolean",
        "timestamp"
    ]

    if data_type not in allowed_types:

        print("Invalid or unsupported data type.")

        return

    query = (
        "ALTER TABLE "
        + table
        + " ADD "
        + column
        + " "
        + data_type
        + ";"
    )

    try:

        session.execute(query)

        print(
            column
            + " was successfully added to "
            + table
            + "."
        )

    except Exception as error:

        print("Unable to add column:", error)


# ---------------------------------------------------------
# REMOVE COLUMN
# ---------------------------------------------------------

def remove_column():

    print("\n--- REMOVE COLUMN ---")

    table = choose_table()

    if table is None:
        return

    column = input(
        "Enter the column name to remove: "
    ).strip()

    if not column.isidentifier():

        print("Invalid column name.")

        return

    query = (
        "ALTER TABLE "
        + table
        + " DROP "
        + column
        + ";"
    )

    try:

        session.execute(query)

        print(
            column
            + " was successfully removed from "
            + table
            + "."
        )

    except Exception as error:

        print("Unable to remove column:", error)


# ---------------------------------------------------------
# DELETE REVIEWS / PRODUCTCATEGORIES TABLES
# ---------------------------------------------------------

def delete_tables():

    print("\n--- DELETE TABLES ---")

    print("1. Delete Reviews")
    print("2. Delete ProductCategories")
    print("3. Delete BOTH tables")
    print("4. Cancel")

    choice = input(
        "Enter your choice: "
    ).strip()

    try:

        if choice == "1":

            session.execute(
                "DROP TABLE IF EXISTS Reviews;"
            )

            print("Reviews table deleted.")

        elif choice == "2":

            session.execute(
                "DROP TABLE IF EXISTS ProductCategories;"
            )

            print("ProductCategories table deleted.")

        elif choice == "3":

            session.execute(
                "DROP TABLE IF EXISTS Reviews;"
            )

            session.execute(
                "DROP TABLE IF EXISTS ProductCategories;"
            )

            print(
                "Reviews and ProductCategories "
                "tables deleted."
            )

        elif choice == "4":

            print("Delete cancelled.")

        else:

            print("Invalid choice.")

    except Exception as error:

        print("Unable to delete table:", error)


# ---------------------------------------------------------
# DELETE AMAZON KEYSPACE
# ---------------------------------------------------------

def delete_keyspace():

    print("\n--- DELETE AMAZON KEYSPACE ---")

    confirmation = input(
        "Type DELETE to delete the Amazon keyspace: "
    ).strip()

    if confirmation == "DELETE":

        try:

            session.execute(
                "DROP KEYSPACE IF EXISTS Amazon;"
            )

            print("Amazon keyspace deleted.")

            return True

        except Exception as error:

            print(
                "Unable to delete Amazon keyspace:",
                error
            )

            return False

    else:

        print("Keyspace deletion cancelled.")

        return False


# ---------------------------------------------------------
# MAIN PROGRAM MENU
# ---------------------------------------------------------

while True:

    print("\n====================================")
    print("          AMAZON REVIEW MENU")
    print("====================================")
    print("1. Display distinct product categories")
    print("2. Count 4-star and higher reviews")
    print("3. Count 1-star reviews")
    print("4. Enter a SELECT statement")
    print("5. Add a column")
    print("6. Remove a column")
    print("7. Delete Reviews/ProductCategories tables")
    print("8. Delete Amazon keyspace")
    print("9. Exit")
    print("====================================")

    choice = input(
        "Enter your choice: "
    ).strip()


    if choice == "1":

        show_categories()


    elif choice == "2":

        count_high_reviews()


    elif choice == "3":

        count_one_star_reviews()


    elif choice == "4":

        custom_select()


    elif choice == "5":

        add_column()


    elif choice == "6":

        remove_column()


    elif choice == "7":

        delete_tables()


    elif choice == "8":

        keyspace_deleted = delete_keyspace()

        if keyspace_deleted:
            break


    elif choice == "9":

        print("Exiting program...")

        break


    else:

        print(
            "Invalid choice. "
            "Please enter a number from 1 through 9."
        )


# ---------------------------------------------------------
# CLOSE CASSANDRA CONNECTION
# ---------------------------------------------------------

cluster.shutdown()

print("Program ended.")
