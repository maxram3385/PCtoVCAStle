import json
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# Max Ramos
# SDC435L 3.3 Project - Cassandra Database Application
# Date: 9/20/2026
# Objective: Read GitHub Archive JSON data, store it in Cassandra,
# perform CRUD operations, and provide repository analysis features.

# Cassandra connection settings from the secured Cassandra lab
CASSANDRA_HOST = "127.0.0.1"
CASSANDRA_USER = "cassUser"
CASSANDRA_PASSWORD = "cassPass"

KEYSPACE = "github_project"
TABLE = "repositories"
DATA_FILE = "Sample_Repos.json"
IMPORT_LIMIT = 100


def connect_to_cassandra():
    """Connect to Cassandra and create the project keyspace/table if needed."""
    print("Connecting to local Cassandra database...")

    auth = PlainTextAuthProvider(
        username=CASSANDRA_USER,
        password=CASSANDRA_PASSWORD
    )

    cluster = Cluster(
        [CASSANDRA_HOST],
        port=9042,
        auth_provider=auth
    )

    session = cluster.connect()

    # Create a keyspace for the GitHub project.
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
        WITH replication = {{
            'class': 'SimpleStrategy',
            'replication_factor': 1
        }}
    """)

    session.set_keyspace(KEYSPACE)

    # repo_name is the primary key because repository names are unique identifiers.
    session.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE} (
            repo_name TEXT PRIMARY KEY,
            watch_count INT
        )
    """)

    print("Connected successfully.")
    return cluster, session


def create_repository(session):
    """CREATE: Add a repository record to Cassandra."""
    name = input("Repository name: ").strip()

    try:
        watchers = int(input("Watcher count: "))
    except ValueError:
        print("Watcher count must be a whole number.")
        return

    query = session.prepare(
        f"INSERT INTO {TABLE} (repo_name, watch_count) VALUES (?, ?)"
    )
    session.execute(query, (name, watchers))

    print("Repository added.")


def read_repository(session):
    """READ: Find one repository by its primary key."""
    name = input("Repository name: ").strip()

    query = session.prepare(
        f"SELECT repo_name, watch_count FROM {TABLE} WHERE repo_name = ?"
    )
    repo = session.execute(query, (name,)).one()

    if repo:
        print("Repository:", repo.repo_name)
        print("Watchers:", repo.watch_count)
    else:
        print("Repository not found.")


def update_repository(session):
    """UPDATE: Change the watcher count for an existing repository."""
    name = input("Repository name: ").strip()

    check_query = session.prepare(
        f"SELECT repo_name FROM {TABLE} WHERE repo_name = ?"
    )
    repo = session.execute(check_query, (name,)).one()

    if not repo:
        print("Repository not found.")
        return

    try:
        watchers = int(input("New watcher count: "))
    except ValueError:
        print("Watcher count must be a whole number.")
        return

    update_query = session.prepare(
        f"UPDATE {TABLE} SET watch_count = ? WHERE repo_name = ?"
    )
    session.execute(update_query, (watchers, name))

    print("Repository updated.")


def delete_repository(session):
    """DELETE: Remove a repository from Cassandra."""
    name = input("Repository name: ").strip()

    check_query = session.prepare(
        f"SELECT repo_name FROM {TABLE} WHERE repo_name = ?"
    )
    repo = session.execute(check_query, (name,)).one()

    if not repo:
        print("Repository not found.")
        return

    delete_query = session.prepare(
        f"DELETE FROM {TABLE} WHERE repo_name = ?"
    )
    session.execute(delete_query, (name,))

    print("Repository deleted.")


