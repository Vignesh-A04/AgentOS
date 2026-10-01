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