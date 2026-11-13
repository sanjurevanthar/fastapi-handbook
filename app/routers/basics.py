
"""01-08: the building Blocks - routes, HTTP methods, status codes, response types"""

from fastapi import APIRouter, Response, status
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse

router = APIRouter(tags=["01 basics"])

#01: Simplest GET. A dict is serilized to JSON automatically.
@router.get("/")
def root():
    return {"message": "Hello, FastAPI"}

#02 - async def. Use async when you await I/O(eg: httpx, async DB). A regular def runs in a threaad pool.
@router.get("/async-hello")
async def async_hello():
    return {"status": "ok"}

#03 - Health check, common in every real world services(load balancers)
@router.get("/health")
def health():
    return {"status": "ok"}

#04 - every HTTP method on one path.(Same path, different opperations)
@router.api_route("/methods", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def add_methods(response: Response):
    response.headers["X-Handled-By"] = "api_route"
    return {"info": "this route accepts GET/POST/PUT/PATCH/DELETE"}

#05 - Custom status code + setting a response header and cookies via the injected Response.
@router.post("/created", status_code=status.HTTP_201_CREATED)
def created(response: Response):
    response.headers["Location"] = "/items/1"
    response.set_cookie("session_hint", "abc123", httponly=True)
    return {"created": True}

#06 - returning a Response directly bypass response_model and give a full control.
@router.get("/custom-json")
def custom_json():
    return JSONResponse(
        status_code = 202,
        content = {"accecepted": True},
        headers = {"X-Custom": "yes"}
    ) 

#07 - A non json responses: plain Text and HTML
@router.get("/text", response_class=PlainTextResponse)
def text():
    return "Just Text"

@router.get("/html", response_class=HTMLResponse)
def html():
    return """
        <html>
            <body>
                <h1>HTML</h1>
            </body>
        </html>
    """

#08 - redirect and 204 No Content(204 must have an empty body)
@router.get("/old-path")
def old_path():
    return RedirectResponse(url="/", status_code = status.HTTP_308_PERMANENT_REDIRECT)

@router.get("/no-content")
def no_content():
    return Response(status_code=status.HTTP_204_NO_CONTENT)

