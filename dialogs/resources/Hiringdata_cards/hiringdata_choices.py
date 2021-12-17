hiringdata_choices = {
    "type": "AdaptiveCard",
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.3",
    "body": [
      {
        "type": "TextBlock",
        "text": "Choose from the below Hiring/Talent data options."        
      },
      {
        "type": "Input.ChoiceSet",
        "id": "SelectVal",
        "style": "compact",
        "placeholder": "Please choose",
        "choices": [
          {
            "title": "Requisition Data",
            "value": "requisition_data"
          },
          {
            "title": "Application Status",
            "value": "application_status"
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
      "title": "Cancel to go to main menu",
      "data":{  
            "action": "menucancel"      
        }
    }
  ]
}