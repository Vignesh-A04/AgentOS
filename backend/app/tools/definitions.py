CALCULATOR_TOOL = {
    "name": "calculator",
    "description": (
        "Perform basic arithmetic calculations. "
        "Use this tool when the user asks for "
        "addition, subtraction, multiplication, or division."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "a": {
                "type": "NUMBER",
                "description": "The first number."
            },
            "b": {
                "type": "NUMBER",
                "description": "The second number."
            },
            "operation": {
                "type": "STRING",
                "enum": [
                    "add",
                    "subtract",
                    "multiply",
                    "divide"
                ],
                "description": "The arithmetic operation."
            }
        },
        "required": [
            "a",
            "b",
            "operation"
        ]
    }
}

CREATE_FILE_TOOL = {
    "name": "create_file",
    "description": (
        "Create a text file inside the AgentOS workspace. "
        "Use this when the user asks you to create or write a file."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "path": {
                "type": "STRING",
                "description": (
                    "Workspace-relative file path, "
                    "for example outputs/report.txt."
                ),
            },
            "content": {
                "type": "STRING",
                "description": "The text content to write.",
            },
        },
        "required": [
            "path",
            "content",
        ],
    },
}


READ_FILE_TOOL = {
    "name": "read_file",
    "description": (
        "Read the contents of a text file "
        "inside the AgentOS workspace."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "path": {
                "type": "STRING",
                "description": (
                    "Workspace-relative file path."
                ),
            },
        },
        "required": [
            "path",
        ],
    },
}


LIST_FILES_TOOL = {
    "name": "list_files",
    "description": (
        "List files and directories inside "
        "the AgentOS workspace."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "path": {
                "type": "STRING",
                "description": (
                    "Workspace-relative directory path. "
                    "Use '.' for the workspace root."
                ),
            },
        },
        "required": [],
    },
}