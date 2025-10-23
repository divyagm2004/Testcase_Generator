import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# Reviewer Agent Tool
async def reviewer_agent_tool(user_story: str) -> int:
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o",
        api_key=OPENAI_API_KEY
    )

    reviewer = AssistantAgent(
        name="reviewer_tool",
        model_client=model_client,
        system_message="""
        You are a reviewer agent. Your task is to evaluate user stories and rate them from 1 to 10.
        Rating Criteria:
        - 1 to 4: Out of scope (not related to software development or QA).
        - 5 to 7: In scope but poorly written (e.g., grammar/spelling issues, vague).
        - 8 to 10: Meaningful and well-written user story in scope.

        Respond ONLY with a single integer between 1 and 10.
        """
    )

    result = await reviewer.run(task=f"Rate this user story: {user_story}")
    await model_client.close()

    try:
        rating = int(result.messages[-1].content.strip())
        return rating
    except ValueError:
        return 0  # fallback if parsing fails

# Generator Agent
async def generate_test_cases(user_story: str, model_choice: str = "openai") -> str:
    rating = await reviewer_agent_tool(user_story)

    if rating <= 4:
        return "I can't help with that. The user story is out of scope."
    elif rating <= 7:
        return "Please provide a clearer and more meaningful user story."

    # Proceed with generation if rating is 8–10
    match model_choice.lower():
        case "openai":
            model_client = OpenAIChatCompletionClient(model="gpt-4o", api_key=OPENAI_API_KEY)
        case "gemini":
            model_client = OpenAIChatCompletionClient(
                model="gemini-2.5-pro",
                model_info=ModelInfo(
                    vision=True,
                    function_calling=True,
                    json_output=True,
                    family="unknown",
                    structured_output=True
                ),
                api_key=GEMINI_API_KEY
            )
        case _:
            raise ValueError("Unsupported model choice")

    agent = AssistantAgent(
        name="testcase",
        model_client=model_client,
        system_message="""
         You are a test case generator chatbot that helps QA teams and developers by converting user stories into structured test cases.
         You must answer only user stories related to software application development.
 Give a   title above the table according to the user story.
 Output format: Tabular with the following fields:
- ID
- Scenario Type (Positive, Negative, Edge Case, Acceptance)
- Description
- Preconditions
- Steps (write as plain text, numbered list if needed, but DO NOT use <br>, <br/>, or any HTML tags)
- Expected Results
- Priority Level
 
Generate all possible test cases based on the user story provided.
        """
    )

    result = await agent.run(task=user_story)
    await model_client.close()
    return result.messages[-1].content

# Sync wrapper for Flask
def run_generate_test_cases(user_story: str, model_choice: str = "openai") -> str:
    return asyncio.run(generate_test_cases(user_story, model_choice))