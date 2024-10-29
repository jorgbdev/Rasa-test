import os
from typing import Any, Dict, List, Text

import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.events import ConversationPaused, EventType
from rasa_sdk.executor import CollectingDispatcher

import config


class ActionHumanHandover(Action):
    def name(self) -> Text:
        return "action_human_handover"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        dispatcher.utter_message(text="Connecting you to a human representative...")

        # Notify .NET application
        user_id = tracker.sender_id
        endpoint = f"{config.BACKEND_ENDPOINT_URL}/handover"

        try:
            response = requests.post(endpoint, json={"user_id": user_id})
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text="Failed to connect to a human representative.")
            # Log the error
            print(f"Error notifying backend: {e}")
            return []
        except Exception as e:
            dispatcher.utter_message(text="An unexpected error occurred.")
            print(f"Unexpected error: {e}")
            return []
        return [ConversationPaused()]


class ActionFetchInfo(Action):
    def name(self) -> Text:
        return "action_fetch_info"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        theme = tracker.get_slot("theme")
        topic = tracker.get_slot("topic")
        info_type = tracker.get_slot("info_type")

        if not theme:
            dispatcher.utter_message(text="I'm sorry, I need to know the theme you're interested in.")
            return []

        if not topic:
            dispatcher.utter_message(text="Which specific topic would you like to know about?")
            return []

        if not info_type:
            dispatcher.utter_message(
                text=(
                    f"What information would you like to know about {topic}? "
                    "You can ask about location, plans, courses, founded year, "
                    "website, or other details."
                )
            )
            return []

        # Construct the API URL
        api_base_url = os.getenv("BACKEND_ENDPOINT_URL")
        api_endpoint = f"{api_base_url}/api/entries"

        # Define the parameters
        params = {"theme": theme, "topic": topic, "key": info_type}

        try:
            response = requests.get(api_endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            if data:
                value = data.get("value")
                if info_type.lower() == "website":
                    dispatcher.utter_message(text=f"You can visit the website here: {value}")
                else:
                    dispatcher.utter_message(text=value)
            else:
                dispatcher.utter_message(text=f"I'm sorry, I don't have information on {info_type} for {topic}.")
        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text="I'm experiencing some technical difficulties. Please try again later.")
            # Log the error
            print(f"Error fetching info: {e}")
            return []

        # Return an empty list if no events are needed
        return []
