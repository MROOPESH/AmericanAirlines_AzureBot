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

from botbuilder.dialogs.prompts import PromptOptions, ActivityPrompt, TextPrompt, NumberPrompt, DateTimePrompt, ChoicePrompt, PromptOptions, PromptValidatorContext
from .resources.Insights_choices_card.top10search_choices_card import top10search_choices
from .resources.Insights_choices_card.top10search_choices_retry_card import top10search_choices_retry
from .resources.Insights_choices_card.insights_choice import insights_choices
from .resources.Insights_choices_card.get_hire_dates import get_hire_dates
from .resources.Insights_choices_card.get_hire_dates_retryprompt import get_hire_dates_retryprompt
from .resources.Insights_choices_card.get_termination_dates import get_termination_dates
from .resources.Insights_choices_card.get_termination_dates_retryprompt import get_termination_dates_retryprompt
from .resources.Insights_choices_card.top_10_locations_factset import top_10_locations_factset

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
    "8" : "vp_name",
    "9" : "termination_ind"
}

data_columns_2 = {
    "1" : "Cost Center",
    "2" : "Department Unit",
    "3" : "Division",
    "4" : "Location",
    "5" : "MD",
    "6" : "Reporting Workgroup",
    "7" : "Sr.VP ",
    "8" : "VP",
    "9" : "Termination Reason"
}

data_columns_3 = {
    "1" : " active employees",
    "2" : " hires by hire date",
    "3" : " terminations by termination date"
}


