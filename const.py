conversationSummarySchema = {
    "name": "get_conversation_summary",
    "description": "Summarizes the entire conversation in points and provides action items for users. The summary includes key points discussed, decisions made, and any important information shared during the conversation. Action items list specific tasks to be done, detailing who is responsible for each task.",
    "parameters": {
        "type": "object",
        "properties": {
            "conversation_summary": {
                "type": "array",
                "description": "List of key points summarizing the conversation.",
                "items": {
                    "type": "string",
                    "description": "A concise point that captures an important aspect of the conversation."
                }
            },
            "action_items": {
                "type": "array",
                "description": "List of action items derived from the conversation.",
                "items": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "A clear description of the task to be done."
                        },
                        "assignees": {
                            "type": "array",
                            "description": "List of individuals assigned to the task, with their roles or responsibilities.",
                            "items": {
                                "type": "string"
                            }
                        },
                        "due_date": {
                            "type": "string",
                            "format": "date",
                            "description": "The due date for the task completion, if applicable."
                        }
                    }
                }
            }
        }
    }
}