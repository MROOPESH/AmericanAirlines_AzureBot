# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import MessageFactory, CardFactory
from botbuilder.dialogs import (
    WaterfallDialog,
    DialogTurnResult,
    WaterfallStepContext,
    ComponentDialog,
    DialogTurnResult,
    DialogTurnStatus
)
from botbuilder.schema import (
    Attachment,
    Activity,
    ActivityTypes
)

from botbuilder.dialogs.prompts import PromptOptions, TextPrompt, NumberPrompt, DateTimePrompt, PromptOptions, PromptValidatorContext
from .resources.Headcount_cards.headcount_choices_card import headcount_choices_select
from .resources.Headcount_cards.get_hire_dates import get_hire_dates
from .resources.Headcount_cards.get_hire_dates_retryprompt import get_hire_dates_retryprompt
from .resources.Headcount_cards.get_termination_dates import get_termination_dates
from .resources.Headcount_cards.get_termination_dates_retryprompt import get_termination_dates_retryprompt
from .resources.Headcount_cards.get_input_text import get_input_text
from .resources.Headcount_cards.get_input_text_retry import get_input_text_retry
from .resources.Headcount_cards.headcount_records import headcount_records
from .resources.Headcount_cards.headcount_None_records import headcount_None_records

import json
import pandas as pd
from query_sql_mi import QuerySQLMI
import os 
import copy

# the criteria1 chosen by the user is replaced with the dataset column_name...
data_columns_1 = {
    "1" : "cost_center_cd",
    "2" : "department_unit",
    "3" : "division_nm",
    "4" : "location_cd",
    "5" : "md_name",
    "6" : "rptg_wrkgrp",
    "7" : "sr_vp_name",
    "8" : "vp_name"
}

data_columns_2 = {
    "1" : "Cost Center",
    "2" : "Department Unit",
    "3" : "Division",
    "4" : "Location",
    "5" : "MD",
    "6" : "Reporting Workgroup",
    "7" : "Sr.VP ",
    "8" : "VP"
}

data_columns_3 = {
    "1" : " active employees",
    "2" : " hires by hire date",
    "3" : " terminations by termination date"
}


text_criteria = {
    "1" : ["Enter the cost center code", "Cost Center Code:", "Eg. 9000/0001", "Please check and re-enter a valid cost center code"],
    "2" : ["Enter the Department unit", "Department unit:", "Eg. 90000000", "Please check and re-enter a valid department unit"],
    "3" : ["Enter the Division name", "Division:", "Eg. Conversion Division", "Please check and re-enter a valid division name"],
    "4" : ["Enter the Location code", "Location:", "Eg. CNV-LOCN", "Please check and re-enter a valid Location code"],
    "5" : ["Enter the Managing Director Name", "Managing Director:", "Eg. Last name, First name", "Please check and re-enter a valid Managing Director Name"],
    "6" : ["Enter the Reporting Work Group", "Reporting Work Group:", "Eg. Passenger Service", "Please check and re-enter a valid Reporting Work Group"],
    "7" : ["Enter the Senior Vice President Name", "Sr Vice President Name:", "Eg. Last name, First name", "Please check and re-enter a valid Senior Vice President Name"],
    "8" : ["Enter the Vice President Name", "Vice President Name:", "Eg. Last name, First name", "Please check and re-enter a valid Vice President Name"]
}



