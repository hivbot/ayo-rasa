
# This file contains the Voiceflow custom action
# which is used to connect a rasa project to the VF Dialog Manager
# using VF's stateless API (https://www.voiceflow.com/api/dialog-manager#tag/Stateless-API)
#
# Docs on Rasa's custom actions:
# https://rasa.com/docs/rasa/custom-actions
#
# Steps to test:
# 1. Generate a VF API Key and assign it to the "token" variable in this file
# 2. Start the custom actions server: "rasa run actions"
# 3. Remove the comment on the "action_endpoint" field in "endpoints.yml". The url must match with where the rasa custom actions server is running
# 4. Train the rasa project: "rasa train"
# 5. Open the rasa shell: "rasa shell"
# 6. Interact with the rasa project. The returned responses will correspond with speak steps in the Voiceflow project

import json
import requests

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import os


endpoint = "https://general-runtime.voiceflow.com/interact/627ec1a15c8725001cfcf876"

# https://www.voiceflow.com/api/dialog-manager#section/Authentication
token = os.environ.get("VF_API_KEY")

class StateManager:
    state = None

    def get(self):
        if (self.state == None):
            r = requests.get(endpoint + "/state", headers = {"authorization": token})
            self.state = r.json()

        return self.state

    def set(self, s):
        self.state = s

state_manager = StateManager()

def generate_entities(slots):
    entities = []

    for key, value in slots.items():
        if (value is None):
            continue
        slot = {"name": key, "value": value}
        entities.append(slot)

    return entities

def build_request(intent_name, entities):
    return {
            "type": "intent",
            "payload": {
                "query": "",
                "intent": {
                    "name": intent_name
                },
                "entities": entities
            }
        }

def parse_slate_content(slate_content):
  ret = ""
  for index, slate_content_item in enumerate(slate_content):
    if "children" in slate_content_item:
      cur_str = ""
      for child in slate_content_item["children"]:
        if "text" in child:
          cur_str += child["text"]
        elif "url" in child:
          cur_str += child["url"]

      # if empty string, it represents a new line
      if cur_str == "":
        ret += "\n"
      else:
        ret += cur_str

      # Add new line for all lines except for last message
      if index != len(slate_content) - 1:
        ret += "\n"

  return ret

class ActionVoiceflowDM(Action):

    def name(self) -> Text:
        return "action_voiceflow_dm"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        curr_state = tracker.current_state()

        intent_name = curr_state["latest_message"]["intent"]["name"]
        entities = generate_entities(curr_state["slots"])

        request = build_request(intent_name, entities)

        data = { "request": request, "state": state_manager.get() }

        r = requests.post(endpoint, json = data, headers = { "authorization": token })
        response = r.json()

        state_manager.set(response["state"])

        for trace in response["trace"]:
            if (trace["type"] == "speak"):
                dispatcher.utter_message(text=trace["payload"]["message"])
            elif (trace["type"] == "text"):
                dispatcher.utter_message(text=parse_slate_content(trace["payload"]["slate"]["content"]))
        return []
