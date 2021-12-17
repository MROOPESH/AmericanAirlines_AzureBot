get_termination_dates_retryprompt = {
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.3",
  "body": [
    {
      "type": "TextBlock",
      "text": "Please check and re-enter valid From and To Termination Dates"
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