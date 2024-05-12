import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contactpr import routes
from fastapi_limiter.depends import RateLimiter
from contactpr.routes import router as contactpr_router


app = FastAPI()

app.include_router(routes.router)
origins = [ 
    "http://localhost:8000"
    ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def index():
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)