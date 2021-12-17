count_of_rqstn_criteria = {
    "type": "AdaptiveCard",
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.3",
    "body": [
      {
        "type": "TextBlock",
        "text": "Choose from the below requisition criteria options."        
      },
      {
        "type": "Input.ChoiceSet",
        "id": "criteria1",
        "style": "compact",
        "placeholder": "Please choose",
        "choices": [
          {
            "title": "Open",
            "value": "Open"
          }
        ]
      },
      {
        "type": "Input.ChoiceSet",
        "id": "criteria2",
        "style": "compact",
        "placeholder": "Please choose",
        "choices": [
          {
            "title": "Managing Director Name",
            "value": "md_nm"
          },
          {
            "title": "Vice President Name",
            "value": "vp_nm"
          },
          {
            "title": "Sr.Vice President Name",
            "value": "svp_nm"
          },
          {
            "title": "Sr.Vice President2 Name",
            "value": "svp2_nm"
          },
          {
            "title": "Sr.Vice President3 Name",
            "value": "svp3_nm"
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