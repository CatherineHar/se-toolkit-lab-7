"""LLM client for intent routing and tool use."""

import json
from typing import Any

import httpx


class LLMClient:
    """Client for LLM API with tool use support."""

    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        """
        Initialize the LLM client.

        Args:
            base_url: Base URL of the LLM API (e.g., http://localhost:42005/v1)
            api_key: API key for authentication
            model: Model name to use
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def chat_with_tools(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]],
        max_iterations: int = 5,
    ) -> str:
        """
        Chat with the LLM using tool use.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: List of tool definitions (function schemas)
            max_iterations: Maximum tool use iterations

        Returns:
            Final response from the LLM
        """
        client = await self._get_client()
        conversation = messages.copy()

        for _ in range(max_iterations):
            # Call the LLM
            payload = {
                "model": self.model,
                "messages": conversation,
                "tools": tools,
                "tool_choice": "auto",
            }

            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()

            # Get the assistant message
            assistant_message = result["choices"][0]["message"]
            conversation.append(assistant_message)

            # Check if there are tool calls
            if "tool_calls" not in assistant_message:
                # No tool calls, return the final response
                return assistant_message.get("content", "I don't have information about that.")

            # Execute tool calls
            tool_results = []
            for tool_call in assistant_message["tool_calls"]:
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])

                # Execute the tool
                result = await self._execute_tool(function_name, function_args)
                tool_results.append({
                    "tool_call_id": tool_call["id"],
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(result),
                })

            # Add tool results to conversation
            conversation.extend(tool_results)

        # If we reach max iterations, return what we have
        return "I'm having trouble processing your request. Please try rephrasing."

    async def _execute_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """
        Execute a tool by calling the backend API.

        Args:
            name: Tool/function name
            arguments: Function arguments

        Returns:
            Tool execution result
        """
        from services.lms_client import LMSClient
        from config import load_config

        config = load_config(test_mode=True)
        lms_client = LMSClient(config.lms_api_base_url, config.lms_api_key)

        try:
            if name == "get_items":
                return await lms_client.get("/items/")
            elif name == "get_learners":
                return await lms_client.get("/learners/")
            elif name == "get_scores":
                lab = arguments.get("lab", "")
                return await lms_client.get("/analytics/scores", params={"lab": lab})
            elif name == "get_pass_rates":
                lab = arguments.get("lab", "")
                return await lms_client.get("/analytics/pass-rates", params={"lab": lab})
            elif name == "get_timeline":
                lab = arguments.get("lab", "")
                return await lms_client.get("/analytics/timeline", params={"lab": lab})
            elif name == "get_groups":
                lab = arguments.get("lab", "")
                return await lms_client.get("/analytics/groups", params={"lab": lab})
            elif name == "get_top_learners":
                lab = arguments.get("lab", "")
                limit = arguments.get("limit", 5)
                return await lms_client.get(
                    "/analytics/top-learners",
                    params={"lab": lab, "limit": limit},
                )
            elif name == "get_completion_rate":
                lab = arguments.get("lab", "")
                return await lms_client.get("/analytics/completion-rate", params={"lab": lab})
            elif name == "trigger_sync":
                client = await self._get_client()
                response = await client.post(f"{config.lms_api_base_url}/pipeline/sync")
                response.raise_for_status()
                return response.json()
            else:
                return {"error": f"Unknown tool: {name}"}
        finally:
            await lms_client.close()


def get_tool_definitions() -> list[dict[str, Any]]:
    """Get the list of tool definitions for the LLM."""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "List of all labs and tasks. Use this to see what labs are available.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_learners",
                "description": "Get enrolled students and their groups.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_scores",
                "description": "Get score distribution (4 buckets) for a specific lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task average scores and attempt counts for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_timeline",
                "description": "Get submissions per day for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Get per-group scores and student counts for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_top_learners",
                "description": "Get top N learners by score for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of top learners to return (default: 5)",
                            "default": 5,
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_completion_rate",
                "description": "Get completion rate percentage for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_sync",
                "description": "Trigger ETL sync to refresh data from autochecker.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
    ]
