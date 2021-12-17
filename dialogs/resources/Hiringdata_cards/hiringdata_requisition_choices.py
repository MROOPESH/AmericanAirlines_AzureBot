hiringdata_rqstn_choices = {
    "type": "AdaptiveCard",
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.3",
    "body": [
      {
        "type": "TextBlock",
        "text": "Choose from the below Requisition data options."        
      },
      {
        "type": "Input.ChoiceSet",
        "id": "SelectVal_rqstn",
        "style": "compact",
        "placeholder": "Please choose",
        "choices": [
          {
            "title": "Search by Requisition ID",
            "value": "search_by_req_id"
          },
          {
            "title": "Count of Requisitions by Status",
            "value": "count_of_rqstn_by_status"
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