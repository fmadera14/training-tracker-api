from fastapi import FastAPI

from src.database import Base, engine
from src.model import User, RoutineExercise, WorkoutSession, WorkoutExercise, WorkoutSet
from src.route.auth import router as auth_router
from src.route.exercises import router as exercise_router
from src.route.routines import router as routine_router
from src.route.routine_day import router as routine_days_router
from src.route.routine_exercise import router as routine_exercise_router
from src.route.workout_session import router as session_router
from src.route.workout_exercise import router as workout_exercise_router
from src.route.workout_set import router as workout_set_router
from src.route.user_settings import router as user_settings_router
from src.route.trainer_request import router as tariner_request_router
from src.route.user import router as user_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Training Tracker API")

app.include_router(auth_router)
app.include_router(exercise_router)
app.include_router(routine_router)
app.include_router(routine_days_router)
app.include_router(routine_exercise_router)
app.include_router(session_router)
app.include_router(workout_exercise_router)
app.include_router(workout_set_router)
app.include_router(user_settings_router)
app.include_router(tariner_request_router)
app.include_router(user_router)


@app.get("/")
def root():
    return {"message": "API corriendo"}
