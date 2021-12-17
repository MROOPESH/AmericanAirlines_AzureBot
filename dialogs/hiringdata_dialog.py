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
from .resources.Hiringdata_cards.hiringdata_choices import hiringdata_choices
from .resources.Hiringdata_cards.hiringdata_requisition_choices import hiringdata_rqstn_choices
from .resources.Hiringdata_cards.hiringdata_application_choices import hiringdata_application_choices
from .resources.Hiringdata_cards.get_rqstn_id_card import get_rqstn_id
from .resources.Hiringdata_cards.get_rqstn_id_retry_card import get_rqstn_id_retry

from .resources.Hiringdata_cards.get_hiring_dates_card import get_hiring_dates
from .resources.Hiringdata_cards.get_hiring_dates_retryprompt_card import get_hiring_dates_retryprompt

from .resources.Hiringdata_cards.count_of_rqstn_criteria_card import count_of_rqstn_criteria
from .resources.Hiringdata_cards.rqstn_details_card import rqstn_details
from .resources.Hiringdata_cards.count_of_rqstn_by_status_card import count_of_rqstn_by_status
from .resources.Hiringdata_cards.top_10_application_status_card import top_10_application_status

import json
import pandas as pd
from query_sql_mi import QuerySQLMI
import os 
import copy

# These are used to create adaptive cards to get user input...
rqstn_data_columns = {
    "md_nm" : "Managing Director",
    "vp_nm" : "Vice President",
    "svp_nm" : "Sr.Vice President",
    "svp2_nm" : "Sr.Vice President2",
    "svp3_nm" : "Sr.Vice President3"
}

appl_data_columns = {
    "md_name" : "Managing Director",
    "vp_name" : "Vice President",
    "svp_name" : "Sr.Vice President",
    "svp2_name" : "Sr.Vice President2",
    "svp3_name" : "Sr.Vice President3",
    "job_division" : "Job Division",
    "job_catg" : "Job Category",
    "work_loc" : "Work Location",
    "evp_name" : "Executive Vice President Name"
}

text_criteria = {
    "job_division" : ["Enter the job division", "Job Division:", "Eg. Air Ops", "Please check and re-enter a valid job division"],
    "job_catg" : ["Enter the job category", "Job Category:", "Eg. Flight Attendants", "Please check and re-enter a valid job category"],
    "work_loc" : ["Enter the Work Location", "Work Location:", "Eg. Training & Conf Ctr (DFW-TRCC)", "Please check and re-enter a valid work location"],
    "vp_name" : ["Enter the Vice President Name", "Vice President Name:", "Eg. Last name, First name", "Please check and re-enter a valid vice president name"],
    "md_name" : ["Enter the Managing Director Name", "Managing Director:", "Eg. Last name, First name", "Please check and re-enter a valid Managing Director Name"],
    "svp_name" : ["Enter the Senior Vice President Name", "Sr Vice President Name:", "Eg. Last name, First name", "Please check and re-enter a valid Senior Vice President Name"],
    "svp2_name" : ["Enter the Senior Vice President2 Name", "Sr Vice President2 Name:", "Eg. Last name, First name", "Please check and re-enter a valid Senior Vice President2 Name"],
    "svp3_name" : ["Enter the Senior Vice President3 Name", "Sr Vice President3 Name:", "Eg. Last name, First name", "Please check and re-enter a valid Senior Vice President3 Name"],
    "evp_name" : ["Enter the Executive Vice President Name", "Executive Vice President Name:", "Eg. Last name, First name", "Please check and re-enter a valid Executive Vice President Name"]
}

