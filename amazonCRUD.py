# Name: Max Ramos
# Date: 09/20/2026
# Assignment: Cassandra CRUD Application
# Purpose: Create a Python application that performs CRUD operations
# on an Amazon Cassandra database using review data from a JSON file.

import json
from cassandra.cluster import Cluster


# Connect to local Cassandra database
print("Connecting to local Cassandra database...")

cluster = Cluster()
session = cluster.connect()


# Create Amazon keyspace
keyspace = '''
CREATE KEYSPACE IF NOT EXISTS Amazon
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};
'''

session.execute(keyspace)

# Connect to Amazon keyspace
session.set_keyspace('amazon')


# Create Reviews table
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


# Create ProductCategories table
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


# Import JSON data
print("Importing data from JSON file...")

with open('dataset_en_dev.json', 'r') as file:
    for line in file:
        dataSet = json.loads(line)

        # Insert data into Reviews table
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

        # Insert data into ProductCategories table
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