def import_repositories(session):
    """Read JSON-formatted GitHub Archive data and store it in Cassandra."""
    insert_query = session.prepare(
        f"INSERT INTO {TABLE} (repo_name, watch_count) VALUES (?, ?)"
    )

    count = 0

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            for line in file:
                repo = json.loads(line)

                name = repo["repo_name"]
                watchers = int(repo["watch_count"])

                # Cassandra INSERT operations are upserts. If the repo already exists,
                # its values are updated instead of creating a duplicate primary key.
                session.execute(insert_query, (name, watchers))
                count += 1

                # Keep the project demonstration manageable while using the same
                # import size as the previous Redis version.
                if IMPORT_LIMIT is not None and count >= IMPORT_LIMIT:
                    break

        print(count, "repositories imported into Cassandra.")

    except FileNotFoundError:
        print(f"Could not find {DATA_FILE}.")
        print("Make sure main.py and Sample_Repos.json are in the same Cassandra folder.")
    except (KeyError, ValueError, json.JSONDecodeError) as error:
        print("There was a problem reading the JSON data:", error)


def get_all_repositories(session):
    """Retrieve all repository records currently stored in the Cassandra table."""
    return list(
        session.execute(
            f"SELECT repo_name, watch_count FROM {TABLE}"
        )
    )


def show_most_watched(session):
    """Feature 1: Display the ten repositories with the highest watcher counts."""
    repos = get_all_repositories(session)

    if not repos:
        print("No repositories are currently stored.")
        return

    repos.sort(key=lambda repo: repo.watch_count, reverse=True)

    print("\n10 Most Watched Repositories")
    print("-" * 55)

    for number, repo in enumerate(repos[:10], start=1):
        print(f"{number}. {repo.repo_name} - {repo.watch_count} watchers")


def find_above_watch_count(session):
    """Feature 2: Find repositories at or above a user-specified watcher count."""
    try:
        minimum = int(input("Minimum watcher count: "))
    except ValueError:
        print("Watcher count must be a whole number.")
        return

    repos = get_all_repositories(session)
    matches = [repo for repo in repos if repo.watch_count >= minimum]
    matches.sort(key=lambda repo: repo.watch_count, reverse=True)

    if not matches:
        print("No repositories met that watcher count.")
        return

    print(f"\nRepositories with at least {minimum} watchers")
    print("-" * 55)

    for repo in matches:
        print(f"{repo.repo_name} - {repo.watch_count} watchers")

    print(f"\n{len(matches)} repositories found.")


def show_repository_statistics(session):
    """Feature 3: Calculate summary statistics from Cassandra repository data."""
    repos = get_all_repositories(session)

    if not repos:
        print("No repositories are currently stored.")
        return

    watch_counts = [repo.watch_count for repo in repos]
    highest_repo = max(repos, key=lambda repo: repo.watch_count)
    lowest_repo = min(repos, key=lambda repo: repo.watch_count)
    average = sum(watch_counts) / len(watch_counts)

    print("\nRepository Statistics")
    print("-" * 55)
    print("Total repositories:", len(repos))
    print(f"Average watcher count: {average:.2f}")
    print(
        f"Highest watcher count: {highest_repo.watch_count} "
        f"({highest_repo.repo_name})"
    )
    print(
        f"Lowest watcher count: {lowest_repo.watch_count} "
        f"({lowest_repo.repo_name})"
    )


def main():
    cluster = None
    session = None

    try:
        cluster, session = connect_to_cassandra()

        while True:
            print("\nGitHub Repository Cassandra Database")
            print("1. Import repositories from JSON")
            print("2. Add repository")
            print("3. Find repository")
            print("4. Update repository")
            print("5. Delete repository")
            print("6. Show most watched repositories")
            print("7. Find repositories above a watcher count")
            print("8. Display repository statistics")
            print("9. Exit")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                import_repositories(session)
            elif choice == "2":
                create_repository(session)
            elif choice == "3":
                read_repository(session)
            elif choice == "4":
                update_repository(session)
            elif choice == "5":
                delete_repository(session)
            elif choice == "6":
                show_most_watched(session)
            elif choice == "7":
                find_above_watch_count(session)
            elif choice == "8":
                show_repository_statistics(session)
            elif choice == "9":
                print("Goodbye.")
                break
            else:
                print("Invalid option.")

    except Exception as error:
        print("Could not run the Cassandra application.")
        print("Error:", error)
        print("Make sure Cassandra is running and cassUser/cassPass authentication is configured.")

    finally:
        if session is not None:
            session.shutdown()
        if cluster is not None:
            cluster.shutdown()


if __name__ == "__main__":
    main()