class HiringdataDialog(ComponentDialog):
    def __init__(self, dialog_id: str):
        super(HiringdataDialog, self).__init__(dialog_id or HiringdataDialog.__name__)
        global qsm
        qsm = QuerySQLMI()

        self.add_dialog(NumberPrompt(NumberPrompt.__name__, HiringdataDialog.rqstn_id_validator))
        self.add_dialog(TextPrompt("textprompt1", HiringdataDialog.appl_text_date_validator1))
        self.add_dialog(TextPrompt("textprompt2", HiringdataDialog.appl_text_date_validator2))
        self.add_dialog(
            WaterfallDialog(
                "WFDialog",
                [
                    self.hiringdata_choice_step,
                    self.hiringdata_choice_step2,
                    self.get_input_step,
                    self.output_step
                ],
            )
        )
        
        self.initial_dialog_id = "WFDialog"

    async def hiringdata_choice_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        # In this step, we put the hiring data choices to the user...
        message = Activity(
            type=ActivityTypes.message,
            attachments=[self.hiringdata_choices_card()],
        )        
        await step_context.context.send_activity(message)
        return DialogTurnResult(status=DialogTurnStatus.Waiting,result={})

    async def hiringdata_choice_step2(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        try:
            # we store the user chosen value from the drop down choice and store it in step_context.values["hiringdata_choice"]
            step_context.values["hiringdata_choice"] = json.loads(step_context.context.activity.text)
        except:
            return await step_context.end_dialog()
        try:
            # Requisition data
            # Application Status
            if step_context.values["hiringdata_choice"]["SelectVal"] == "requisition_data":
                message = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.hiringdata_rqstn_choices_card()],
                )        
                await step_context.context.send_activity(message)
                return DialogTurnResult(status=DialogTurnStatus.Waiting,result={})

            elif step_context.values["hiringdata_choice"]["SelectVal"] == "application_status":
                message = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.hiringdata_application_choices_card()],
                )
                await step_context.context.send_activity(message)
                return DialogTurnResult(status=DialogTurnStatus.Waiting,result={})
        except:
            return await step_context.end_dialog()

    # In this step, we get the input dates and the user input for the criteria chosen...
    async def get_input_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        # we store the option chosen by the user in the step_context variables as below...
        try:
            if step_context.values["hiringdata_choice"]["SelectVal"] == "requisition_data":       
                step_context.values["hiringdata_rqstn_choice"] = json.loads(step_context.context.activity.text)
                
            elif step_context.values["hiringdata_choice"]["SelectVal"] == "application_status":
                step_context.values["hiringdata_application_choice"] = json.loads(step_context.context.activity.text)

        except:
            return await step_context.end_dialog()

        try:
            # if user chosen "Cancel to go to main menu", then we end the dialog...
            if step_context.values["hiringdata_choice"]["SelectVal"] == "requisition_data":   
                if step_context.values["hiringdata_rqstn_choice"]["action"] == "menucancel":
                    return await step_context.end_dialog()

            if step_context.values["hiringdata_choice"]["SelectVal"] == "application_status":
                if step_context.values["hiringdata_application_choice"]["action"] == "menucancel":
                    return await step_context.end_dialog()

            if step_context.values["hiringdata_choice"]["SelectVal"] == "requisition_data":
                # if user chooses Search details by Requisition ID...
                if step_context.values["hiringdata_rqstn_choice"]["SelectVal_rqstn"] == "search_by_req_id":
                    message = Activity(
                        type=ActivityTypes.message,
                        attachments=[self.get_rqstn_id_card()],
                    )                    
                    message1 = Activity(
                        type=ActivityTypes.message,
                        attachments=[self.get_rqstn_id_retry_card()],
                    )
                    await step_context.prompt(
                        NumberPrompt.__name__,
                        PromptOptions(
                            prompt=message,
                            retry_prompt=message1,
                        ),
                    )
                    return DialogTurnResult(status=DialogTurnStatus.Waiting,result={})
                elif step_context.values["hiringdata_rqstn_choice"]["SelectVal_rqstn"] == "count_of_rqstn_by_status":
                    # if user chooses Count of Requisitions by status...
                    message = Activity(
                        type=ActivityTypes.message,
                        attachments=[self.count_of_rqstn_criteria_card()],
                    )        
                    await step_context.context.send_activity(message)
                    return DialogTurnResult(status=DialogTurnStatus.Waiting,result={})
            elif step_context.values["hiringdata_choice"]["SelectVal"] == "application_status":
                # if user chooses application status option, then we provide a drop down choice to choose the criteria...
                message = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.get_hiring_dates_card(step_context.values["hiringdata_application_choice"]["SelectVal_application"])],
                )
                message1 = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.get_hiring_dates_retryprompt_card(step_context.values["hiringdata_application_choice"]["SelectVal_application"])],
                )
                if step_context.values["hiringdata_application_choice"]["SelectVal_application"] == "none":
                    await step_context.prompt(
                        "textprompt1",
                        PromptOptions(
                            prompt=message,
                            retry_prompt=message1,
                        ),
                    )
                else:
                    await step_context.prompt(
                        "textprompt2",
                        PromptOptions(
                            prompt=message,
                            retry_prompt=message1,
                        ),
                    )
                return DialogTurnResult(status=DialogTurnStatus.Waiting,result={})
        except:
            return await step_context.end_dialog()

    async def output_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        try:
            if step_context.values["hiringdata_choice"]["SelectVal"] == "requisition_data":
                if step_context.values["hiringdata_rqstn_choice"]['SelectVal_rqstn'] == "search_by_req_id":                
                    if step_context.context.activity.value['action'] == 'cancel':
                        return await step_context.end_dialog()
                    # we get the user input and store it in the step_context variable...
                    step_context.values["rqstn_id"] = step_context.result
                    ans = qsm.hiringdata_details(int(step_context.values["rqstn_id"]))
                    message = Activity(
                        type=ActivityTypes.message,
                        attachments=[self.rqstn_details_factset_card(ans)],
                    )
                    await step_context.context.send_activity(message)
                    return await step_context.end_dialog()

                elif step_context.values["hiringdata_rqstn_choice"]['SelectVal_rqstn'] == "count_of_rqstn_by_status":
                    if step_context.context.activity.value['action'] == 'menucancel':
                        return await step_context.end_dialog()

                    step_context.values["count_of_requisitions_criteria"] = json.loads(step_context.context.activity.text)
                    ans = qsm.hiringdata_countofrqstn(step_context.values["count_of_requisitions_criteria"]["criteria1"], step_context.values["count_of_requisitions_criteria"]["criteria2"])
                    print(ans)
                    message = Activity(
                        type=ActivityTypes.message,
                        attachments=[self.count_of_rqstn_results_card(ans, step_context.values["count_of_requisitions_criteria"]["criteria1"], step_context.values["count_of_requisitions_criteria"]["criteria2"])],
                    )                   
                    await step_context.context.send_activity(message)
                    return await step_context.end_dialog()

            elif step_context.values["hiringdata_choice"]["SelectVal"] == "application_status":
                if step_context.context.activity.value['action'] == "cancel":
                    return await step_context.end_dialog() 
                step_context.values["get_hiring_dates"] = json.loads(step_context.context.activity.text)
                
                from_date = step_context.values["get_hiring_dates"]["from_date"]
                #to_date = step_context.values["get_hiring_dates"]["to_date"]
                try:
                    # Since, to_date is optional, it is stored in variable as follows...
                    if step_context.values["get_hiring_dates"]['to_date'] != "":
                        to_date = step_context.values["get_hiring_dates"]['to_date']
                    else:
                        # if to_date entered is null, then to_date is ""...
                        to_date = ""
                except:
                    to_date = ""                
                if step_context.values["hiringdata_application_choice"]["SelectVal_application"] == "none":
                    ans = qsm.hiringdata_application_status_None(from_date, to_date)
                else:
                    ans = qsm.hiringdata_application_status(step_context.values["hiringdata_application_choice"]["SelectVal_application"], step_context.values["get_hiring_dates"]["userText"], from_date, to_date)                
                
                message = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.top_10_application_status_card(ans, step_context.values["hiringdata_application_choice"]["SelectVal_application"])],
                )                   
                await step_context.context.send_activity(message)                
                return await step_context.end_dialog()

            return await step_context.end_dialog()
        except:         
            return await step_context.end_dialog()


    @staticmethod
    async def rqstn_id_validator(prompt_context: PromptValidatorContext) -> bool:
        # This validator method validates whether the user entered requisition id is a valid id or not...
        try:
            print(prompt_context.context.activity.text)
            print(json.loads(prompt_context.context.activity.text))
            print(prompt_context.context.activity.value['action'])
        except:
            return False
        if prompt_context.context.activity.value['action'] == 'submit':
            try:
                # validate_rqstn_id is a method in query_sql_mi.py
                return (
                    prompt_context.recognized.succeeded
                    and qsm.validate_rqstn_id(int(prompt_context.context.activity.value['rqstn_id']))
                )
            except:
                return False
        elif prompt_context.context.activity.value['action'] == 'cancel':
            return True

    @staticmethod
    async def appl_text_date_validator1(prompt_context: PromptValidatorContext) -> bool:
        # This validator validates the usertext and dates whether they are valid dates or not...
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
            return True

        elif prompt_context.context.activity.value['action'] == 'cancel':
            return True

    @staticmethod
    async def appl_text_date_validator2(prompt_context: PromptValidatorContext) -> bool:
        # This validator validates the usertext and dates whether they are valid dates or not...
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
                    print("validate_appl_status_text method") 
                    return True and qsm.validate_appl_status_text(prompt_context.context.activity.value['userText'])
                else: 
                    return False
            except:
                return False
            
        elif prompt_context.context.activity.value['action'] == 'cancel':
            return True

    def hiringdata_choices_card(self) -> Attachment:
        card_data = hiringdata_choices    
        return CardFactory.adaptive_card(card_data)

    def hiringdata_rqstn_choices_card(self) -> Attachment:
        card_data = hiringdata_rqstn_choices    
        return CardFactory.adaptive_card(card_data)

    def hiringdata_application_choices_card(self) -> Attachment:
        card_data = hiringdata_application_choices    
        return CardFactory.adaptive_card(card_data)

    def get_rqstn_id_card(self) -> Attachment:
        card_data = get_rqstn_id    
        return CardFactory.adaptive_card(card_data)

    def get_rqstn_id_retry_card(self) -> Attachment:
        card_data = get_rqstn_id_retry    
        return CardFactory.adaptive_card(card_data)

    def count_of_rqstn_criteria_card(self) -> Attachment:
        card_data = count_of_rqstn_criteria    
        return CardFactory.adaptive_card(card_data)

    # we design the dates adaptive card here...
    def get_hiring_dates_card(self, criteria1) -> Attachment:
        card_data = copy.deepcopy(get_hiring_dates)

        if criteria1 == "none":
            card_data['body'].pop(0)
            card_data['body'].pop(0)

            return CardFactory.adaptive_card(card_data)
        
        card_data['body'][0]["text"] = text_criteria[criteria1][0]
        card_data['body'][1]["columns"][0]["items"][0]["text"] = text_criteria[criteria1][1]
        card_data['body'][1]["columns"][1]["items"][0]["placeholder"] = text_criteria[criteria1][2]
        
        return CardFactory.adaptive_card(card_data)

    def get_hiring_dates_retryprompt_card(self, criteria1) -> Attachment:
        card_data = copy.deepcopy(get_hiring_dates_retryprompt) 

        if criteria1 == "none":
            card_data['body'].pop(0)
            card_data['body'].pop(0)

            return CardFactory.adaptive_card(card_data)
        
        card_data['body'][0]["text"] = text_criteria[criteria1][3]
        card_data['body'][1]["columns"][0]["items"][0]["text"] = text_criteria[criteria1][1]
        card_data['body'][1]["columns"][1]["items"][0]["placeholder"] = text_criteria[criteria1][2]
        
        return CardFactory.adaptive_card(card_data)

    def rqstn_details_factset_card(self, card_details: dict) -> Attachment:
        card_data = rqstn_details    
        for i, value in enumerate(card_details.values()):
            card_data['body'][1]['facts'][i]['value'] = str(value).upper()  
        return CardFactory.adaptive_card(card_data)
    
    def count_of_rqstn_results_card(self, card_details: dict, criteria1, criteria2) -> Attachment:
        card_data = copy.deepcopy(count_of_rqstn_by_status)
        if card_details == {}:
            for i in range(9-len(card_details)):
                card_data['body'].pop()
            try:
                card_data['body'][0]['text'] = "Total count of Requisition for " + criteria1 + " status by " + rqstn_data_columns[criteria2] + " is:"
                card_data['body'][1]['text'] = "No records found"
            except Exception as e:
                print(e)
            return CardFactory.adaptive_card(card_data)
        else:
            card_data['body'][0]['text'] = "Total count of Requisition for " + criteria1 + " status by " + rqstn_data_columns[criteria2] + " is:"
            print(card_data)
            for i in range(10-len(card_details)):
                card_data['body'].pop()
            print(card_data)
            count = 0
            for key, value in card_details.items():
                if "None" in str(key) or "" == str(key):
                    key = "Others"
                try:
                    card_data['body'][count+1]['text'] = str(key) + " has " + str(int(value)) + " Requisitions"
                except:
                    card_data['body'][count+1]['text'] = str(key) + " has " + str(value) + " Requisitions"
                count = count + 1
            print(card_data)
            return CardFactory.adaptive_card(card_data)

    # This method returns top 10 application status results card...
    def top_10_application_status_card(self, card_details: dict, criteria) -> Attachment:
        # we deepcopy the top_10_application_status dictionary...
        card_data = copy.deepcopy(top_10_application_status)
        # card_details is the result we get on performing the query. We fit card with these details.
        if card_details == {}:
            # if card_details are empty...
            # then, we pop the text blocks from body of adaptive card as there were no values to fit...
            for i in range(9-len(card_details)):
                card_data['body'].pop()
            if criteria == "none":
                card_data['body'][0]['text'] = "Total Count by Application Status is:"
            else:
                card_data['body'][0]['text'] = "Total Count of " + appl_data_columns[criteria] + " by Application Status is:"
            card_data['body'][1]['text'] = "No records found"

            return CardFactory.adaptive_card(card_data)
        else:
            if criteria == "none":
                card_data['body'][0]['text'] = "Total Count by Application Status is:"
            else:
                card_data['body'][0]['text'] = "Total Count of " + appl_data_columns[criteria] + " by Application Status is:"
            # If there are not 10 results in card_details, then we pop out the unnecessary text blocks from Top 10 Application status adpative card
            for i in range(10-len(card_details)):
                card_data['body'].pop()

            count = 0
            for key, value in card_details.items():
                if "None" == str(value) or "" == str(value):
                    value = "Others"
                
                try:
                    card_data['body'][count+1]['text'] = str(int(key)) + " count for Application Status: " + str(value)
                except:
                    card_data['body'][count+1]['text'] = str(key) + " count for Application Status: " + str(value)
                count = count + 1

            return CardFactory.adaptive_card(card_data)