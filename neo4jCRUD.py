# ------------------------------------------------------------
# Name: Max Ramos
# Date: September 28, 2026
# Assignment: Neo4j CRUD Application
# Purpose: Use Python to perform CRUD operations on a
# Neo4j graph database.
# ------------------------------------------------------------

import json
from neo4j import GraphDatabase

# Connect to Neo4j
URI = "neo4j://127.0.0.1:7687"
AUTH = ("neo4j", "password1")

driver = GraphDatabase.driver(URI, auth=AUTH)
session = driver.session(database="neo4j")


# ------------------------------------------------------------
# Import JSON data and create nodes and relationships
# ------------------------------------------------------------

with open("dataset_en_dev (3).json", "r", encoding="utf-8") as file:

    for line in file:

        item = json.loads(line)

        # Create Category
        session.run("""
            MERGE (c:Category {name: $name})
        """, name=item["product_category"])

        # Create Product
        session.run("""
            MERGE (p:Product {name: $name})
        """, name=item["product_id"])

        # Create Review
        session.run("""
            MERGE (r:Review {name: $name})
            SET r.title = $title,
                r.content = $content,
                r.stars = $stars
        """,
        name=item["review_id"],
        title=item["review_title"],
        content=item["review_body"],
        stars=item["stars"])

        # Create Reviewer
        session.run("""
            MERGE (u:Reviewer {name: $name})
        """, name=item["reviewer_id"])

        # Reviewer to Review
        session.run("""
            MATCH (u:Reviewer {name: $reviewer})
            MATCH (r:Review {name: $review})
            MERGE (u)-[:WROTE]->(r)
        """,
        reviewer=item["reviewer_id"],
        review=item["review_id"])

        # Product to Category
        session.run("""
            MATCH (p:Product {name: $product})
            MATCH (c:Category {name: $category})
            MERGE (p)-[:BELONGS_TO]->(c)
        """,
        product=item["product_id"],
        category=item["product_category"])

        # Product to Review
        session.run("""
            MATCH (p:Product {name: $product})
            MATCH (r:Review {name: $review})
            MERGE (p)-[:HAS_REVIEW]->(r)
        """,
        product=item["product_id"],
        review=item["review_id"])


print("Data imported successfully!")


# ------------------------------------------------------------
# Main Menu
# ------------------------------------------------------------

while True:

    print("\nType in a number and press enter to execute the menu option.")
    print("1. Create a new node")
    print("2. Create a new relationship")
    print("3. Count Products per Category")
    print("4. Count Reviews per Reviewer")
    print("5. Delete a category")
    print("6. Delete all relationships")
    print("7. Delete all nodes")
    print("8. Exit the program")

    choice = input()


    # --------------------------------------------------------
    # Create a new node
    # --------------------------------------------------------

    if choice == "1":

        print("\nWhat kind of node do you want to create?")
        print("1. Category")
        print("2. Product")
        print("3. Review")
        print("4. Reviewer")

        node = input()

        if node == "1":

            name = input("Enter Category name:\n")

            session.run("""
                CREATE (:Category {name: $name})
            """, name=name)

            print("Node Created!")

        elif node == "2":

            name = input("Enter Product name:\n")

            session.run("""
                CREATE (:Product {name: $name})
            """, name=name)

            print("Node Created!")

        elif node == "3":

            name = input("Enter Review name:\n")
            title = input("Enter Review title:\n")
            content = input("Enter Review content:\n")
            stars = input("Enter Review stars:\n")

            session.run("""
                CREATE (:Review {
                    name: $name,
                    title: $title,
                    content: $content,
                    stars: $stars
                })
            """,
            name=name,
            title=title,
            content=content,
            stars=stars)

            print("Node Created!")

        elif node == "4":

            name = input("Enter Reviewer name:\n")

            session.run("""
                CREATE (:Reviewer {name: $name})
            """, name=name)

            print("Node Created!")

        else:
            print("Invalid option.")


    # --------------------------------------------------------
    # Create a new relationship
    # --------------------------------------------------------

    elif choice == "2":

        print("\nWhat kind of relationship do you want to create?")
        print("1. Product to Category")
        print("2. Product to Review")

        relationship_choice = input()

        if relationship_choice == "1":

            product = input("Enter the name of the Product to connect:\n")
            category = input("Enter the name of the Category to connect:\n")
            relationship = input("Enter the name of the Relationship:\n")

            # Remove spaces from relationship name
            relationship = relationship.replace(" ", "_")

            query = f"""
                MATCH (p:Product {{name: $product}})
                MATCH (c:Category {{name: $category}})
                CREATE (p)-[:{relationship}]->(c)
            """

            session.run(
                query,
                product=product,
                category=category
            )

            print("\nRelationship Created!")

        elif relationship_choice == "2":

            product = input("Enter the name of the Product to connect:\n")
            review = input("Enter the name of the Review to connect:\n")
            relationship = input("Enter the name of the Relationship:\n")

            relationship = relationship.replace(" ", "_")

            query = f"""
                MATCH (p:Product {{name: $product}})
                MATCH (r:Review {{name: $review}})
                CREATE (p)-[:{relationship}]->(r)
            """

            session.run(
                query,
                product=product,
                review=review
            )

            print("\nRelationship Created!")

        else:
            print("Invalid option.")


    # --------------------------------------------------------
    # Count Products per Category
    # --------------------------------------------------------

    elif choice == "3":

        category = input("Enter Category name:\n")

        result = session.run("""
            MATCH (p:Product)-[]->(c:Category {name: $category})
            RETURN count(p) AS total
        """, category=category)

        print("Product Count:", result.single()["total"])


    # --------------------------------------------------------
    # Count Reviews per Reviewer
    # --------------------------------------------------------

    elif choice == "4":

        reviewer = input("Enter Reviewer name:\n")

        result = session.run("""
            MATCH (u:Reviewer {name: $reviewer})-[]->(r:Review)
            RETURN count(r) AS total
        """, reviewer=reviewer)

        print("Review Count:", result.single()["total"])


    # --------------------------------------------------------
    # Delete a Category
    # --------------------------------------------------------

    elif choice == "5":

        category = input("Enter Category name to delete:\n")

        session.run("""
            MATCH (c:Category {name: $category})
            DETACH DELETE c
        """, category=category)

        print("Category Deleted!")


    # --------------------------------------------------------
    # Delete all relationships
    # --------------------------------------------------------

    elif choice == "6":

        session.run("""
            MATCH ()-[r]-()
            DELETE r
        """)

        print("All Relationships Deleted!")


    # --------------------------------------------------------
    # Delete all nodes
    # --------------------------------------------------------

    elif choice == "7":

        session.run("""
            MATCH (n)
            DETACH DELETE n
        """)

        print("All Nodes Deleted!")


    # --------------------------------------------------------
    # Exit
    # --------------------------------------------------------

    elif choice == "8":

        print("Program Closed.")
        break

    else:
        print("Invalid option.")


session.close()
driver.close()
