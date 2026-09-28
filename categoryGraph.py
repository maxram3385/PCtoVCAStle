import json
from neo4j import GraphDatabase

#Connection information for local database
URI = "neo4j://localhost:7687"
AUTH = ("neo4j","password1")

#Notify when script is starting
print("Connecting to local Neo4j database...")

driver = GraphDatabase.driver(URI, auth=AUTH)
session = driver.session()

#Create lists to hold each category and product
categoryList = []
productList = []

#Import data from JSON file
print("Importing data from file...")
for line in open('dataset_en_dev.json','r'):
 dataSet = json.loads(line)
 categoryList.append(dataSet["product_category"])
 productList.append([dataSet["product_id"],
dataSet["product_category"]])
 
#Filter out duplicate categories
categoryList = [*set(categoryList)]

#Create a node for each category
print("Creating Category nodes...")
for category in categoryList:
 query = "CREATE (node:Category {name:'" + category +
"'})"
 session.run(query)

#Create a node for each product
print("Creating Product nodes...")
for product in productList:
 query = "CREATE (node:Product{name:'" + product[0] +
"'})"
 session.run(query)

#Connect each product node to its category node
print("Connecting Products to Categories...")
for product in productList:
 query = "MATCH (node:Product) WHERE node.name='" +
product[0] + "' CREATE (node)-[:CLASSIFIED_AS]-\
>(:Category{name:'" + product[1] + "'})"
 session.run(query)

#Count the number of products per category
print("\nDisplaying the count of products per category:")

#Alphabetize list
categoryList.sort()

for category in categoryList:
 query = "MATCH (:Product)--(category:Category) WHERE \
category.name ='" + category + "' RETURN(COUNT(*))"
 result = session.run(query)
 print(category + " has " + str(result.value()) + " \
products!")

#Delete all relationships connected to 1 node
print("\nAll relationships from book category removed.")
query = "MATCH (node:Category{name:'book'})-[r:CLASIFIED_AS]-\
>() DELETE r"
session.run(query)

#Delete a node
print("Toy node removed.")
query = "MATCH (node:Category{name:'toy'}) DETACH DELETE \
node"
session.run(query)

#Delete all relationships
print("All relationships removed.")
query = "MATCH ()-[r]-() DELETE r"
session.run(query)

#Delete all nodes
print("All nodes removed.")
query = "MATCH (node) DELETE node"
session.run(query)
