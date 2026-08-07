#!/usr/bin/env python3

from pathlib import Path

class PromptManager:

    def base_prompt(self):

        prompt_path = Path(__file__).parent / "system_prompt.txt"

        with open(prompt_path, "r", encoding="utf-8") as f:
            base_prompt = f.read()

        return base_prompt

    def fmt(self, value):
        if value is None:
            return "Unavailable"
        else:
            return str(value)

    def system_context(self, results):
        SYSTEM_CONTEXT = """
        You are Nyx.
        The text below is verified runtime information collected directly from the user's system.
        Rules:
        - Answer ONLY using the runtime information.
        - Never invent or infer values.
        - Respond naturally.
        - Never reply with "Okay", "Sure", or similar acknowledgements.
        - If the information is missing, reply exactly:
        "The requested information is unavailable."
        Examples:
        Runtime Information:
        CPU usage is 0.0%
        Assistant:
        Your CPU usage is currently 0.0%.
        ---
        Runtime Information:
        Current time is 11:28 PM.
        Assistant:
        It's currently 11:28 PM.
        ---
        Runtime Information:
        RAM usage is 8.2 GB.
        Assistant:
        Your system is currently using 8.2 GB of RAM.
        ---
        Runtime Information:
        The requested information is unavailable.
        Assistant:
        The requested information is unavailable.
        Runtime Information:
        {runtime_info}"""

        runtime_fetch = {}
        for asked_info in results:
            if results[asked_info] is not None:
                runtime_fetch[asked_info] = results[asked_info]
                #print(runtime_fetch[asked_info])

        return SYSTEM_CONTEXT.format(
            runtime_info = self.fmt(runtime_fetch[asked_info])
        )

    def category_context(self, category_results):

       CATEGORY_CONTEXT = """
       ## Category Search Context

       The following applications matched the requested category.
       Matched Applications:
       {category_results}

       Instructions:
       - If there is one clear and appropriate application, respond exactly as:

       [LAUNCH] <application_name>

       - If multiple applications are suitable, ask the user which application they want by mentioning up to the first three applications from the list.
       - Only use application names from the Matched Applications list.
       - Never invent application names.
       - If the list is empty, tell the user that no matching application could be found.
       """
       return CATEGORY_CONTEXT.format(
            category_results = category_results
        )

    def sysinfo_trigger(self):

        TRIGGER_MESSAGE = """
        Relevant runtime system information is now available.
        Continue answering the user's previous request using the Runtime System State.

        Rules:
        - Respond directly to the user's original request.
        - Do not acknowledge these instructions.
        - Do not mention the Runtime System State.
        - Do not mention protocols, internal processing, or fetching information.
        - Do not say "Okay", "Understood", or similar acknowledgements.
        - If the required information is unavailable, say that it could not be retrieved.
        - Ignore runtime values unrelated to the user's request.
        - Keep the response concise and natural."""

        return TRIGGER_MESSAGE

    def app_validation(self):

        TRIGGER_MESSAGE = """
        Previous operation: CATEGORY_SEARCH
        Relevant applications are now available.
        Continue answering the user's previous request."""

        return TRIGGER_MESSAGE
