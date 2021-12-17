main_menu_options = {
    "type": "AdaptiveCard",
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.3",
    "body": [
      {
        "type": "TextBlock",
        "text": "Ask EDDI... Choose from the below options."        
      },
      {
        "type": "Input.ChoiceSet",
        "id": "menu_choice_val",
        "style": "compact",
        "placeholder": "Please choose",
        "choices": [
          {
            "title": "Hiring/Talent Data",
            "value": "hiringdata"
          },
          {
            "title": "HR/People Data",
            "value": "hrdata"
          }
        ]
      }
  ],
  "actions": [
    {
      "type": "Action.Submit",
      "title": "Submit"
    }
  ]
}

