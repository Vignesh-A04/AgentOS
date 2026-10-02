from app.tools.calculator import calculator
from app.tools.filesystem import (
    create_file,
    read_file,
    list_files,
)


TOOL_REGISTRY = {
    "calculator": calculator,
    "create_file": create_file,
    "read_file": read_file,
    "list_files": list_files,
}