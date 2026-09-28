# ------------------------------------------------------------
# Name: Max Ramos
# Date: September 28, 2026
# Assignment: Neo4j CRUD Application
# Purpose: Create a Python application that performs CRUD
# operations on a Neo4j graph database.
# ------------------------------------------------------------

import json
from neo4j import GraphDatabase

# Connect to Neo4j
URI = "neo4j://127.0.0.1:7687"
AUTH = ("neo4j", "YOUR_PASSWORD")

driver = GraphDatabase.driver(URI, auth=AUTH)
session = driver.session(database="neo4j")

# Open JSON file
with open("dataset_en_dev (3).json", "r", encoding="utf-8") as file:
    data = [json.loads(line) for line in file]

# Create nodes and relationships from JSON data
for item in data:

    session.run("""
        MERGE (c:Category {name: $category})
    """, category=item["product_category"])

    session.run("""
        MERGE (p:Product {name: $product})
    """, product=item["product_id"])

    session.run("""
        MERGE (r:Review {review_id: $review_id})
        SET r.title = $title,
            r.content = $content,
            r.stars = $stars
    """,
    review_id=item["review_id"],
    title=item["review_title"],
    content=item["review_body"],
    stars=int(item["stars"]))

    session.run("""
        MERGE (u:Reviewer {name: $reviewer})
    """, reviewer=item["reviewer_id"])

    session.run("""
        MATCH (p:Product {name: $product})
        MATCH (c:Category {name: $category})
        MERGE (p)-[:BELONGS_TO]->(c)
    """,
    product=item["product_id"],
    category=item["product_category"])

    session.run("""
        MATCH (p:Product {name: $product})
        MATCH (r:Review {review_id: $review_id})
        MERGE (p)-[:HAS_REVIEW]->(r)
    """,
    product=item["product_id"],
    review_id=item["review_id"])

    session.run("""
        MATCH (u:Reviewer {name: $reviewer})
        MATCH (r:Review {review_id: $review_id})
        MERGE (u)-[:WROTE]->(r)
    """,
    reviewer=item["reviewer_id"],
    review_id=item["review_id"])

print("JSON data imported successfully.")


# Main menu
while True:

    print("\n--- Neo4j CRUD Menu ---")
    print("1. Create Node")
    print("2. Create Relationship")
    print("3. Count Products by Category")
    print("4. Count Reviews by Reviewer")
    print("5. Update Node")
    print("6. Delete Category")
    print("7. Delete All Relationships")
    print("8. Delete All Nodes")
    print("9. Exit")

    choice = input("Enter selection: ")

    # Create node
    if choice == "1":

        print("\n1. Category")
        print("2. Product")
        print("3. Review")
        print("4. Reviewer")

        node_choice = input("Select node type: ")

        if node_choice == "1":
            name = input("Enter category name: ")
            session.run("CREATE (:Category {name: $name})", name=name)

        elif node_choice == "2":
            name = input("Enter product name: ")
            session.run("CREATE (:Product {name: $name})", name=name)

        elif node_choice == "3":
            review_id = input("Enter review ID: ")
            title = input("Enter title: ")
            content = input("Enter content: ")
            stars = int(input("Enter stars: "))

            session.run("""
                CREATE (:Review {
                    review_id: $review_id,
                    title: $title,
                    content: $content,
                    stars: $stars
                })
            """,
            review_id=review_id,
            title=title,
            content=content,
            stars=stars)

        elif node_choice == "4":
            name = input("Enter reviewer name: ")
            session.run("CREATE (:Reviewer {name: $name})", name=name)

        print("Node created.")


    # Create relationship
    elif choice == "2":

        print("\n1. Product to Category")
        print("2. Product to Review")

        rel_choice = input("Select relationship: ")

        if rel_choice == "1":

            product = input("Enter product name: ")
            category = input("Enter category name: ")

            session.run("""
                MATCH (p:Product {name: $product})
                MATCH (c:Category {name: $category})
                MERGE (p)-[:BELONGS_TO]->(c)
            """,
            product=product,
            category=category)

        elif rel_choice == "2":

            product = input("Enter product name: ")
            review_id = input("Enter review ID: ")

            session.run("""
                MATCH (p:Product {name: $product})
                MATCH (r:Review {review_id: $review_id})
                MERGE (p)-[:HAS_REVIEW]->(r)
            """,
            product=product,
            review_id=review_id)

        print("Relationship created.")


    # Count products by category
    elif choice == "3":

        category = input("Enter category name: ")

        result = session.run("""
            MATCH (p:Product)-[:BELONGS_TO]->(c:Category {name: $category})
            RETURN count(p) AS total
        """, category=category)

        print("Product count:", result.single()["total"])


    # Count reviews by reviewer
    elif choice == "4":

        reviewer = input("Enter reviewer name: ")

        result = session.run("""
            MATCH (u:Reviewer {name: $reviewer})-[:WROTE]->(r:Review)
            RETURN count(r) AS total
        """, reviewer=reviewer)

        print("Review count:", result.single()["total"])


    # Update node
    elif choice == "5":

        old_name = input("Enter current category name: ")
        new_name = input("Enter new category name: ")

        session.run("""
            MATCH (c:Category {name: $old_name})
            SET c.name = $new_name
        """,
        old_name=old_name,
        new_name=new_name)

        print("Category updated.")


    # Delete category
    elif choice == "6":

        category = input("Enter category name to delete: ")

        session.run("""
            MATCH (c:Category {name: $category})
            DETACH DELETE c
        """, category=category)

        print("Category deleted.")


    # Delete all relationships
    elif choice == "7":

        session.run("""
            MATCH ()-[r]-()
            DELETE r
        """)

        print("All relationships deleted.")


    # Delete all nodes
    elif choice == "8":

        session.run("""
            MATCH (n)
            DETACH DELETE n
        """)

        print("All nodes deleted.")


    # Exit
    elif choice == "9":

        break

    else:
        print("Invalid selection.")


session.close()
driver.close()
print("Program closed.")
