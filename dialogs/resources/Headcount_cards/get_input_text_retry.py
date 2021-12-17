get_input_text_retry = {
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.3",
  "body": [
    {
      "type": "TextBlock",
      "text": "Please check and re-enter the value"
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
    }
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
  ]
}