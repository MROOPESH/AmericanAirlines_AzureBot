# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import MessageFactory, TurnContext
from botbuilder.schema import ChannelAccount
from .dialog_bot import DialogBot

from botbuilder.schema import Activity, ActivityTypes, Attachment
from botbuilder.core import CardFactory
from dialogs.resources.main_menu_card import main_menu_options

class RichCardsBot(DialogBot):
    
    def __init__(self, conversation_state, user_state, dialog):
        super().__init__(conversation_state, user_state, dialog)

    # when a member is added to chat, this method is executed... 
    async def on_members_added_activity(
        self, members_added: ChannelAccount, turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                # welcome message
                reply = MessageFactory.text(
                    "Welcome to American Airlines - People Analytics" + "\n\n" + "Employee Data Distribution Interface."
                )
                await turn_context.send_activity(reply)
                # Along with welcome message, main menu card is also shown to the user
                # so that the user can start the conversation by choosing the choices in adaptive card...
                # message is the main menu card...
                message = Activity(
                    type=ActivityTypes.message,
                    attachments=[self.main_menu_options_card()],
                )        
                await turn_context.send_activity(message)
                await turn_context.send_activity("If your query is not listed in above options please refer this [LINK](https://newjetnet.aa.com/community/people-analytics)")
                

    # This method returns a main menu adaptive card as attachment to the above message activity
    def main_menu_options_card(self) -> Attachment:
        card_data = main_menu_options    
        return CardFactory.adaptive_card(card_data)
