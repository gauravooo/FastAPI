from fastapi import FastAPI , Path , HTTPException , Query
import json

app = FastAPI()

def load_data():
    with open("patients.json", "r") as file:
        data = json.load(file)
        return data

@app.get("/")
def hello():
    return {"message": "Patient Management System"}

@app.get("/about")
def about():
    return {"message": "Fully functional patient management system built with FastAPI."}

@app.get("/view")
def view():
    data = load_data()
    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description="The ID of the patient to retrieve", examples =["P001"])):
    data = load_data()
    
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")

@app.get("/sort")
def sort_patients(sort_by: str = Query(..., description="The field to sort by"),
                  order_by: str = Query("asc", description="The order to sort (asc or desc)")):
    
    data = load_data()

    valid_fields = ["name", "age", "bmi", "weight", "height"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort field , select from {valid_fields}")
    
    if order_by not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order , select 'asc' or 'desc'")
    
    order = False if order_by == "asc" else True
    sorted_data = sorted(data.values(), key=lambda x: x[sort_by], reverse=order)
    return sorted_data
