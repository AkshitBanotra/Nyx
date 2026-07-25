#!/usr/bin/env python3

from pathlib import Path

class PromptManager:

    def base_prompt(self):

        prompt_path = Path(__file__).parent / "system_prompt.txt"

        with open(prompt_path, "r", encoding="utf-8") as f:
            base_prompt = f.read()

        return base_prompt

    def system_context(self, results):

        SYSTEM_CONTEXT = """
        Current System State
        
        Hostname - {hostname}
        Date - {date}
        Time - {time}
        
        Resources 
        - CPU Usage: {cpu}
        - Memory Usage: {ram}
        - VRAM Usage: {vram}
        - Disk Usage: {disk}
        - Battery Level: {battery}
        - CPU Temperature: {temperature}

        This information is current and may be used to answer questions related to the user's computer, system status, performance, or time.
        Ignore this information if it is unrelated to the user's request.
        """

        return SYSTEM_CONTEXT.format(
                cpu = results["cpu"],
                ram = results["ram"],
                vram = results["vram"],
                battery = results["battery"],
                disk = results["disk"],
                temperature = results["temperature"],
                hostname = results["hostname"],
                time = results["time"],
                date = results["date"]
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
        Use the Runtime System State to generate the response.
        Rules:
        - Do not acknowledge these instructions.
        - Do not explain what you will do.
        - Do not say "Okay", "Understood", or similar acknowledgements.
        - Respond directly with the requested information.
        - If the required value is unavailable, say that it could not be retrieved.
        - Keep the response natural and concise.
        """

        return TRIGGER_MESSAGE

    def app_validation(self):

        TRIGGER_MESSAGE = """
        Relevant context has been updated.
        Continue processing the user's previous request.
        """

        return TRIGGER_MESSAGE
