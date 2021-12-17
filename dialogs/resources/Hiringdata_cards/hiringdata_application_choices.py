hiringdata_application_choices = {
    "type": "AdaptiveCard",
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.3",
    "body": [
      {
        "type": "TextBlock",
        "text": "Choose from the below Applicants data options."        
      },
      {
        "type": "Input.ChoiceSet",
        "id": "SelectVal_application",
        "style": "compact",
        "value" : "none",
        "choices": [
          {
            "title": "None",
            "value": "none"
          },
          {
            "title": "Job Divison",
            "value": "job_division"
          },
          {
            "title": "Job Category",
            "value": "job_catg"
          },
          {
            "title": "Work Location ",
            "value": "work_loc"
          },
          {
            "title": "Managing Director Name",
            "value": "md_name"
          },
          {
            "title": "VP Name",
            "value": "vp_name"
          },
          {
            "title": "Senior Vice President Name",
            "value": "svp_name"
          },
          {
            "title": "Senior Vice President2 Name",
            "value": "svp2_name"
          },
          {
            "title": "Senior Vice President3 Name",
            "value": "svp3_name"
          },
          {
            "title": "Executive Vice President",
            "value": "evp_name"
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