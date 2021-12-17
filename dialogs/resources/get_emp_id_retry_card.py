# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Example content for an AdaptiveCard."""

get_emp_id_retry = {
    "type": "AdaptiveCard",
    "body": [
        {
            "type": "TextBlock",
            "text": "Please enter a valid Employee/Personal Id"
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Employee/Personal Id :"
                        }
                    ],
                    "width": 40
                },
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "Input.Text",
                            "id": "userText",
                            "placeholder": "Enter employee ID here"
                        }
                    ],
                    "width": 60
                }
            ]
        },
    ],
    "actions": [
            {
                "type": "Action.Submit",
                "title": "Submit",
                "data":{  
                        "action": "submit"      
                }
            },
            {
                "type": "Action.Submit",
                "title": "Cancel",
                "data":{  
                        "action": "cancel"      
                }
            }
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.0"
}