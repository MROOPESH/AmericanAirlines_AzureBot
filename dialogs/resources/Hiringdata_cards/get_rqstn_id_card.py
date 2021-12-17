# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Example content for an AdaptiveCard."""

get_rqstn_id = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.0",
    "body": [
        {
            "type": "TextBlock",
            "text": "Enter the Requisition Id"
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Requisition Id :"
                        }
                    ],
                    "width": 40
                },
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "Input.Text",
                            "id": "rqstn_id",
                            "placeholder": "Enter Requisition ID here"
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
                "title": "Cancel to go to main menu",
                "data":{  
                        "action": "cancel"      
                }
            }
    ]
}