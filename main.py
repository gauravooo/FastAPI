from fastapi import FastAPI , Path , HTTPException , Query
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Literal, Annotated , Optional

app = FastAPI()

class Patient(BaseModel):

    id: Annotated[str, Field(..., description="The unique identifier for the patient")]
    name: Annotated[str, Field(..., description="The name of the patient")]
    city: Annotated[str, Field(..., description="The city where the patient lives")]
    age: Annotated[int, Field(...,gt=0, lt=120, description="The age of the patient")]
    gender: Annotated[Literal["Male", "Female", "Other"], Field(..., description="The gender of the patient")]
    weight: Annotated[float, Field(...,gt=0, description="The weight of the patient in kg")]
    height: Annotated[float, Field(...,gt=0, description="The height of the patient in meters")]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi =  round(self.weight / (self.height ** 2), 2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
        bmi = self.bmi
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 25:
            return "Normal weight"
        elif 25 <= bmi < 30:
            return "Overweight"
        else:
            return "Obesity"


def load_data():
    with open("patients.json", "r") as file:
        data = json.load(file)
        return data

def save_data(data):
    with open("patients.json", "w") as file:
        json.dump(data, file)

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

@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    data[patient.id] = patient.model_dump(exclude={"id"})
    save_data(data)
    return JSONResponse(content={"message": "Patient created successfully"}, status_code=201)


class UpdatePatient(BaseModel):
    name: Annotated[Optional[str], Field(None)]
    city: Annotated[Optional[str], Field(None)]
    age: Annotated[Optional[int], Field(None,gt=0, lt=120)]
    gender: Annotated[Optional[Literal["Male", "Female", "Other"]], Field(None)]
    weight: Annotated[Optional[float], Field(None,gt=0)]
    height: Annotated[Optional[float], Field(None,gt=0)]

@app.put("/update/{patient_id}")
def update_patient(patient_id: str, patient_update : UpdatePatient):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    existing_patient = data[patient_id]
    update_data_info = patient_update.model_dump(exclude_unset=True)
    for key, value in update_data_info.items():
        existing_patient[key] = value

    existing_patient["id"] = patient_id
    patient_pydantic_obj = Patient(**existing_patient)
    existing_patient = patient_pydantic_obj.model_dump(exclude="id")
    data[patient_id] = existing_patient
    save_data(data)
    return JSONResponse(content={"message": "Patient updated successfully"}, status_code=200)

@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    del data[patient_id]
    save_data(data)
    return JSONResponse(content={"message": "Patient deleted successfully"}, status_code=200)
