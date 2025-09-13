# main.py
from pymongo import MongoClient
from pydantic import BaseModel
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient


app = FastAPI()

# Mongo connection
MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["assessment_db"]
employees_collection = db["employees"]

# Define schema
class Employee(BaseModel):
    employee_id: str
    name: str
    department: str
    salary: float
    joining_date: str   # ISO string "YYYY-MM-DD"
    skills: list[str]

class UpdateEmployee(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[float] = None
    joining_date: Optional[str] = None
    skills: Optional[list[str]] = None

@app.get("/")
def home():
    return {"message": "API is running!"}

# Create employee
@app.post("/employees")
def create_employee(employee: Employee):
    if employees_collection.find_one({"employee_id": employee.employee_id}):
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    employees_collection.insert_one(employee.dict())
    return {"message": "Employee added successfully"}

# Get all employees
@app.get("/employees")
def get_employees():
    employees = []
    for emp in employees_collection.find():
        employees.append({
            "employee_id": emp.get("employee_id"),
            "name": emp.get("name"),
            "department": emp.get("department"),
            "salary": emp.get("salary"),
            "joining_date": emp.get("joining_date"),
            "skills": emp.get("skills", [])
        })
    return {"employees": employees}

@app.get("/employees")
def get_employees(department: Optional[str] = Query(None)):
    query = {}
    if department:
        query["department"] = department

    # Sort by joining_date descending (newest first)
    employees = list(employees_collection.find(query).sort("joining_date", -1))
    result = []
    for emp in employees:
        result.append({
            "employee_id": emp.get("employee_id"),
            "name": emp.get("name"),
            "department": emp.get("department"),
            "salary": emp.get("salary"),
            "joining_date": emp.get("joining_date"),
            "skills": emp.get("skills", [])
        })
    return {"employees": result}


@app.get("/employees/avg-salary")
def avg_salary_by_department():
    pipeline = [
        {"$group": {"_id": "$department", "average_salary": {"$avg": "$salary"}}}
    ]
    result = list(employees_collection.aggregate(pipeline))
    return [{"department": r["_id"], "average_salary": r["average_salary"]} for r in result]

@app.get("/employees/search")
def search_by_skill(skill: str = Query(...)):
    employees = employees_collection.find({"skills": skill})
    result = []
    for emp in employees:
        result.append({
            "employee_id": emp.get("employee_id"),
            "name": emp.get("name"),
            "department": emp.get("department"),
            "salary": emp.get("salary"),
            "joining_date": emp.get("joining_date"),
            "skills": emp.get("skills", [])
        })
    return {"employees": result}


# Get employee by employee_id
@app.get("/employees/{employee_id}")
def get_employee(employee_id: str):
    emp = employees_collection.find_one({"employee_id": employee_id})
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {
        "employee_id": emp["employee_id"],
        "name": emp["name"],
        "department": emp["department"],
        "salary": emp["salary"],
        "joining_date": emp["joining_date"],
        "skills": emp["skills"]
    }

# Update employee (partial updates allowed)
@app.put("/employees/{employee_id}")
def update_employee(employee_id: str, updates: UpdateEmployee):
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    result = employees_collection.update_one(
        {"employee_id": employee_id},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee updated successfully"}

# Delete employee
@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: str):
    result = employees_collection.delete_one({"employee_id": employee_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}
