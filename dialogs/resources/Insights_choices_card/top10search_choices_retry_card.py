top10search_choices_retry = {
    "type": "AdaptiveCard",
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.3",
    "body": [
      {
        "type": "TextBlock",
        "text": "Please check and re-choose from the below Top 10 Search options."        
      },
      {
        "type": "Input.ChoiceSet",
        "id": "criteria2",
        "style": "compact",
        "placeholder": "Please choose",
        "choices": [
          {
            "title": "Headcount of Non-Terminated employees",
            "value": "1"
          },
          {
            "title": "No. of Hires by Hire Date",
            "value": "2"
          },
          {
            "title": "No. of Terminations by Termination Date",
            "value": "3"
          }
        ]
      },
      {
        "type": "Input.ChoiceSet",
        "id": "criteria1",
        "style": "compact",
        "placeholder": "Please choose",
        "choices": [
          {
            "title": "Cost Center",
            "value": "1"
          },
          {
            "title": "Department Unit",
            "value": "2"
          },
          {
            "title": "Division",
            "value": "3"
          },
          {
            "title": "Location",
            "value": "4"
          },
          {
            "title": "Managing Director Name",
            "value": "5"
          },
          {
            "title": "Reporting Work Group",
            "value": "6"
          },
          {
            "title": "Senior Vice President Name",
            "value": "7"
          },
          {
            "title": "Vice President Name",
            "value": "8"
          },
          {
            "title": "Termination Reason",
            "value": "9"
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
      "title": "Cancel to go to Main Menu",
      "data":{  
            "action": "menucancel"      
        }
    }
  ]
}