class HeadcountDialog(ComponentDialog):
    def __init__(self, dialog_id: str):
        super(HeadcountDialog, self).__init__(dialog_id or HeadcountDialog.__name__)

        global qsm
        qsm = QuerySQLMI()

        # text_prompt_validator is a validator for the input given by user in text box...
        # the user enters the prompted value in text box and is validated whether that value is present in database
        # ex: if a user enters a cost center value, the validator validates whether that cost center is present in database or not.
        self.add_dialog(TextPrompt("textprompt", HeadcountDialog.text_prompt_validator))

        # date_prompt_validator is a validator for the date chosen by user in Date Input box...
        # the user chooses a date in date input box and is validated whether that value is present in database
        self.add_dialog(DateTimePrompt("datetimeprompt1", HeadcountDialog.date_prompt_validator1))
        self.add_dialog(DateTimePrompt("datetimeprompt2", HeadcountDialog.date_prompt_validator2))

        # The 3 waterfall steps are defined         
        self.add_dialog(
            WaterfallDialog(
                "WFDialog",
                [
                    self.headcount_choice_step,
                    self.get_dates_step,
                    self.output_step,
                ],
            )
        )
        
        self.initial_dialog_id = "WFDialog"

    async def headcount_choice_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        # When a user chooses Insights query in main_dialog.py...
        # We give the user the criteria combinations which the user can choose.
        message = Activity(
            type=ActivityTypes.message,
            attachments=[self.headcount_choice_card()],
        )        
        await step_context.context.send_activity(message)
        # This line takes us to the next step in waterfall steps
        return DialogTurnResult(status=DialogTurnStatus.Waiting,result={})


    async def get_dates_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        try:
            print(step_context.context.activity.text)
            # The choice chosen by the user in Headcount choices adaptive card is stored in step_context.values["insights_choices"] variable
            # The user choice is stored as a dictionary using json.loads()     
            step_context.values["insights_choices"] = json.loads(step_context.context.activity.text)
        except:
            # if a user enters some text in chat instead of choosing choice from Headcount choices adaptive card...
            # then in that case the dialog ends by putting a Headcount choices card.
            return await step_context.end_dialog()
        
        try:
            print(step_context.context.activity.value['action'])
            # if user clicks "Cancel to go to main menu" button, then we end the headcount and go to main menu dialog...
            if step_context.context.activity.value['action'] == 'menucancel':
                return await step_context.end_dialog()

            # if the user clicks "cancel" button, then we begin the headcount dialog again so that the user can choose another criteria choices... 
            elif step_context.context.activity.value['action'] == 'cancel':
                return await step_context.begin_dialog(HeadcountDialog.__name__)
            
            # if the user chooses Headcount of Non-Terminated employees, then the following is executed...
            if step_context.values["insights_choices"]['criteria2'] == '1':
                # If the user chooses "None" option in adaptive card, then we can directly process the query without any input from user...
                if step_context.values["insights_choices"]['criteria1'] == '0':
                    # headcount_None_1() is the method in querydatalake file...
                    ans = qsm.headcount_None_nonterminated()
                    # we load the adaptive card with results and then display it to the user
                    message = Activity(
                        type=ActivityTypes.message,
                        attachments=[self.headcount_None_records_card(ans, step_context.values["insights_choices"]['criteria1'], step_context.values["insights_choices"]['criteria2'])],
                    )
                    await step_context.context.send_activity(message)
                    # At the end of query, we go to the beginning of headcount query,
                    # so that the user can perform another query 
                    return await step_context.begin_dialog(HeadcountDialog.__name__)

                # if the user choice is other that "None" in 2nd dropdown choice of adptive card,
                # then the following executes...
                message = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.get_input_text_card(step_context.values["insights_choices"]['criteria1'])],
                )   
                message1 = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.get_input_text_retry_card(step_context.values["insights_choices"]['criteria1'])],
                )
                # The user will be prompted to enter a value in a text box using prompt=message...
                # if the value entered by the user is not present in the database, then the user will be re_prompted to enter the value using retry_prompt=message1
                await step_context.prompt(
                    "textprompt",
                    PromptOptions(
                        prompt=message,
                        retry_prompt=message1,
                    ),
                )
                # After the validation is passed, we go to next waterfall steps...
                return DialogTurnResult(status=DialogTurnStatus.Waiting,result={})

            # if the user chooses No. of Hires by Hire Date, then the following is executed...
            elif step_context.values["insights_choices"]['criteria2'] == '2':
                # The user will be prompted to enter a value in a text box and also choose From_date and To_date using prompt=message...
                # if the value entered by the user is not present in the database or the dates entered are invalid, then the user will be re_prompted to enter the value using retry_prompt=message1
                message = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.get_hire_dates_card(step_context.values["insights_choices"]['criteria1'])],
                )     
                message_1 = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.get_hire_dates_retryprompt_card(step_context.values["insights_choices"]['criteria1'])],
                ) 
                # if the user chooses "None" as the choice in 2nd dropdown choices,
                # then, the below adaptive cards are put to the user...
                if step_context.values["insights_choices"]['criteria1'] == '0':
                    await step_context.prompt(
                        "datetimeprompt2",
                        PromptOptions(
                            prompt=message,
                            retry_prompt=message_1,
                        ),
                    )
                else:
                    await step_context.prompt(
                        "datetimeprompt1",
                        PromptOptions(
                            prompt=message,
                            retry_prompt=message_1,
                        ),
                    )
                return DialogTurnResult(status=DialogTurnStatus.Waiting,result={})

            # if the user chooses No. of Terminations by Termination Date, then the following is executed...
            elif step_context.values["insights_choices"]['criteria2'] == '3':
                message = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.get_termination_dates_card(step_context.values["insights_choices"]['criteria1'])],
                )
                message_1 = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.get_termination_dates_retryprompt_card(step_context.values["insights_choices"]['criteria1'])],
                )
                # if one of the choice is "None", then we don't need to validate the text value...
                # else, we need to validate the text followed by the from_date and to_date.
                if step_context.values["insights_choices"]['criteria1'] == '0':
                    await step_context.prompt(
                        "datetimeprompt2",
                        PromptOptions(
                            prompt=message,
                            retry_prompt=message_1,
                        ),
                    )
                else:
                    await step_context.prompt(
                        "datetimeprompt1",
                        PromptOptions(
                            prompt=message,
                            retry_prompt=message_1,
                        ),
                    )
                return DialogTurnResult(status=DialogTurnStatus.Waiting,result={})

            return await step_context.end_dialog()
        except:
            return await step_context.end_dialog()

    async def output_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        try:
            print(step_context.context.activity.value)
            # if user clicks "Cancel to go to main menu", then we end dialog...
            if step_context.context.activity.value['action'] == 'menucancel':
                return await step_context.end_dialog()
            if step_context.values["insights_choices"]['criteria2'] == "1":
                if step_context.context.activity.value['action'] == 'cancel':
                    return await step_context.begin_dialog(HeadcountDialog.__name__)
                # we store the user entered text value in step_context.values["get_usertext"]...
                step_context.values["get_usertext"] = json.loads(step_context.context.activity.text)
                ans = qsm.headcount_non_terminated(data_columns_1[step_context.values["insights_choices"]['criteria1']], str(step_context.values["get_usertext"]["userText"]))
                # we fit the results adaptive card with the output of query...
                message = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.headcount_records_card(ans, step_context.values["insights_choices"]['criteria1'], step_context.values["insights_choices"]['criteria2'])],
                )        
                await step_context.context.send_activity(message)
                return await step_context.begin_dialog(HeadcountDialog.__name__)

            elif step_context.values["insights_choices"]['criteria2'] == "2":
                if step_context.context.activity.value['action'] == 'cancel':
                    return await step_context.begin_dialog(HeadcountDialog.__name__)
                # we store the user entered text value in step_context.values["get_usertext"]
                if step_context.values["insights_choices"]['criteria1'] == "0":
                    step_context.values["get_dates"] = json.loads(step_context.context.activity.text)
                    # from_date and to_date entered by user are stored in a variable...
                    from_date = step_context.values["get_dates"]['from_date']
                    try:
                        if step_context.values["get_dates"]['to_date'] != "":
                            to_date = step_context.values["get_dates"]['to_date']
                        else:
                            to_date = ""
                    except:
                        to_date = ""

                    ans = qsm.headcount_None_hire(from_date, to_date)
                    # we fit the adpative card with the results of query...
                    message = Activity(
                        type=ActivityTypes.message,
                        attachments=[self.headcount_None_records_card(ans, step_context.values["insights_choices"]['criteria1'], step_context.values["insights_choices"]['criteria2'])],
                    )        
                    await step_context.context.send_activity(message)
                    return await step_context.begin_dialog(HeadcountDialog.__name__)

                else:
                    step_context.values["get_dates"] = json.loads(step_context.context.activity.text)
                    from_date = step_context.values["get_dates"]['from_date']
                    try:
                        if step_context.values["get_dates"]['to_date'] != "":
                            to_date = step_context.values["get_dates"]['to_date']
                        else:
                            to_date = ""
                    except:
                        to_date = ""
                    ans = qsm.headcount_hires_by_hiredate(data_columns_1[step_context.values["insights_choices"]['criteria1']], from_date, to_date, str(step_context.values["get_dates"]["userText"]))
                    
                    message = Activity(
                        type=ActivityTypes.message,
                        attachments=[self.headcount_records_card(ans, step_context.values["insights_choices"]['criteria1'], step_context.values["insights_choices"]['criteria2'])],
                    )        
                    await step_context.context.send_activity(message)
                    return await step_context.begin_dialog(HeadcountDialog.__name__)

            elif step_context.values["insights_choices"]['criteria2'] == "3":
                if step_context.context.activity.value['action'] == 'cancel':
                    return await step_context.begin_dialog(HeadcountDialog.__name__)

                if step_context.values["insights_choices"]['criteria1'] == "0":
                    step_context.values["get_dates"] = json.loads(step_context.context.activity.text)
                    from_date = step_context.values["get_dates"]['from_date']
                    try:
                        if step_context.values["get_dates"]['to_date'] != "":
                            to_date = step_context.values["get_dates"]['to_date']
                        else:
                            to_date = ""
                    except:
                        to_date = ""

                    ans = qsm.headcount_None_terminated(from_date, to_date)
                    message = Activity(
                        type=ActivityTypes.message,
                        attachments=[self.headcount_None_records_card(ans, step_context.values["insights_choices"]['criteria1'], step_context.values["insights_choices"]['criteria2'])],
                    )        
                    await step_context.context.send_activity(message)
                    return await step_context.begin_dialog(HeadcountDialog.__name__)

                else:
                    step_context.values["get_dates"] = json.loads(step_context.context.activity.text)
                    from_date = step_context.values["get_dates"]['from_date']
                    try:
                        if step_context.values["get_dates"]['to_date'] != "":
                            to_date = step_context.values["get_dates"]['to_date']
                        else:
                            to_date = ""
                    except:
                        to_date = ""

                    ans = qsm.headcount_trmns_by_terminationdate(data_columns_1[step_context.values["insights_choices"]['criteria1']], from_date, to_date, str(step_context.values["get_dates"]["userText"]))
                    message = Activity(
                        type=ActivityTypes.message,
                        attachments=[self.headcount_records_card(ans, step_context.values["insights_choices"]['criteria1'], step_context.values["insights_choices"]['criteria2'])],
                    )        
                    await step_context.context.send_activity(message)
                    return await step_context.begin_dialog(HeadcountDialog.__name__)
            return await step_context.end_dialog()
        except:
            return await step_context.begin_dialog(HeadcountDialog.__name__)

        
    @staticmethod
    async def date_prompt_validator1(prompt_context: PromptValidatorContext) -> bool:
        try:
            print(prompt_context.recognized.succeeded)
            print(prompt_context.context.activity.text)
            print(json.loads(prompt_context.context.activity.text))
            print(prompt_context.context.activity.value['action'])
        except:
            return False
        
        if prompt_context.context.activity.value['action'] == 'submit':
            try:
                if json.loads(prompt_context.context.activity.text)['from_date'] != "":
                    from_date = pd.to_datetime(json.loads(prompt_context.context.activity.text)['from_date']).date()
                    # From date can't be earlier than 1900
                    if from_date.year < 1900:
                        return False
                    # From date can't be higher than today's date
                    if from_date > pd.to_datetime('today').date():
                        return False
                # From_date should not be null value
                else:
                    return False             
            except:
                return False
            
            try:
                if json.loads(prompt_context.context.activity.text)['to_date'] != "":
                    to_date = pd.to_datetime(json.loads(prompt_context.context.activity.text)['to_date']).date()
                    
                    # from_date can't be greater than to_date... 
                    if from_date > to_date:
                        return False
                    # from_date and to_date can't be higher than today's date
                    elif from_date > pd.to_datetime('today').date() and to_date > pd.to_datetime('today').date():
                        return False
                    # From date can't be higher than today's date
                    elif from_date > pd.to_datetime('today').date():
                        return False
                    # To date can't be higher than today's date
                    elif to_date > pd.to_datetime('today').date():
                        return False
            except: 
                pass

            try:
                # after validating dates as above, we validate the usertext value entered by the user...
                # if both validations are passed, then we return True.
                if json.loads(prompt_context.context.activity.text)["userText"]!= "": 
                    return True and qsm.validate_headcount_text(prompt_context.context.activity.value['userText'])
                else: 
                    return False
            except:
                return False
        elif prompt_context.context.activity.value['action'] == 'cancel':
            return True

    @staticmethod
    async def date_prompt_validator2(prompt_context: PromptValidatorContext) -> bool:
        try:
            print(prompt_context.recognized.succeeded)
            print(prompt_context.context.activity.text)
            print(json.loads(prompt_context.context.activity.text))
            print(prompt_context.context.activity.value['action'])
        except:
            return False
        
        if prompt_context.context.activity.value['action'] == 'submit':
            try:
                if json.loads(prompt_context.context.activity.text)['from_date'] != "":
                    from_date = pd.to_datetime(json.loads(prompt_context.context.activity.text)['from_date']).date()
                    # From date can't be earlier than 1900
                    if from_date.year < 1900:
                        return False
                    # From date can't be higher than today's date
                    if from_date > pd.to_datetime('today').date():
                        return False
                else:
                    # From_date should not be null value
                    return False           
            except:
                return False
            
            try:
                if json.loads(prompt_context.context.activity.text)['to_date'] != "":
                    to_date = pd.to_datetime(json.loads(prompt_context.context.activity.text)['to_date']).date()
                    
                    # From date can't be higher than to date
                    if from_date > to_date:
                        return False
                    # From date and to date can't be higher than today's date
                    elif from_date > pd.to_datetime('today').date() and to_date > pd.to_datetime('today').date():
                        return False
                    # From date can't be higher than today's date
                    elif from_date > pd.to_datetime('today').date():
                        return False
                    # To date can't be higher than today's date
                    elif to_date > pd.to_datetime('today').date():
                        return False
            except: 
                pass
            return True
        elif prompt_context.context.activity.value['action'] == 'cancel':
            return True

    @staticmethod
    async def text_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        try:
            print(prompt_context.recognized.succeeded)
            print(prompt_context.context.activity.text)
            print(json.loads(prompt_context.context.activity.text))
            print(prompt_context.context.activity.value['action'])
        except:
            return False

        if prompt_context.context.activity.value['action'] == 'submit':
            try:
                # Here we validate the value entered by the user in the text box of adpative card prompted...
                return (prompt_context.recognized.succeeded
                        and qsm.validate_headcount_text(prompt_context.context.activity.value['userText']))
            except:
                return False
        elif prompt_context.context.activity.value['action'] == 'cancel':
            return True

    # This method returns headcount choices card as attachment
    def headcount_choice_card(self) -> Attachment:
        card_data = headcount_choices_select    
        return CardFactory.adaptive_card(card_data)

    # This method returns get input text card as attachment
    def get_input_text_card(self, criteria1) -> Attachment:
        card_data = copy.deepcopy(get_input_text)  
        # we design the body of the adpative card based on user choices in dropdown bar...
        card_data['body'][0]["text"] = text_criteria[criteria1][0]
        card_data['body'][1]["columns"][0]["items"][0]["text"] = text_criteria[criteria1][1]
        card_data['body'][1]["columns"][1]["items"][0]["placeholder"] = text_criteria[criteria1][2]
        
        return CardFactory.adaptive_card(card_data) 

    # This method returns get input text retry card as attachment
    def get_input_text_retry_card(self, criteria1) -> Attachment:
        card_data = copy.deepcopy(get_input_text)  
        # we design the body of the adpative card based on user choices in dropdown bar...
        card_data['body'][0]["text"] = text_criteria[criteria1][3]
        card_data['body'][1]["columns"][0]["items"][0]["text"] = text_criteria[criteria1][1]
        card_data['body'][1]["columns"][1]["items"][0]["placeholder"] = text_criteria[criteria1][2]
        
        return CardFactory.adaptive_card(card_data) 

    # we design the dates adaptive card here...
    def get_hire_dates_card(self, criteria1) -> Attachment:
        card_data = copy.deepcopy(get_hire_dates)

        if criteria1 == "0":
            card_data['body'].pop(0)
            card_data['body'].pop(0)

            return CardFactory.adaptive_card(card_data)

        card_data['body'][0]["text"] = text_criteria[criteria1][0]
        card_data['body'][1]["columns"][0]["items"][0]["text"] = text_criteria[criteria1][1]
        card_data['body'][1]["columns"][1]["items"][0]["placeholder"] = text_criteria[criteria1][2]

        return CardFactory.adaptive_card(card_data)

    def get_hire_dates_retryprompt_card(self, criteria1) -> Attachment:
        card_data = copy.deepcopy(get_hire_dates_retryprompt) 

        if criteria1 == "0":
            card_data['body'].pop(0)
            card_data['body'].pop(0)

            return CardFactory.adaptive_card(card_data)

        card_data['body'][0]["text"] = text_criteria[criteria1][3]
        card_data['body'][1]["columns"][0]["items"][0]["text"] = text_criteria[criteria1][1]
        card_data['body'][1]["columns"][1]["items"][0]["placeholder"] = text_criteria[criteria1][2]
        return CardFactory.adaptive_card(card_data)

    def get_termination_dates_card(self, criteria1) -> Attachment:
        card_data = copy.deepcopy(get_termination_dates)

        if criteria1 == "0":
            card_data['body'].pop(0)
            card_data['body'].pop(0)

            return CardFactory.adaptive_card(card_data)

        card_data['body'][0]["text"] = text_criteria[criteria1][0]
        card_data['body'][1]["columns"][0]["items"][0]["text"] = text_criteria[criteria1][1]
        card_data['body'][1]["columns"][1]["items"][0]["placeholder"] = text_criteria[criteria1][2]

        return CardFactory.adaptive_card(card_data)

    def get_termination_dates_retryprompt_card(self, criteria1) -> Attachment:
        card_data = copy.deepcopy(get_termination_dates_retryprompt)  

        if criteria1 == "0":
            card_data['body'].pop(0)
            card_data['body'].pop(0)

            return CardFactory.adaptive_card(card_data)

        card_data['body'][0]["text"] = text_criteria[criteria1][3]
        card_data['body'][1]["columns"][0]["items"][0]["text"] = text_criteria[criteria1][1]
        card_data['body'][1]["columns"][1]["items"][0]["placeholder"] = text_criteria[criteria1][2]

        return CardFactory.adaptive_card(card_data)

    # we design the results card here in this function...
    def headcount_None_records_card(self, card_details: dict, criteria1, criteria2) -> Attachment:
        card_data = copy.deepcopy(headcount_None_records)
        # we modify the text blocks in adaptive card based on the results of the query...
        if card_details["count"] == "0":
            if criteria1 == "0":
                card_data['body'][0]['text'] = "Total HeadCount (HC) of " + data_columns_3[criteria2] + " is:" 
            else:   
                card_data['body'][0]['text'] = "Total HeadCount (HC) of " + data_columns_3[criteria2] + " by " +data_columns_2[criteria1] + " is:"
            
            card_data['body'][1]['text'] = "No records found"

            return CardFactory.adaptive_card(card_data)     

        else:
            if criteria1 == "0":
                card_data['body'][0]['text'] = "Total HeadCount (HC) of " + data_columns_3[criteria2] + " is:" 
            else:   
                card_data['body'][0]['text'] = "Total HeadCount (HC) of " +  data_columns_3[criteria2] + " by " +data_columns_2[criteria1] + " is:"
            
            card_data['body'][1]['text'] = card_details["count"] + " is the HeadCount"
            print(card_data)
            return CardFactory.adaptive_card(card_data)
            
    # we design the results card here in this function...
    def headcount_records_card(self, card_details: dict, criteria1, criteria2) -> Attachment:
        card_data = copy.deepcopy(headcount_records)
        if card_details == {}:
            if criteria1 == "0":
                card_data['body'][0]['text'] = "Total HeadCount (HC) of  " + data_columns_3[criteria2] + " is:" 
            else:   
                card_data['body'][0]['text'] = "Total HeadCount (HC) of " + data_columns_3[criteria2] + " by " +data_columns_2[criteria1] + " is:"

            card_data['body'][1]['text'] = "No records found"
            return CardFactory.adaptive_card(card_data)
        else:
            if criteria1 == "0":
                card_data['body'][0]['text'] = "Total HeadCount (HC) of " + data_columns_3[criteria2] + " is:" 
            else:
                card_data['body'][0]['text'] = "Total HeadCount (HC) of " + data_columns_3[criteria2] + " by " +data_columns_2[criteria1] + " is:"

            for key, value in card_details.items():
                if "None" in str(value) or "" == str(value):
                    value = "Others"
                try:
                    card_data['body'][1]['text'] = str(int(key)) + " HC for " + data_columns_2[criteria1] + " : " + str(value)
                except:
                    card_data['body'][1]['text'] = str(key) + " HC for " + data_columns_2[criteria1] + " : " + str(value)
            
            print(card_data)
            return CardFactory.adaptive_card(card_data)
