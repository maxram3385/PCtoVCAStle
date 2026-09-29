# Name: Max Ramos
# Date: September 29, 2026
# Assignment: Guided Practice - Python Application Securing a Neo4j Database
# Objective: Create a Python application that assists with data securing techniques on a Neo4j database.

import os
from neo4j import GraphDatabase

#Connection information for local database
URI = "neo4j://localhost:7687"
AUTH = ("neo4j","password1")

#Create sample nodes
def createNodes(session):
    session.run("CREATE (:Person {name: 'Alice'})")
    session.run("CREATE (:Person {name: 'Bob'})")
    session.run("CREATE (:Person {name: 'Eve'})")
    session.run("CREATE (:Person {name: 'Mallory'})")

#Create sample relationships
def createRelationships(session):
    query = "MATCH (a:Person {name: 'Alice'}),(b:Person {name: 'Bob'})"
    query += " CREATE (a)-[:FRIEND]->(b)"
    session.run(query)

    query = "MATCH (a:Person {name: 'Eve'}),(b:Person {name: 'Mallory'})"
    query += " CREATE (a)-[:FRIEND]->(b)"
    session.run(query)

    query = "MATCH (a:Person {name: 'Eve'}),(b:Person {name: 'Alice'})"
    query += " CREATE (a)-[:EAVESDROP]->(b)"
    session.run(query)

    query = "MATCH (a:Person {name: 'Mallory'}),(b:Person {name: 'Bob'})"
    query += " CREATE (a)-[:TARGET]->(b)"
    session.run(query)

#Connect to the local database
username = os.getlogin()
print(f"Hello {username}, connecting to Neo4j...")
driver = GraphDatabase.driver(URI, auth=AUTH)
print("Connection success!")

#While connection is open, run queries
with driver.session() as session:
    print("Creating nodes...")
    session.execute_write(createNodes)
    print("Creating relationships...")
    session.execute_write(createRelationships)

#Close the connection
driver.close()
print("Connection to Neo4j closed.")
