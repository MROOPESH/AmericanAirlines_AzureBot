rqstn_details = {
	"$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
	"type": "AdaptiveCard",
	"version": "1.0",
	"msTeams": { "width": "full" },
	"body": [
        {
            "type": "TextBlock",
            "text": "The requisition details are as follows:",
        },
		{
			"type": "FactSet",
			"facts": [
				{
					"title": "REQUISITION ID:",
					"value": "Value 1"
				},
				{
					"title": "HIRING MANAGER:",
					"value": "Value 2"
				},
				{
					"title": "OPEN DATE:",
					"value": "Value 3"
				},
				{
					"title": "REQUISITION STATUS:",
					"value": "Value 4"
				},
				{
					"title": "JOB TITLE:",
					"value": "Value 5"
				},
				{
					"title": "AGE OF REQUISITION:",
					"value": "Value 6"
				},
				{
					"title": "NUMBER OF OPENINGS:",
					"value": "Value 7"
				}
			]
		}
	]
}