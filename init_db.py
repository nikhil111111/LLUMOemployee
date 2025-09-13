# init_db.py
from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)

# Use (or create) database
db = client["assessment_db"]

# Use (or create) collection
employees = db["employees"]

# Insert a sample document
sample_employee = {
    "name": "Nikhil Garg",
    "email": "nikhil.garg@example.com",
    "position": "Software Engineer"
}

result = employees.insert_one(sample_employee)
print("Inserted employee with _id:", result.inserted_id)

# Verify by fetching it back
for emp in employees.find():
    print(emp)
