get_hire_dates = {
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.3",
  "body": [
    {
      "type": "TextBlock",
      "text": "Enter the value"
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
    {
      "type": "TextBlock",
      "text": "Enter the From and To Hire Dates"
    },
    {
      "type": "TextBlock",
      "text": "From Date Input"
    },
    {
      "type": "Input.Date",
      "id": "from_date",
      "placeholder": "Enter a date"
    },
    {
      "type": "TextBlock",
      "text": "To Date Input (Optional)"
    },
    {
      "type": "Input.Date",
      "id": "to_date",
      "placeholder": "Enter a date"
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
