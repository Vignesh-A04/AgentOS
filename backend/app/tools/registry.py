from app.tools.calculator import calculator
from app.tools.filesystem import (
    create_file,
    read_file,
    list_files,
)
from app.tools.api import api_get
from app.tools.web_search import web_search

TOOL_REGISTRY = {
    "calculator": calculator,
    "create_file": create_file,
    "read_file": read_file,
    "list_files": list_files,
    "api_get": api_get,
    "web_search": web_search,
}