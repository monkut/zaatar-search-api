# Summary of the Search and Summarization API

This document summarizes the architecture and components of the search and summarization system based on the provided code snippets. The system is designed to generate, manage, and display complex summaries derived from user data using Large Language Models (LLMs).

## Core Concept: "Shades"

The central data structure is the **"Shade"** (`ShadeInfo` class). A Shade represents a dynamic and evolving summary or profile of a specific topic, domain, or user interest. It is built from underlying data snippets referred to as "memories" or "notes."

Key characteristics of a Shade include:
- **Multiple Perspectives**: It stores descriptions from both a third-person view (`desc_third_view`) and a second-person view (`desc_second_view`), allowing for different narrative styles.
- **Timelines**: It maintains a timeline of events or memories that contributed to its creation and evolution.
- **Vector Representation**: Shades are associated with vector embeddings, as evidenced by the `_calculate_merged_shades_center_embed` function, which suggests they can be semantically clustered, compared, and merged.

## Key Python Components

The backend logic is primarily handled by two main classes that interact with an LLM.

### 1. `ShadeGenerator`
This class manages the entire lifecycle of a Shade. It is responsible for:
- **Initial Creation**: Generating a new Shade from a list of new "memories" (`_initial_shade_process`).
- **Improvement**: Refining an existing Shade by incorporating new memories (`_improve_shade_info`).
- **Merging**: Combining multiple Shades into a single, more comprehensive Shade (`_merge_shades_info`).
- **Orchestration**: The main `generate_shade` method determines whether to create, improve, or merge Shades based on the input.

### 2. `ShadeMerger`
This class specializes in the task of merging multiple existing Shades.
- It uses an LLM to make an intelligent decision on which shades are semantically similar enough to be grouped together.
- For each group of shades that are merged, it calculates a new **center embedding**, effectively finding the semantic center of the new, combined concept.

### LLM Integration
- Both `ShadeGenerator` and `ShadeMerger` use an OpenAI-compatible client to make calls to an LLM.
- The system includes a robust and clever retry mechanism (`_call_llm_with_retry` and `_fix_top_p_param`) that automatically adjusts the `top_p` parameter from 0 to a very small number (0.001) if the API rejects the call. This handles a common issue with some LLM providers that do not accept `top_p=0`.
- The system parses structured JSON data from the raw text responses of the LLM.

## API Endpoints & Frontend

The system exposes its functionality through a REST API and includes components for frontend display.

- **API Endpoints**:
    - `POST /api/v1/quick_summary`: Accepts a query to generate a quick research summary on demand.
    - `GET /api/research_search_metrics`: Retrieves and displays performance and search metrics for a given research task.
- **Frontend Display**:
    - The `displaySearchMetrics` JavaScript function is used to render detailed analytics on a web page.
    - It shows high-level metrics like success rate and average response time.
    - It also provides a detailed breakdown of each search call, including the engine used, the query, the number of results, and the response time.

## Other Observations
- The presence of an "SFT GUIDE" snippet suggests that the project may involve Supervised Fine-Tuning of its own models, in addition to using general-purpose APIs.
- The overall architecture points to a sophisticated system that goes beyond simple summarization, creating a dynamic, learning knowledge base from user inputs.
