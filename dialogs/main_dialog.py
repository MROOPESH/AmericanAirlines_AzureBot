# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import CardFactory, MessageFactory
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
    DialogTurnStatus
)
from botbuilder.dialogs.prompts import (
    ChoicePrompt, PromptOptions, TextPrompt, NumberPrompt, ConfirmPrompt, PromptValidatorContext
    )
from botbuilder.dialogs.choices import Choice
from botbuilder.schema import (
    ActionTypes,
    Attachment,
    CardAction,
    CardImage,
    Activity,
    ActivityTypes
)
import json

# Importing adaptive cards from resources folder
# In resources, main_menu_card.py is the file which contains main_menu_options dictionary...
# we are importing that dictionary from main_menu_card.py
from .resources.main_menu_card import main_menu_options

# similar to above import statement
from .resources.hrdata_choices import hrdata_choices
from .resources.get_emp_id_card import get_emp_id
#from .resources.emp_details_card import emp_details_card1
from .resources.emp_details_factset import emp_details_factset 
#from .resources.emp_details_terminated import emp_details_terminated
from .resources.get_emp_id_retry_card import get_emp_id_retry
from .resources.Insights_choices_card.top_10_locations_factset import top_10_locations_factset
from query_sql_mi import QuerySQLMI

from dialogs.insights_dialog import InsightsDialog
from dialogs.headcount_dialog import HeadcountDialog
from dialogs.hiringdata_dialog import HiringdataDialog

MAIN_WATERFALL_DIALOG = "mainWaterfallDialog"
CARD_PROMPT = "cardPrompt"


