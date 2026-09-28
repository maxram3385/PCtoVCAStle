# ============================================================
# Name: Max Ramos
# Assignment: Data Integrity - SQLite Database
# Description: Creates and manages a SQLite database using
#              tables, triggers, views, and stored functions.
# ============================================================

import sqlite3
import os


# Connect to the SQLite database
db = sqlite3.connect("DataIntegrity.db")
cursor = db.cursor()


def createTables():
    # Prep query to create a Patient table
    newTable = '''
    CREATE TABLE IF NOT EXISTS Patient (
        PatientID INTEGER PRIMARY KEY,
        FirstName TEXT,
        LastName TEXT,
        Address TEXT
    );
    '''
    db.execute(newTable)

    # Prep query to create a Medicine table
    newTable = '''
    CREATE TABLE IF NOT EXISTS Medicine (
        MedicineID TEXT PRIMARY KEY,
        Name TEXT,
        Category TEXT
    );
    '''
    db.execute(newTable)

    # Prep query to create a Prescription table
    newTable = '''
    CREATE TABLE IF NOT EXISTS Prescription (
        PrescriptionID TEXT PRIMARY KEY,
        MedicineID TEXT,
        PatientID INTEGER,
        Quantity INTEGER,
        RefillCount INTEGER,
        FOREIGN KEY(PatientID) REFERENCES Patient(PatientID),
        FOREIGN KEY(MedicineID) REFERENCES Medicine(MedicineID)
    );
    '''
    db.execute(newTable)


def insertData():
    # Create sample data
    patientList = [
        (1, "John", "Doe", "123 Main St."),
        (2, "Jane", "Doe", "456 Rain Rd."),
        (3, os.getlogin(), "TestLN", "TestAddress")
    ]

    medicineList = [
        ("MedA", "Medication A", "Antibiotic"),
        ("MedB", "Medication B", "Bronchodilator"),
        ("MedC", "Medication C", "Cold Relief")
    ]

    prescriptionList = [
        ("P1", "MedA", 1, 10, 3),
        ("P2", "MedB", 2, 20, 6),
        ("P3", "MedC", 3, 30, 12)
    ]

    # Insert data into the Patient table
    query = '''
    INSERT INTO Patient (PatientID, FirstName, LastName, Address)
    VALUES (?, ?, ?, ?);
    '''
    cursor.executemany(query, patientList)
    db.commit()

    # Insert data into the Medicine table
    query = '''
    INSERT INTO Medicine
    VALUES (?, ?, ?);
    '''
    cursor.executemany(query, medicineList)
    db.commit()

    # Insert data into the Prescription table
    query = '''
    INSERT INTO Prescription (
        PrescriptionID,
        MedicineID,
        PatientID,
        Quantity,
        RefillCount
    )
    VALUES (?, ?, ?, ?, ?);
    '''
    cursor.executemany(query, prescriptionList)
    db.commit()


def createUpdateTrigger():
    # Set a trigger on the Prescription table.
    # After every update, make sure refill count never goes negative.
    trigger = '''
    CREATE TRIGGER IF NOT EXISTS updateRefills
    AFTER UPDATE OF RefillCount ON Prescription
    FOR EACH ROW
    BEGIN
        UPDATE Prescription
        SET RefillCount = 0
        WHERE RefillCount < 0;
    END;
    '''
    cursor.execute(trigger)
    db.commit()


# Test the UPDATE trigger by trying to set a refill to a negative value
def updateRefills(val):
    query = '''
    UPDATE Prescription
    SET RefillCount = -1
    WHERE PrescriptionID = ?;
    '''
    cursor.execute(query, (val,))
    db.commit()


# Run the stored SQL function
def displayScript(num, quant, refill):
    script = "\nPatient #" + str(num) + " received " + str(quant)
    script += " doses and has " + str(refill) + " refills left.\n"
    return script


# Delete all tables and views from the database
def deleteTables():
    print("\nRemoving the Tables from the database...")

    query = "DROP TABLE IF EXISTS Prescription;"
    db.execute(query)
    db.commit()

    query = "DROP TABLE IF EXISTS Medicine;"
    db.execute(query)
    db.commit()

    query = "DROP TABLE IF EXISTS Patient;"
    db.execute(query)
    db.commit()

    query = "DROP VIEW IF EXISTS MedChart;"
    db.execute(query)
    db.commit()

    print("Complete!")


# Create a view to quickly display related data
def createView():
    query = '''
    SELECT FirstName, Name, Quantity, RefillCount
    FROM Patient Pa
    INNER JOIN Prescription Pr
        ON Pa.PatientID = Pr.PatientID
    INNER JOIN Medicine Me
        ON Pr.MedicineID = Me.MedicineID;
    '''

    view = f"CREATE VIEW IF NOT EXISTS MedChart AS {query}"
    cursor.execute(view)
    db.commit()


# *** MAIN Function ***
def main():
    print("Creating database...")

    # If tables currently exist, remove them
    deleteTables()

    # Create tables and insert information
    createTables()
    createUpdateTrigger()
    insertData()

    print("Database created and data loaded!")

    # Create a stored function to format script information
    db.create_function("displayScript", 3, displayScript)
    db.commit()

    # Run stored function
    print("Running Stored Function...")

    query = '''
    SELECT displayScript(PatientID, Quantity, RefillCount)
    FROM Prescription
    WHERE PatientID = 1;
    '''

    cursor.execute(query)
    print(*cursor.fetchone())

    # Attempt to update refills to -1
    print("Remove refills for which PrescriptionID? ")
    info = input()
    updateRefills(info)

    # Create a view and display its data
    createView()

    # Display the contents of the view
    query = "SELECT * FROM MedChart;"
    cursor.execute(query)
    result = cursor.fetchall()

    # Note that the Trigger activated to prevent negative refills
    print("Displaying contents of the MedChart View...")

    for row in result:
        print(row)

    # Close connection to database
    db.close()


# Run main function
main()
