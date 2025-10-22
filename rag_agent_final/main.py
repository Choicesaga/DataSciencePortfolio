import asyncio
from pathlib import Path
from beeai_framework.agents.requirement import RequirementAgent
from beeai_framework.agents.requirement.requirements.conditional import ConditionalRequirement
from beeai_framework.backend import ChatModel
from beeai_framework.memory.unconstrained_memory import UnconstrainedMemory
from beeai_framework.tools.search.duckduckgo import DuckDuckGoSearchTool
from beeai_framework.tools.think import ThinkTool
from beeai_framework.tools import Tool
from beeai_framework.middleware.trajectory import GlobalTrajectoryMiddleware
from beeai_framework.logger import Logger
from beeai_framework.errors import FrameworkError
from beeai_framework.tools.search.retrieval import VectorStoreSearchTool

from rag_storage import load_documents, setup_knowledge_base

async def main():
    folder_path = "/app/md_docs"
    file_paths = get_all_filepaths_in_directory(folder_path, extension=".md")

    agent = await create_agent(file_paths)
    loop = True

    while(loop):
        user_prompt = user_input()

        if user_prompt == "q":
            loop = False
            break
        print("Thinking...")

        try:
            response = await agent.run(user_prompt)

        except FrameworkError as e:
            print(e.explain())
        print()
        print(response.last_message.text)
        print()
    
async def create_agent(file_paths):
    vector_store, text_splitter = await setup_knowledge_base()
    loaded_vector_store = await load_documents(vector_store, text_splitter, file_paths)

    rag_tool = VectorStoreSearchTool(vector_store=loaded_vector_store)

    llm = ChatModel.from_name("ollama:granite3.3")
    logger = Logger("my-agent",level="TRACE")

    think_tool = ThinkTool()
    search_tool = DuckDuckGoSearchTool()

    logger.info("Creating agent")

    agent = RequirementAgent(
        llm=llm,
        memory = UnconstrainedMemory(),
        tools = [think_tool, rag_tool, search_tool],
        role = "Data knowledge consultant for a business",

        instructions="""You are the **Business Knowledge Specialist AI**. Your function is to answer user questions using our proprietary internal data.

            ### Directives
            1.  **Vector DB is Authoritative:** **PRIORITIZE** all information retrieved from the Vector DB. This proprietary data is the foundational truth for all responses.
            2.  **Augment, Don't Just Repeat:** Use the retrieved business knowledge to **directly address and augment** the specific scenario or question posed by the user.
            3.  **No External Web Search:** **DO NOT** use any external web search tools (e.g., Google, DuckDuckGo). All factual data must originate from the Vector DB.
            4.  **Tone & Delivery:** Be **precise, factual, and highly confident**. Omit all hedging language ("I think," "It seems").""",

        middlewares=[GlobalTrajectoryMiddleware(included=[Tool])],
        requirements=[
            ConditionalRequirement(think_tool,force_at_step = 1,force_after = Tool, consecutive_allowed=False, max_invocations=3),
            ConditionalRequirement(rag_tool, min_invocations = 1,force_at_step = 2 ,consecutive_allowed=False, max_invocations=2),
            ConditionalRequirement(search_tool, min_invocations = 1, consecutive_allowed = False, max_invocations = 2)
        ]
    )
    return agent

def get_all_filepaths_in_directory(directory_path: str, extension: str = None) -> list[str]:
   # Function that returns all file paths in a directory , used to store markdown files into vector DB
   
    dir_path = Path(directory_path)
    if not dir_path.is_dir():
        print(f"Warning: Directory not found: {directory_path}")
        return []

    if extension:
        # Use glob to find files matching the pattern (e.g., "*.pdf")
        pattern = f"*{extension}" if extension.startswith('.') else f"*.{extension}"
        # Ensure we return the absolute path as a string
        return [f"{str(p.resolve())}" for p in dir_path.glob(pattern) if p.is_file()]
    else:
        # Get all files and directories, then filter only for files
        return [f"{str(p.resolve())}" for p in dir_path.iterdir() if p.is_file()]
    
def user_input():
    user_prompt = input("- ")
    return user_prompt


if __name__ == "__main__":
    asyncio.run(main())