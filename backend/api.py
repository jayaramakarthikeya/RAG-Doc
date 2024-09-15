from fastapi import FastAPI, HTTPException, Response, UploadFile, File, Form
from typing import Any
from rag.ollama_pipeline import OllamaPipeline
import uvicorn
import asyncio
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import shutil
from cryptography.fernet import Fernet
from langchain_community.document_loaders import PyPDFLoader
from langchain.vectorstores.utils import filter_complex_metadata

key = None
with open('/mnt/sda/hophacks/frontend/filekey.key', 'rb') as filekey:
    key = filekey.read()

fernet = Fernet(key)

user = None

app = FastAPI()

# Setting up SQLite Database
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    age = Column(Integer)
    blood_group = Column(String)
    password = Column(String)
    pdf_file_path = Column(String)

Base.metadata.create_all(bind=engine)

context_path = "/mnt/sda/hophacks/backend/symptom-disease-dataset.csv"
pipeline = OllamaPipeline(
    model_name="llama3.1",
    localhost="localhost",
    port=11434,
    embedding_function_type="all-MiniLM-L6-v2",
    context_path=context_path
)
pipeline.setup_query()

@app.post("/register/")
async def register_user(
    full_name: str = Form(...),
    email: str = Form(...),
    age: int = Form(...),
    blood_group: str = Form(...),
    file: UploadFile = File(...),
    password: bytes = Form(...)
):
    # Save PDF file to local directory
    file_location = f"pdf_files/{full_name}_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Store user data in the database
    db = SessionLocal()
    user = User(
        full_name=full_name,
        email=email,
        age=age,
        blood_group=blood_group,
        password=password,
        pdf_file_path=file_location,
        in_vector_database= 0
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully!"}

@app.post("/login/")
def login_user(
    full_name: str = Form(...),
    password: bytes = Form(...)
):
    db = SessionLocal()
    user = db.query(User).filter(User.full_name == full_name).first()
    #print(full_name)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    #print(fernet.decrypt(password).decode())
    if fernet.decrypt(user.password).decode() != fernet.decrypt(password).decode():
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    return {"message": "Login successful"}

@app.post("/query/")
def query(question: str):
   
    try:
        result = pipeline.query(question)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    asyncio.run(uvicorn.run(app, host="0.0.0.0", port=8000))