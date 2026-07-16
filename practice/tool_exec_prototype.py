from abc import ABC, abstractmethod

print("The intent: ", end='')
intent = input("")

action, argument = intent.split(maxsplit=1)

class Tool(ABC):

    def __init__(self, name, description):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, argument):
        pass

class OpenApp(Tool):

    def __init__(self):
        super().__init__("Firefox", "A web browser")

    def execute(self, argument):
        print(f"Opening {argument}...")

class SystemUtilities(Tool):
    def __init__(self):
        super().__init__("Volume Changer", "A literal Volume changer yo?!")

    def execute(self, argument):
        print(f"Changing volume to {argument}%...")

class PluginTools(Tool):
    def __init__(self):
        super().__init__("Niggafier", "Makes human to nigga")

    def execute(self, argument):
        print(f"Niggafying human...")

tool_registry = {
        "[LAUNCH]": OpenApp(),
        "[SYSTEM]": SystemUtilities(),
        "[PLUGIN]": PluginTools()
        }

tools = tool_registry[action]

tools.execute(argument)
