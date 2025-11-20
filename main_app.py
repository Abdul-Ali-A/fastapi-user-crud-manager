from fastapi import status, FastAPI, HTTPException, Path
from typing import Optional
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi import Request, Form
from fastapi.responses import HTMLResponse

templates = Jinja2Templates(directory="templates")

# Full CRUD program with proper UI which gets users info using their username(Using FASTAPI Framework).
# Creats new users.
# Updates user details.
# Deletes Users, also automatically deletes users if their credit score requirement do not meet.
# No Database used, data is stored in dictionaries.
app = FastAPI()

users_db = {
    "mike": {
        "id_name": "Michael",
        "age": 35,
        "gender": "Male",
        "profession": "Mechanic",
        "hobby": "Jet Skiing",
        "credit_score": 95,
    },
    "john": {
        "id_name": "Johnathan",
        "age": 62,
        "gender": "Male",
        "profession": "Military Officer",
        "hobby": "Reading",
        "credit_score": 200,
    },
}


# Pydantic Model Classes:
class User(BaseModel):
    id_name: str
    age: int
    gender: str
    profession: Optional[str] = None
    hobby: Optional[str] = None
    credit_score: int


class UpdateUser(BaseModel):
    id_name: Optional[str] = None
    age: Optional[int] = None
    profession: Optional[str] = None
    hobby: Optional[str] = None
    credit_score: Optional[int] = None


# <---------------(BACKEND)------------------>


# Getting users information using their username:
@app.get("/user/{username}")
def get_username(
    username: str = Path(..., description="Enter your username to access your info:"),
):
    required_credit_score = 100
    if username not in users_db:
        raise HTTPException(
            status_code=404,
            detail="Invalid username provided.",
        )
    elif users_db[username]["credit_score"] <= required_credit_score:
        del users_db[username]
        raise HTTPException(
            status_code=400,
            detail="User Deleted due to Insufficient Credit Score!",
        )
    else:
        return users_db[username]


# Creating new users:
@app.post("/user/create_user/{username}", status_code=status.HTTP_201_CREATED)
def create_user(username: str, user: User):
    required_credit_score = 100

    if username in users_db:
        raise HTTPException(
            status_code=400,
            detail="User already exists!",
        )
    elif user.age >= 100 or user.age <= 0:
        raise HTTPException(status_code=400, detail="Age is Invalid")
    elif user.credit_score <= required_credit_score:
        raise HTTPException(
            status_code=400,
            detail="Credit Score requirement not met, user was not created!",
        )
    else:
        # Storing newly created user data as a dictionary in another dictionary.
        users_db[username] = user.dict()
        return {
            "message": f"User {users_db[username]['id_name']} Created successfully!"
        }


# Updating user details:
@app.put("/user/update/{username}")
def update_user(username: str, user: UpdateUser):
    required_credit_score = 100
    if username not in users_db:
        raise HTTPException(
            status_code=404,
            detail="This User does not exist!",
        )
    if user.id_name is not None:
        users_db[username]["id_name"] = user.id_name
    if user.age is not None:
        users_db[username]["age"] = user.age
    if user.profession is not None:
        users_db[username]["profession"] = user.profession
    if user.hobby is not None:
        users_db[username]["hobby"] = user.hobby
    if user.credit_score is not None:
        if user.credit_score <= required_credit_score:
            del users_db[username]
            raise HTTPException(
                status_code=400, detail="User Deleted due to Insufficient Credit Score!"
            )

    return {"message": f"Updated details for {users_db[username]['id_name']}"}


# Deleting users:
@app.delete("/user/delete/{username}", status_code=204)
def delete_user(
    username: str = Path(..., description="Enter the username to delete that user:"),
):
    if username not in users_db:
        raise HTTPException(
            status_code=404,
            detail="This User does not exist!",
        )
    del users_db[username]


# <---------------(FRONTEND)------------------>


# Home Page with links to other pages:
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# View User Details Page:
# For the exsisting dictionary users_db.
@app.get("/user/", response_class=HTMLResponse)
def view_user_by_query(request: Request, username: str):
    return view_user(request, username)


@app.get("/user/{username}/view", response_class=HTMLResponse)
def view_user(request: Request, username: str):
    try:
        user = get_username(username)  # reuse your existing logic
        return templates.TemplateResponse(
            "user_details.html",
            {"request": request, "user": user, "username": username},
        )
    except HTTPException as e:
        return HTMLResponse(content=f"<h2>{e.detail}</h2>", status_code=e.status_code)


# Create User Page:
@app.get("/create", response_class=HTMLResponse)
def create_form(request: Request):
    return templates.TemplateResponse("user_form.html", {"request": request})


@app.post("/create", response_class=HTMLResponse)
async def create_form_post(
    request: Request,
    username: str = Form(...),
    id_name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    profession: str = Form(None),
    hobby: str = Form(None),
    credit_score: int = Form(...),
):
    user = User(
        id_name=id_name,
        age=age,
        gender=gender,
        profession=profession,
        hobby=hobby,
        credit_score=credit_score,
    )
    try:
        create_user(username, user)
        return HTMLResponse(content="<h2>User created! <a href='/'>Home</a></h2>")
    except HTTPException as e:
        return HTMLResponse(
            content=f"<h2>Error: {e.detail}</h2>", status_code=e.status_code
        )


# Update User Page:
@app.get("/update/{username}", response_class=HTMLResponse)
def update_form(request: Request, username: str):
    if username not in users_db:
        raise HTTPException(status_code=404, detail="Not Found")
    return templates.TemplateResponse(
        "user_form.html",
        {"request": request, "username": username, "user": users_db[username]},
    )


@app.post("/user/update/{username}", response_class=HTMLResponse)
async def update_user_post(
    request: Request,
    username: str = Path(...),
    id_name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    profession: Optional[str] = Form(None),
    hobby: Optional[str] = Form(None),
    credit_score: int = Form(...),
):
    updates = {
        "id_name": id_name,
        "age": age,
        "gender": gender,
        "profession": profession,
        "hobby": hobby,
        "credit_score": credit_score,
    }

    updates = {k: v for k, v in updates.items() if v is not None}

    users_db[username].update(updates)
    return HTMLResponse("<h2>User updated! <a href='/'>Home</a></h2>")


# Delete User Page:
@app.get("/delete/{username}", response_class=HTMLResponse)
def delete_confirm(request: Request, username: str):
    if username not in users_db:
        return HTMLResponse("<h2>User not found</h2>")
    return templates.TemplateResponse(
        "user_delete.html", {"request": request, "username": username}
    )


@app.post("/delete/{username}", response_class=HTMLResponse)
def delete_user_post(username: str):
    delete_user(username)
    return HTMLResponse(
        '<h2 class="text-green-400">User deleted!</h2><a href="/">← Home</a>'
    )
