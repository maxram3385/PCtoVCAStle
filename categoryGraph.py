# Max Ramos
# 9/27/2026
# Python Application Accessing a Graph Database
# Objective: Perform CRUD operations on a Neo4j graph database.

import json
from neo4j import GraphDatabase

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password1")

print("Connecting to local Neo4j database...")
driver = GraphDatabase.driver(URI, auth=AUTH)
session = driver.session()

categoryList = []
productList = []

print("Importing data from file...")

for line in open("dataset_en_dev.json", "r"):
    dataSet = json.loads(line)
    categoryList.append(dataSet["product_category"])
    productList.append([dataSet["product_id"], dataSet["product_category"]])

categoryList = list(set(categoryList))

print("Creating Category nodes...")
for category in categoryList:
    session.run("CREATE (:Category {name:$name})", name=category)

print("Creating Product nodes...")
for product in productList:
    session.run("CREATE (:Product {name:$name})", name=product[0])

print("Connecting Products to Categories...")
for product in productList:
    session.run(
        "MATCH (p:Product {name:$product}), (c:Category {name:$category}) "
        "CREATE (p)-[:CLASSIFIED_AS]->(c)",
        product=product[0],
        category=product[1]
    )

print("\nDisplaying the count of products per category:")

categoryList.sort()

for category in categoryList:
    result = session.run(
        "MATCH (:Product)-[:CLASSIFIED_AS]->(c:Category {name:$name}) "
        "RETURN count(*) AS total",
        name=category
    )

    print(category, "has", result.single()["total"], "products!")

print("\nAll relationships from book category removed.")
session.run(
    "MATCH (:Product)-[r:CLASSIFIED_AS]->(:Category {name:'book'}) DELETE r"
)

print("Toy node removed.")
session.run(
    "MATCH (c:Category {name:'toy'}) DETACH DELETE c"
)

print("All relationships removed.")
session.run("MATCH ()-[r]-() DELETE r")

print("All nodes removed.")
session.run("MATCH (n) DELETE n")

session.close()
driver.close()