class MainDialog(ComponentDialog):
    def __init__(self):
        super().__init__("MainDialog")
        global qsm
        qsm = QuerySQLMI()
        qsm.init()

        # Define the main dialog and its related components.
        self.add_dialog(ChoicePrompt(CARD_PROMPT))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))

        # empid_prompt_validator is a validator for the input given by user in input box...
        # the emp id user enters for search emp details query is validated whether that empid is present in database
        self.add_dialog(NumberPrompt(NumberPrompt.__name__, MainDialog.empid_prompt_validator))
        
        # Insights dialog is seperate dialog like main_dialog.py which is developed for insights query 
        self.add_dialog(InsightsDialog(InsightsDialog.__name__))

        # Headcount Dialog is seperate dialog like main_dialog.py which is developed for Headcount query 
        self.add_dialog(HeadcountDialog(HeadcountDialog.__name__))

        # Hiringdata dialog is seperate dialog like main_dialog.py which is developed for Hiring data query 
        self.add_dialog(HiringdataDialog(HiringdataDialog.__name__))

        # The 3 waterfall steps are defined 
        self.add_dialog(
            WaterfallDialog(
                MAIN_WATERFALL_DIALOG, [
                    self.menu_options_card_step,
                    self.get_emp_id_step,
                    self.output_step,
                ]
            )
        )

        # The initial child Dialog to run.
        self.initial_dialog_id = MAIN_WATERFALL_DIALOG

    # This step shows the main menu options...
    async def menu_options_card_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        try:
            # when a user types 'hi'
            # there won't be any output.
            if step_context.context.activity.text.lower() == "hi":
                return await step_context.end_dialog()
        except:
            pass
        try:
            print(step_context.context.activity.text)  

            # The choice chosen by the user in main menu adaptive card is stored in step_context.values["menu_choice"] variable
            # The user choice is stored as a dictionary using json.loads()    
            step_context.values["menu_choice"] = json.loads(step_context.context.activity.text)

            # "menu_choice_val" is the id given to Input.ChoiceSet in main_menu_card.py
            if step_context.values["menu_choice"]["menu_choice_val"] == "hiringdata":
                # For hiringdata, hiringdata_dialog.py is called using begin_dialog()
                return await step_context.begin_dialog(HiringdataDialog.__name__)
            
            # If the user chooses HR/People data choice, then we show the HR/People data choices
            elif step_context.values["menu_choice"]["menu_choice_val"] == "hrdata":
                # Adaptive card with hr data choices...
                message = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.hrdata_choices_card()],
                )        
                await step_context.context.send_activity(message)
                await step_context.context.send_activity("If your query is not listed in above options please refer this [LINK](https://newjetnet.aa.com/community/people-analytics)")
                # This line takes us to the next step in waterfall steps which is get_emp_id_step...
                return DialogTurnResult(status=DialogTurnStatus.Waiting,result={})

            return DialogTurnResult(status=DialogTurnStatus.Waiting,result={})
        except:
            # if a user enters some text in chat instead of choosing choice from main menu adaptive card...
            # then in that case the dialog ends. 
            message2 = Activity(
                type=ActivityTypes.message,
                attachments=[self.main_menu_options_card()],
            )        
            await step_context.context.send_activity(message2)
            await step_context.context.send_activity("If your query is not listed in above options please refer this [LINK](https://newjetnet.aa.com/community/people-analytics)")
            return await step_context.end_dialog()


    async def get_emp_id_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        try:
            print(step_context.context.activity.text)

            # The choice chosen by the user in main menu adaptive card is stored in step_context.values["menu_choice"] variable
            # The user choice is stored as a dictionary using json.loads()     
            step_context.values["choice"] = json.loads(step_context.context.activity.text)
        except:
            # if a user enters some text in chat instead of choosing choice from main menu adaptive card...
            # then in that case the dialog ends by putting a main menu card.             
            message2 = Activity(
                type=ActivityTypes.message,
                attachments=[self.main_menu_options_card()],
            )        
            await step_context.context.send_activity(message2)
            await step_context.context.send_activity("If your query is not listed in above options please refer this [LINK](https://newjetnet.aa.com/community/people-analytics)")
            
            return await step_context.end_dialog()

        try:
            if step_context.values["choice"]["action"] == "menucancel":
                message = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.main_menu_options_card()],
                )        
                await step_context.context.send_activity(message)
                await step_context.context.send_activity("If your query is not listed in above options please refer this [LINK](https://newjetnet.aa.com/community/people-analytics)")            
                return await step_context.end_dialog()                

            # if user chooses Hiring/Talent data...
            # then in the previous step, the hiring_dialog.py is called and query is executed
            # and when the hiringdata dialog ends, then this if condition is executed...
            # The user is provided the main menu card again to continue querying.

            if step_context.values["menu_choice"]["menu_choice_val"] == "hiringdata":
                message2 = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.main_menu_options_card()],
                )        
                await step_context.context.send_activity(message2)
                await step_context.context.send_activity("If your query is not listed in above options please refer this [LINK](https://newjetnet.aa.com/community/people-analytics)")            
                return await step_context.end_dialog()

            # if the user chooses HR/People data, and then he chooses "Search by Employee ID" query...
            # then we need to get the employee id from the user..
            elif step_context.values["choice"]['SelectVal'] == "search_by_emp_id":
                # we are using two adaptive cards. They are get_emp_id_card.py, get_emp_id_retry_card.py
                # get_emp_id_card.py is to get the emp_id from the user for the first time...
                # get_emp_id_retry_card.py is used when a user enters wrong employee id or invalid employee id.
                # The validation of the input employee id given by the user is done in empid_prompt_validator() method below.
                # we defined a NumberPrompt with empid_prompt_validator in line 65 above...
                message = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.get_empid_card()],
                )
                message1 = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.get_empid_retry_card()],
                ) 
                # the empid_prompt_validator validates the user input text
                # if it says that the user input employee id is invalid, then the retry_prompt is implemented which uses the get_emp_id_retry_card.py       
                await step_context.prompt(
                    NumberPrompt.__name__,
                    PromptOptions(
                        prompt=message,
                        retry_prompt=message1,
                    ),
                )
                # This line takes us to the next step in waterfall steps which is output_step...
                return DialogTurnResult(status=DialogTurnStatus.Waiting,result={})

            # if the user chooses roster query, then we give a link in below as an output 
            elif step_context.values["choice"]['SelectVal'] == "roster": 
                # The output consists of a hyperlink "LINK", which takes to the link mentioned next to it...             
                await step_context.context.send_activity("To access Roster, please click on this [LINK](https://cognos.aa.com/c11/bi/v1/disp?pathRef=.public_folders%2FPeople%2FPeople%2BReports%2FRoster%2FRoster%2BReport%2B%2528Search%2Band%2BMulti%2BSelect%2529)")            
                # After the output link, a main menu card is shown to the user to continue with further queries...
                message = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.main_menu_options_card()],
                )        
                await step_context.context.send_activity(message)
                await step_context.context.send_activity("If your query is not listed in above options please refer this [LINK](https://newjetnet.aa.com/community/people-analytics)")            
                # On end_dialog(), the waterfall steps start again from the beginning...
                return await step_context.end_dialog()

            # For headcount query, headcount_dialog.py is called using begin_dialog()
            elif step_context.values["choice"]['SelectVal'] == "headcount":
                return await step_context.begin_dialog(HeadcountDialog.__name__)

            # For insights query, insights_dialog.py is called using begin_dialog()
            elif step_context.values["choice"]['SelectVal'] == "insights":
                return await step_context.begin_dialog(InsightsDialog.__name__)
            # This line takes us to the next step in waterfall steps which is output_step...
            return DialogTurnResult(status=DialogTurnStatus.Waiting,result={})
        except:
            # if a user enters some text in chat instead of choosing choice from main menu adaptive card...
            # then in that case the dialog ends by putting a main menu card.                         
            message = Activity(
                type=ActivityTypes.message,
                attachments=[self.main_menu_options_card()],
            )        
            await step_context.context.send_activity(message)
            await step_context.context.send_activity("If your query is not listed in above options please refer this [LINK](https://newjetnet.aa.com/community/people-analytics)")            
            return await step_context.end_dialog()            
        
    async def output_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        try:
            if step_context.values["choice"]['SelectVal'] == "search_by_emp_id":
                # In Search By Employee ID query
                # while entering employee id in text box of adaptive card,
                # if the user wants to end the query and click 'cancel' button, then we end the dialog by putting a main menu card...
                if step_context.context.activity.value['action'] == 'cancel':
                    message = Activity(
                        type=ActivityTypes.message,
                        attachments=[self.main_menu_options_card()],
                    )        
                    await step_context.context.send_activity(message)
                    await step_context.context.send_activity("If your query is not listed in above options please refer this [LINK](https://newjetnet.aa.com/community/people-analytics)")
                    return await step_context.end_dialog()

                # if the user enters a value in the textbox and clicks 'submit' button,
                # then we store the value entered by the user in step_context.values["emp_details"]
                step_context.values["emp_details"] = step_context.result
                print(step_context.values["emp_details"])

                # we pass the user entered employee id to fetch_emp_details_by_empid() method present in querydatalake.py...
                # ans is the response we get from fetch_emp_details_by_empid() method...
                ans = qsm.fetch_emp_details_by_empid(int(step_context.values["emp_details"]))
                    
                # The ans is passed to the adaptive card and the values are placed in the adaptive card to show it to user.
                # message1 is the results adaptive card for Search By Employee ID query...
                message1 = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.emp_details_output_card(ans)],
                ) 
                # this line is for putting the adaptive card as output response to user for his query...      
                await step_context.context.send_activity(message1)
                
                # message2 is the main menu card, so that the user can continue further with another queries...
                message2 = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.main_menu_options_card()],
                )        
                await step_context.context.send_activity(message2)
                await step_context.context.send_activity("If your query is not listed in above options please refer this [LINK](https://newjetnet.aa.com/community/people-analytics)")        
                return await step_context.end_dialog() 

            # when a user chooses headcount query, the query processing is done in headcount_dialog.py...
            # and at the end, the main menu card is put here...
            elif step_context.values["choice"]['SelectVal'] == "headcount":
                message2 = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.main_menu_options_card()],
                )        
                await step_context.context.send_activity(message2)
                await step_context.context.send_activity("If your query is not listed in above options please refer this [LINK](https://newjetnet.aa.com/community/people-analytics)")        
                return await step_context.end_dialog()    

            # when a user chooses insights query, the query processing is done in insights_dialog.py...
            # and at the end, the main menu card is put here...
            elif step_context.values["choice"]['SelectVal'] == "insights":
                message2 = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.main_menu_options_card()],
                )        
                await step_context.context.send_activity(message2)
                await step_context.context.send_activity("If your query is not listed in above options please refer this [LINK](https://newjetnet.aa.com/community/people-analytics)")        
                return await step_context.end_dialog()    

            # if none of the above conditions are satisfied then we end the dialog by putting main menu card.     
            message2 = Activity(
                type=ActivityTypes.message,
                attachments=[self.main_menu_options_card()],
            )        
            await step_context.context.send_activity(message2)
            await step_context.context.send_activity("If your query is not listed in above options please refer this [LINK](https://newjetnet.aa.com/community/people-analytics)")        
            return await step_context.end_dialog()
        except:
            # if a user enters some text in chat instead of interacting with the adaptive card...
            # then in that case the dialog ends by putting a main menu card.                         
            message2 = Activity(
                type=ActivityTypes.message,
                attachments=[self.main_menu_options_card()],
            )        
            await step_context.context.send_activity(message2)
            await step_context.context.send_activity("If your query is not listed in above options please refer this [LINK](https://newjetnet.aa.com/community/people-analytics)")      
            return await step_context.end_dialog()

    # ======================================
    # Helper functions used to create cards.
    # ======================================
    @staticmethod
    async def empid_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        # this validator is for validating when a user enters the employee id...
        # if validator returns True, then the next waterfall step is executed,
        # else the retry_promt adaptive card appears to user to check and enter valid details again...
        try:
            print(prompt_context.context.activity.text)
            # if the user doesn't enter the employee id in adaptive card and types some junk in chat space, then the json.loads() will throw an error
            # which is handled by the except statement...
            # except statement returns False which means the user will be prompted to check and enter a valid employee id in the adaptive card.
            print(json.loads(prompt_context.context.activity.text))
            print(prompt_context.context.activity.value['action'])
        except:
            # if the validator returns False, then the retry_prompt is initiated i.e. the same adaptive card appears to the user to enter a valid employee id.
            return False

        if prompt_context.context.activity.value['action'] == 'submit':
            try:
                # the validate_empid() method in query_sql_mi.py validate whether the employee id is present in the database or not
                # if not present, then it returns False 
                return (
                    prompt_context.recognized.succeeded
                    and qsm.validate_empid(prompt_context.context.activity.value['userText'])
                )
            except:
                return False
        elif prompt_context.context.activity.value['action'] == 'cancel':
            # if the user clicks 'cancel' button, then it returns True..
            return True


    # Methods to generate cards
    def hrdata_choices_card(self) -> Attachment:
        card_data = hrdata_choices    
        return CardFactory.adaptive_card(card_data)

    def main_menu_options_card(self) -> Attachment:
        card_data = main_menu_options    
        return CardFactory.adaptive_card(card_data)
    
    # This method returns an adaptive card containing text box as an attachment...
    def get_empid_card(self) -> Attachment:
        card_data = get_emp_id    
        return CardFactory.adaptive_card(card_data)

    # This method returns an retry adaptive card containing text box as an attachment...
    def get_empid_retry_card(self) -> Attachment:
        card_data = get_emp_id_retry    
        return CardFactory.adaptive_card(card_data)

    def top_10_locations_card(self, card_details) -> Attachment:
        card_data = top_10_locations_factset  
        for i, key in enumerate(card_details.keys()):
            card_data['body'][1]['facts'][i]['title'] = key
        
        for i, value in enumerate(card_details.values()):
            card_data['body'][1]['facts'][i]['value'] = str(value)
        return CardFactory.adaptive_card(card_data)

    # this method is to fit the adaptive card with the query ouptut details
    def emp_details_output_card(self, card_details: dict) -> Attachment:
        card_data = emp_details_factset
        # we loop through the card_details(response) from the fetch_emp_details_by_empid() and update the adaptive card...
        for i, value in enumerate(card_details.values()):
            card_data['body'][1]['facts'][i]['value'] = str(value).upper()  
        
        # the heading of the adaptive card is set here...
        card_data['body'][0]['text'] = "The details of the employee are as follows"   
        return CardFactory.adaptive_card(card_data)