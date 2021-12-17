hrdata_choices = {
    "type": "AdaptiveCard",
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.3",
    "body": [
      {
        "type": "TextBlock",
        "text": "Choose from the below HR/People data options."        
      },
      {
        "type": "Input.ChoiceSet",
        "id": "SelectVal",
        "style": "compact",
        "placeholder": "Please choose",
        "choices": [
          {
            "title": "Search by Employee ID",
            "value": "search_by_emp_id"
          },
          {
            "title": "Headcount",
            "value": "headcount"
          },
          {
            "title": "Insights",
            "value": "insights"
          },
          {
            "title": "Roster",
            "value": "roster"
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