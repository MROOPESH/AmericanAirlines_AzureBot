insights_choices = {
    "type": "AdaptiveCard",
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.3",
    "body": [
      {
        "type": "TextBlock",
        "text": "Choose from the below Insights options."        
      },
      {
        "type": "Input.ChoiceSet",
        "id": "insights_choice_val",
        "style": "compact",
        "errorMessage": "This is a required input",
        "placeholder": "Please choose",
        "choices": [
          {
            "title": "Top 10 Search",
            "value": "top10search"
          },
          {
            "title": "Average of Records",
            "value": "averageofrecords"
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