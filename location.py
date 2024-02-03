from fastapi import FastAPI, HTTPException, Depends, status
from typing import Annotated
from sqlmodel import Field, Session, select, create_engine, SQLModel


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Location Finder API",
    description="API to find the location of person stored in data base using SQLModel, FastAPI, GPT Actions",
    version="0.1.0",
    servers=[
        {
            "url": "https://cool-probable-seasnail.ngrok-free.app/",
            "description":"Production Server"
        },
        {
            "url": "http://127.0.0.1:8000/",
            "description":"Development Server"},
        ]
)

# CORS middleware configuration
origins = [
    "http://localhost:8000",   # Another example with a different port
    "https://cool-probable-seasnail.ngrok-free.app/",     # Example for a different domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

class Location(SQLModel, table=True,):
    name: str = Field(index=True, primary_key=True)
    location: str
    

database_url = "postgresql://aasifshahzad:kF5weXORDU7a@ep-white-sun-a1yogq94.ap-southeast-1.aws.neon.tech/location?sslmode=require"

engine = create_engine(database_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    # print("database created")
    
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Dependency Function
def get_location_or_404(name: str):
    with Session(engine) as session:
        statement = select(Location).where(Location.name == name)
        location = session.exec(statement).first()
        if not location:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Location not found for {name}")
        return location
    
# Get endpoint -> get location for a person
@app.get("/location/{name}")
def get_person_location(name: str, location: Annotated[Location, Depends(get_location_or_404)]):
    return location

# Get endpoint -> get location for all persons
@app.get("/persons/")
def read_all_persons():
    with Session(engine) as session:
        loc_data = session.exec(select(Location)).all()
        return loc_data

# Post endpoint -> Add person's location in database
@app.post("/person/")
def create_person(person_data: Location):
    with Session(engine) as session:
        session.add(person_data)
        session.commit()
        session.refresh(person_data)
        return person_data

# Delete endpoint -> delete  person along with its location
@app.delete("/{name}")
def delete_person_and_location(name: str):
    with Session(engine) as session:
        statement = select(name).where(name == name)
        person = session.exec(statement).first()
        if not person:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Person not found for {name}")
        
        session.delete(person)
        session.commit()
        
        return {"message": f"Person {name} and associated location deleted successfully"}


# Patch endpoint
@app.patch("/location/{name}")
def update_person_location(name: str, new_location: str):
    with Session(engine) as session:
        statement = select(Location).where(Location.name == name)
        location = session.exec(statement).first()
        if not location:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Location not found for {name}")

        location.location = new_location
        session.commit()

        return {"message": f"Location for {name} updated successfully"}