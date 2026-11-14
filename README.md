# Nyx

Nyx is a personal, ongoing project focused on building a local AI daemon for Linux.

It integrates voice interaction, local LLM inference, application management, and system awareness into a background service that runs alongside the desktop environment.

The project is built primarily with Python, with an emphasis on local execution, resource efficiency, and predictable system-level interaction.

Nyx starts automatically with the system and can be activated through global keyboard shortcuts. It is designed to handle everyday desktop interactions through natural conversation rather than requiring predefined commands from the user.

**Project status:** Actively developed. Core functionality is implemented and working. Development is currently focused on the resource lifecycle management subsystem.

## Features

- **Background daemon:** Starts automatically when the system boots.
- **Voice interaction:** Supports voice input and spoken responses.
- **Global activation:** Uses `keyd` for keyboard-based activation and deactivation.
- **Application discovery:** Scans installed `.desktop` files and maintains an SQLite application registry.
- **Application launching:** Opens installed applications through structured model-generated commands.
- **Contextual application selection:** Resolves ambiguous requests using application categories and contextual suggestions.
- **System awareness:** Retrieves live CPU, RAM, VRAM, battery, storage, and other system information.
- **Time awareness:** Uses the system date and time for contextual responses and greetings.
- **Custom tool protocol:** Uses constrained command formats to improve tool-call reliability with smaller language models.
- **Resource lifecycle management:** Currently under development, with the goal of managing Nyx's resource consumption and service lifecycle automatically.

## Architecture

Nyx uses a producer-consumer architecture to coordinate its speech-processing and response-generation pipeline.

```text
                    Voice Input
                        |
                        v
                    Silero VAD
                        |
                        v
                  Faster Whisper
                        |
                        v
                    Text Queue
                        |
                        v
                   Ollama (LLM)
                        |
                +-------+-------+
                |               |
                v               v
          Tool Protocol    Natural Response
                |               |
          +-----+------+        |
          |            |        |
          v            v        |
       [LAUNCH]     [SYSTEM]    |
          |            |        |
          v            v        |
      App Handler  System Info  |
          |            |        |
          v            v        |
       SQLite DB   Live Metrics |
          |            |        |
          +------+-----+--------+
                 |
                 v
            Response Queue
                 |
                 v
              Kokoro
                 |
                 v
             Voice Output
```

Python handles the application logic, threading, queue management, protocol parsing, and coordination between individual components.

Queues allow different stages of the pipeline to process data independently, following a producer-consumer pattern.

## Speech Processing

Nyx uses a fully local speech-processing pipeline.

| Component | Purpose |
|---|---|
| Silero VAD | Voice activity detection |
| Faster Whisper | Speech-to-text transcription |
| Ollama | Local LLM inference |
| Gemma 3 4B | Language model |
| Kokoro TTS | Speech synthesis |

The components are coordinated using Python queues and multithreading.

Ollama runs as a local inference server, allowing Nyx to communicate with the language model through its local API.

Model selection is influenced by available hardware resources, particularly limited GPU VRAM.

## Custom Tool Protocol

One of the central design decisions in Nyx is the use of a custom command protocol for tool invocation.

Smaller language models can struggle with strict JSON formatting and structured tool calls. To address this, I developed a constrained output format that is easier for the model to generate and for the application to parse.

Instead of relying entirely on unrestricted JSON generation, Nyx uses explicit command prefixes to identify the intended operation.

### Application commands

Direct application launching:

```text
[LAUNCH] firefox
```

Multiple applications:

```text
[LAUNCH] firefox spotify discord
```

Category-based application resolution:

```text
[LAUNCH] browser
```

### System commands

System information requests use a separate command format:

```text
[SYSTEM] cpu
```

The application interprets the command and routes it to the appropriate handler.

For system requests, the relevant metrics are retrieved and injected into an independent LLM request, allowing the model to formulate a natural-language response using actual system information.

This approach separates intent recognition from system execution and reduces malformed tool calls.

## Application Discovery and Execution

Nyx maintains an SQLite registry of installed desktop applications.

The registry is populated by scanning `.desktop` files, parsing their metadata, filtering relevant applications, and storing the resulting entries.

```text
.desktop Files
      |
      v
   Parser
      |
      v
  Application Filtering
      |
      v
  SQLite Registry
      |
      v
  Application Lookup
```

Application requests are handled in two ways.

**Direct application requests**

When a user explicitly requests an application, the model generates a `[LAUNCH]` command containing its name. The application handler resolves the requested application against the SQLite registry and launches it.

**Ambiguous or category-based requests**

For requests such as asking to open a browser or music player, Nyx follows a contextual resolution process:

1. Identifies the requested application category.
2. Retrieves matching applications from SQLite.
3. Passes the available applications and original user intent to an independent LLM request.
4. Asks the model to select up to three relevant applications.
5. Presents the suggestions to the user.
6. Launches the selected application after confirmation.

If the suggestions are unsuitable, the conversation can continue through natural language for further clarification.

This allows Nyx to work with applications actually installed on the machine rather than relying on a predefined application list.

## System Awareness

Nyx can retrieve live information from the host system and use it as context for conversational responses.

| Category | Information |
|---|---|
| CPU | Usage and temperature |
| RAM | Memory utilization |
| GPU | VRAM utilization |
| Battery | Charge percentage |
| Power | Charger connection status |
| Storage | Disk utilization |
| Host | System hostname |
| Time | Current date and time |

System information is retrieved through dedicated Python handlers and injected into independent LLM requests.

This allows Nyx to respond using actual system metrics instead of relying on the model's internal knowledge.

## Resource Lifecycle Management

**Status: Currently under development**

The resource lifecycle manager is the current focus of development.

The idea is to make Nyx aware of its own resource consumption and capable of managing its execution lifecycle according to system resource availability.

The intended functionality includes:

- Monitoring system resource utilization.
- Detecting sustained resource pressure.
- Unloading locally running models when resource usage crosses configured thresholds.
- Stopping unnecessary background services.
- Notifying the user before entering a suspended state.
- Restarting services and reloading models when sufficient resources become available again.

For example, when a resource-intensive application such as a game is started, Nyx should be able to detect sustained resource pressure, notify the user, and release its own resources by unloading models and stopping its services.

When resource utilization remains low for a specified period, it should be able to resume its services.

The goal is to make Nyx a resource-aware background system rather than another application continuously competing for system resources.

This subsystem is still being developed and is not yet considered stable.

## Technology Stack

| Technology | Usage |
|---|---|
| Python | Core application and system integration |
| Silero VAD | Voice activity detection |
| Faster Whisper | Speech recognition |
| Ollama | Local LLM inference |
| Gemma 3 4B | Language model |
| Kokoro TTS | Speech synthesis |
| SQLite | Application registry |
| keyd | Global keyboard shortcuts |
| systemd | Background service management |

## Development Status

Nyx is a personal project developed independently alongside my college studies. Development happens alongside academic commitments, so progress is gradual.

The core voice interaction pipeline, application discovery and launching, custom tool protocol, and system information retrieval are implemented and working.

Current development is focused primarily on the resource lifecycle manager, with further improvements planned for the overall architecture.

The project is actively maintained and evolving. The existing functionality is usable, while newer subsystems may remain experimental until properly tested.