class InsightsDialog(ComponentDialog):
    def __init__(self, dialog_id: str):
        super(InsightsDialog, self).__init__(dialog_id or InsightsDialog.__name__)
        # qsm is the object for QuerySQLMI class in query_sql_mi.py file...
        global qsm
        qsm = QuerySQLMI()
        # date_prompt_validator is a validator for the input given by user in input box...
        # the date entered by the user for Insights query is validated whether that date is present in database

        #self.add_dialog(TextPrompt(TextPrompt.__name__, InsightsDialog.date_prompt_validator))
        #self.add_dialog(NumberPrompt(NumberPrompt.__name__))
        self.add_dialog(DateTimePrompt(DateTimePrompt.__name__, InsightsDialog.date_prompt_validator))
        self.add_dialog(ActivityPrompt("criteriavalidation", InsightsDialog.criteria_prompt_validator))
        
        # The 4 waterfall steps are defined  
        self.add_dialog(
            WaterfallDialog(
                "WFDialog",
                [
                    self.choose_insights_step,
                    self.top10search_choice_step,
                    self.get_dates_step,
                    self.output_step,
                ],
            )
        )
        
        self.initial_dialog_id = "WFDialog"

    async def choose_insights_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        print(step_context.context.activity.text)
        # When a user chooses Insights option in HR/People Data... 
        # Insights choices(criteria) card is put to the user...   
        message = Activity(
            type=ActivityTypes.message,
            attachments=[self.insights_choice_card()],
        )        
        await step_context.context.send_activity(message)
        return DialogTurnResult(status=DialogTurnStatus.Waiting,result={})

    async def top10search_choice_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        try:
            # The user choice from insights_choice_card adaptive card is stored in "insights_choices" as below... 
            step_context.values["insights_choices"] = json.loads(step_context.context.activity.text)
        except:
            # if a user enters some text in chat instead of choosing choice from insights_choice_card adaptive card...
            # then in that case the dialog ends. 
            return await step_context.end_dialog()
        try:
            # if user clicks on "Cancel to go to main menu", then the dialog ends
            if step_context.values["insights_choices"]["action"] == "menucancel":
                return await step_context.end_dialog()

            print(step_context.context.activity.text)

            step_context.values["insights_choices"] = json.loads(step_context.context.activity.text)
            if step_context.values["insights_choices"]["insights_choice_val"] == "top10search":
                # if the user chooses Top 10 Search...
                # then, the top 10 search choices card is put to the user...
                # if the user chooses "Termination Reason" with other than "No. of Terminations by Termination Date",
                # then that is a wrong choice, and the retry card is put to the user through message1...
                message = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.top10search_choice_card()],
                )        
                message1 = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.top10search_choice_retryprompt_card()],
                )  
                return await step_context.prompt(
                    "criteriavalidation",
                    PromptOptions(
                        prompt=message,
                        retry_prompt=message1,
                    ),
                )
            
            elif step_context.values["insights_choices"]["insights_choice_val"] == "averageofrecords":
                print("avergeofrecords")
                await step_context.context.send_activity(MessageFactory.text("*** Work is in progress... ***"))
                return await step_context.begin_dialog(InsightsDialog.__name__)              
        except:
            # if there is any exception arises, we begin the Insights dialog from beginning... 
            return await step_context.begin_dialog(InsightsDialog.__name__)

    async def get_dates_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        try:
            if step_context.values["insights_choices"]["insights_choice_val"] == "top10search":
                try:
                    print(step_context.context.activity.text)
                    step_context.values["top10search_choices"] = json.loads(step_context.context.activity.text)
                except:
                    return await step_context.begin_dialog(InsightsDialog.__name__)
                try:
                    # if user clicks on "Cancel to go to main menu", then the dialog ends                    
                    if step_context.context.activity.value['action'] == 'menucancel':
                        return await step_context.end_dialog()
                    # if user clicks on cancel button, then we begin the insights dialog...
                    elif step_context.context.activity.value['action'] == 'cancel':
                        return await step_context.begin_dialog(InsightsDialog.__name__)

                    if step_context.values["top10search_choices"]['criteria2'] == '1':
                        # ans is the result for headcount of non-terminated employees query...
                        ans = qsm.insights_non_terminated(data_columns_1[step_context.values["top10search_choices"]['criteria1']])
                        # The results are fitted into top 10 locations card...
                        message = Activity(
                            type=ActivityTypes.message,
                            attachments=[self.top_10_locations_card(ans, step_context.values["top10search_choices"]['criteria1'], step_context.values["top10search_choices"]['criteria2'])],
                        )        
                        await step_context.context.send_activity(message)
                        # At the end of query, we begin the insights dialog again...
                        return await step_context.begin_dialog(InsightsDialog.__name__)

                    elif step_context.values["top10search_choices"]['criteria2'] == '2':
                        # This query is No. of hires by hire date query...
                        message = Activity(
                            type=ActivityTypes.message,
                            attachments=[self.get_hire_dates_card()],
                        )     
                        message_1 = Activity(
                            type=ActivityTypes.message,
                            attachments=[self.get_hire_dates_retryprompt_card()],
                        )
                        await step_context.prompt(
                            DateTimePrompt.__name__,
                            PromptOptions(
                                prompt=message,
                                retry_prompt=message_1,
                            ),
                        )
                        return DialogTurnResult(status=DialogTurnStatus.Waiting,result={})

                    elif step_context.values["top10search_choices"]['criteria2'] == '3':
                        # This query is No. of terminations by termination date query...
                        message = Activity(
                            type=ActivityTypes.message,
                            attachments=[self.get_termination_dates_card()],
                        )
                        message_1 = Activity(
                            type=ActivityTypes.message,
                            attachments=[self.get_termination_dates_retryprompt_card()],
                        )
                        await step_context.prompt(
                            DateTimePrompt.__name__,
                            PromptOptions(
                                prompt=message,
                                retry_prompt=message_1,
                            ),
                        )
                        return DialogTurnResult(status=DialogTurnStatus.Waiting,result={})

                    return await step_context.end_dialog()
                except:
                    return await step_context.end_dialog()
            else:
                return await step_context.end_dialog()
        except:
            return await step_context.end_dialog()


    async def output_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        if step_context.values["insights_choices"]["insights_choice_val"] == "top10search":
            try:
                if step_context.values["top10search_choices"]['criteria2'] == "2":
                    if step_context.context.activity.value['action'] == 'cancel':
                        return await step_context.begin_dialog(InsightsDialog.__name__)

                    step_context.values["get_dates"] = json.loads(step_context.context.activity.text)
                    # The from_date entered by user in adaptive card is stored in from_date as below...
                    from_date = step_context.values["get_dates"]['from_date']
                    #from_date = pd.to_datetime(step_context.values["get_dates"]['from_date'])#.date()
                    try:
                        # Since, to_date is optional, it is stored in variable as follows...
                        if step_context.values["get_dates"]['to_date'] != "":
                            to_date = step_context.values["get_dates"]['to_date']
                        else:
                            # if to_date entered is null, then to_date is ""...
                            to_date = ""
                    except:
                        to_date = ""
                    
                    # ans is the result of no.of hire by hire dates query...
                    ans = qsm.insights_hires_by_hiredate(data_columns_1[step_context.values["top10search_choices"]['criteria1']], from_date, to_date)
                    # The results are fitted into the adaptive card...
                    message = Activity(
                        type=ActivityTypes.message,
                        attachments=[self.top_10_locations_card(ans, step_context.values["top10search_choices"]['criteria1'], step_context.values["top10search_choices"]['criteria2'])],
                    )        
                    await step_context.context.send_activity(message)
                    return await step_context.begin_dialog(InsightsDialog.__name__)

                elif step_context.values["top10search_choices"]['criteria2'] == "3":
                    if step_context.context.activity.value['action'] == 'cancel':
                        return await step_context.begin_dialog(InsightsDialog.__name__)

                    step_context.values["get_dates"] = json.loads(step_context.context.activity.text)
                    from_date = step_context.values["get_dates"]['from_date']
                    #from_date = pd.to_datetime(step_context.values["get_dates"]['from_date'])#.date()
                    try:
                        if step_context.values["get_dates"]['to_date'] != "":
                            to_date = step_context.values["get_dates"]['to_date']
                        else:
                            to_date = ""
                    except:
                        to_date = ""

                    ans = qsm.insights_trmns_by_terminationdate(data_columns_1[step_context.values["top10search_choices"]['criteria1']], from_date, to_date)
                    message = Activity(
                        type=ActivityTypes.message,
                        attachments=[self.top_10_locations_card(ans, step_context.values["top10search_choices"]['criteria1'], step_context.values["top10search_choices"]['criteria2'])],
                    )        
                    await step_context.context.send_activity(message)
                    return await step_context.begin_dialog(InsightsDialog.__name__)

                return await step_context.end_dialog()
            except:
                return await step_context.end_dialog()
        else:
            return await step_context.end_dialog()

    @staticmethod
    async def date_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        try:
            print(prompt_context.recognized.succeeded)
            print(prompt_context.context.activity.text)
            # if the user enters something in chat without choosing date in adaptive card,
            # then that is a wrong input to the bot and in that case, the bot re-prompts the user to choose the date again...
            print(json.loads(prompt_context.context.activity.text))
            print(prompt_context.context.activity.value['action'])
        except:
            # if any exception happens in above statements, then the validator returns False which means the
            return False
        
        # When a user enters a date and clicks on submit, then the following executes...
        if prompt_context.context.activity.value['action'] == 'submit':
            try:
                if json.loads(prompt_context.context.activity.text)['from_date'] != "":
                    # from_date is the user entered from date in adaptive card...
                    from_date = pd.to_datetime(json.loads(prompt_context.context.activity.text)['from_date']).date()
                    if from_date.year < 1900:
                        # From date can't be earlier than 1900...
                        print("From date can't be earlier than 1900")
                        return False

                    if from_date > pd.to_datetime('today').date():
                        # From date can't be greater than today's date...
                        print("From date can't be higher than today's date")
                        return False
                else:
                    # From date can't be a null value
                    print("From_date should not be null value")
                    return False               
            except:
                return False
            
            try:
                if json.loads(prompt_context.context.activity.text)['to_date'] != "":
                    # to_date is the To date entered by the user...
                    to_date = pd.to_datetime(json.loads(prompt_context.context.activity.text)['to_date']).date()
                    
                    # From date can't be greater than To date... 
                    if from_date > to_date:
                        print("From date can't be higher than to date")
                        return False
                    # from_date shouldn't be less than today's date
                    elif from_date > pd.to_datetime('today').date() and to_date > pd.to_datetime('today').date():
                        print("From date and to date can't be higher than today's date")
                        return False
                    # From date can't be greater than today's date...
                    elif from_date > pd.to_datetime('today').date():
                        print("From date can't be higher than today's date")
                        return False
                    # To date can't be higher than today's date...
                    elif to_date > pd.to_datetime('today').date():
                        #await prompt_context.context.send_activity("To date can't be higher than today's date")
                        print("To date can't be higher than today's date")
                        return False
            except: 
                pass
            return True

        elif prompt_context.context.activity.value['action'] == 'cancel':
            # if the user clicks on 'cancel' button, then we return True...
            return True

    @staticmethod
    async def criteria_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        # criteria_prompt_validator does the criteria validation,
        # The combination for criteria "Termination Reason" is validated, 
        try:
            print(prompt_context.recognized.succeeded == True)
            print(prompt_context.context.activity.text)
            # if the user enters something in chat without choosing criteria in adaptive card,
            # then that is a wrong input to the bot and in that case, the bot re-prompts the user to choose the criteria again...
            print(json.loads(prompt_context.context.activity.text))
            print(prompt_context.context.activity.value['action'])
        except:
            return False        

        if prompt_context.context.activity.value['action'] == 'submit':
            try:
                # if the user chooses "Termination Reason" with other than "No. of Terminations by Termination Date" criteria,
                # then that combination is incorrect...
                criteria1 = json.loads(prompt_context.context.activity.text)["criteria1"]
                criteria2 = json.loads(prompt_context.context.activity.text)["criteria2"]
                if criteria1 == "9":
                    if criteria2 == "3":
                        return True
                    else:
                        return False
                else:
                    return True
            except:
                True
        elif prompt_context.context.activity.value['action'] == 'menucancel':
            return True

    # This method returns insights choices card as attachment
    def insights_choice_card(self) -> Attachment:
        card_data = insights_choices    
        return CardFactory.adaptive_card(card_data)

    # This method returns top10search_choices as attachment
    def top10search_choice_card(self) -> Attachment:
        card_data = top10search_choices    
        return CardFactory.adaptive_card(card_data)

    # This method returns top10search_choices_retry as attachment
    def top10search_choice_retryprompt_card(self) -> Attachment:
        card_data = top10search_choices_retry    
        return CardFactory.adaptive_card(card_data)

    # This method returns get hire dates as attachment
    def get_hire_dates_card(self) -> Attachment:
        card_data = get_hire_dates
        return CardFactory.adaptive_card(card_data)

    # This method returns get hire dates retry prompt card as attachment
    def get_hire_dates_retryprompt_card(self) -> Attachment:
        card_data = get_hire_dates_retryprompt    
        return CardFactory.adaptive_card(card_data)

    # This method returns get termination dates as attachment
    def get_termination_dates_card(self) -> Attachment:
        card_data = get_termination_dates    
        return CardFactory.adaptive_card(card_data)

    # This method returns get termination dates retry as attachment
    def get_termination_dates_retryprompt_card(self) -> Attachment:
        card_data = get_termination_dates_retryprompt    
        return CardFactory.adaptive_card(card_data)

    # This method returns top 10 locations results card...
    def top_10_locations_card(self, card_details: dict, criteria1, criteria2) -> Attachment:
        # we deepcopy the top_locations_factset dictionary...
        card_data = copy.deepcopy(top_10_locations_factset)
        # card_details is the result we get on performing the query. We fit card with these details.
        if card_details == {}:
            # if card_details are empty...
            # then, we pop the text blocks from body of adaptive card as there were no values to fit...
            for i in range(9-len(card_details)):
                card_data['body'].pop()

            card_data['body'][0]['text'] = "Total HeadCount (HC) of " +data_columns_3[criteria2] + " by " +data_columns_2[criteria1] + " is:"
            card_data['body'][1]['text'] = "No records found"

            return CardFactory.adaptive_card(card_data)
        else:
            card_data['body'][0]['text'] = "Total HeadCount (HC) of " + data_columns_3[criteria2] + " by " +data_columns_2[criteria1] + " is:"
            # If there are not 10 results in card_details, then we pop out the unnecessary text blocks from Top 10 locations adpative card
            for i in range(10-len(card_details)):
                card_data['body'].pop()

            count = 0
            for key, value in card_details.items():
                if "None" == str(value) or "" == str(value):
                    value = "Others"
                                
                try:
                    card_data['body'][count+1]['text'] = str(int(key)) + " HC for " + data_columns_2[criteria1] + " : " + str(value)
                except:
                    card_data['body'][count+1]['text'] = str(key) + " HC for " + criteria1 + " : " + str(value)
                count = count + 1
            
            return CardFactory.adaptive_card(card_data)

            