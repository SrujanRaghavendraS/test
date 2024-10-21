import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
logging.basicConfig(level=logging.INFO)
# Initialize Firebase Admin SDK
cred = credentials.Certificate("C:\\Users\\sruja\\Downloads\\smart-ai-71057-firebase-adminsdk-xynfi-c1c4546052.json")  # Update with your JSON file path
firebase_admin.initialize_app(cred)

# Initialize Firestore DB
db = firestore.client()

# FastAPI instance
app = FastAPI()

# CORS middleware to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserSignup(BaseModel):
    first_name: str
    last_name: str
    phone: str
    dob: str
    age: int
    address: str
    email: str
    password: str
    parent_name:str


# Pydantic model for user input
class UserLogin(BaseModel):
    email: str
    password: str  # In practice, you would not handle passwords this way for security reasons

@app.post("/signin")
async def sign_in(user: UserLogin):
    try:
        # Query Firestore for user data
        users_ref = db.collection('users')  # Assuming you have a 'users' collection

        # Ensure the field name matches the Firestore document structure (case-sensitive)
        query = users_ref.where('email', '==', user.email).limit(1)  # Assuming the field name in Firestore is lowercase 'email'
        results = query.get()

        if not results:
            raise HTTPException(status_code=400, detail="Invalid email or password")

        user_data = results[0].to_dict()

        # Check if password matches (assuming you've stored the password securely)
        if user_data.get("password") != user.password:
            raise HTTPException(status_code=400, detail="Invalid email or password")

        # Return user ID on successful login
        return {"message": "Logged in successfully", "user_id": results[0].id}

    except Exception as e:
        # Print error to console for detailed debugging
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during login")
    

@app.post("/signup")
async def sign_up(user: UserSignup):
    logging.info(f"Received data: {user}")
    try:
        # Check if the user already exists
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', user.email).limit(1).get()


        if query:
            raise HTTPException(status_code=400, detail="User with this email already exists")

        # Add new user to Firestore
        new_user_ref = users_ref.document()
        new_user_ref.set({
            "name":user.first_name+' '+user.last_name,
            "phone": user.phone,
            "dob": user.dob,
            "age": user.age,
            "address": user.address,
            "email": user.email,
            "password": user.password  ,
            "parentname": user.parent_name,# Ideally, hash this password before storing it
        })

        print(new_user_ref)

        return {"message": "Signup successful", "user_id": new_user_ref.id}

    except Exception as e:
        logging.error(f"Error during signup: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during signup")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)