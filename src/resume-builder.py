import asyncio
import argparse

from semantic_kernel.agents import Agent, ChatCompletionAgent, GroupChatOrchestration, RoundRobinGroupChatManager
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatMessageContent

"""
The following script orchestrates a multi-agent workflow to create a high-quality resume tailored for a specific job description.
It uses a group chat orchestration with a round-robin manager to ensure that each agent contributes to the process.
The agents involved are: ProjectManager, JobMarketAnalyst, and Strategist.
This script is designed to ensure that the final resume meets ATS requirements and scores more than 85% on the necessary keywords.
The agents will iterate through the resume creation process until the desired score is achieved.
"""

# === Agent Instructions and Descriptions ===
PROJECT_MANAGER_INSTRUCTIONS = (
    "Oversee multi-agent workflows, enforce standards, and make sure the new resume scores more than 85% on the necessary keywords. "
    "If the newly created resume scores less than 85%, ask the agents to repeat the process until 85% or more is reached. "
    "You are a seasoned program manager with a decade of experience in crafting high-impact career resumes. "
    "You create new content and edit contents based on the feedback."
    "Do not ask for additional information, just use the provided resume and job description to create a new resume. "
    "Always implement any additional refinements suggested by other agents if provided. "
)
PROJECT_MANAGER_DESCRIPTION = (
    "Oversees the resume creation workflow, enforces standards, and ensures the final resume meets ATS requirements."
)

JOB_MARKET_ANALYST_INSTRUCTIONS = (
    "Conduct deep analyses of technical job postings—extract core requirements, uncover implicit employer priorities, benchmark against industry standards, "
    "and surface actionable insights to optimize application strategies. You are a veteran labor market intelligence specialist with a track record in parsing "
    "thousands of engineering job descriptions. You review the content and provide feedback to the project manager."
    "Do not ask for additional information, just use the provided resume and job description to create a new resume. "
)
JOB_MARKET_ANALYST_DESCRIPTION = (
    "Analyzes job postings, extracts key requirements, and provides actionable insights for resume optimization."
)

STRATEGIST_INSTRUCTIONS = (
    "You are a Senior Curriculum Vitae Strategist. Transform raw candidate data into a laser-focused, accomplishment-driven resume—tailored for the target role, "
    "optimized for both ATS parsing and human reader engagement. You are a career strategist with a decade of experience elevating resumes for Fortune 500 and "
    "high-growth startups. You review the provided feedback and create new content and edit contents based on the feedback."
    "Do not ask for additional information, just use the provided resume and job description to create a new resume. "
    "Always implement any additional refinements suggested by other agents if provided. "
)
STRATEGIST_DESCRIPTION = (
    "Crafts and optimizes resumes for the target role, ensuring both ATS and human appeal."
)

# Store the entire conversation
conversation_log = []

# Load original resume and job description from given file paths
def load_files(resume_path='../docs/resume.md', job_desc_path='../docs/sample/job-description.md'):
    with open(resume_path, 'r', encoding='utf-8') as f:
        original_resume = f.read()
    with open(job_desc_path, 'r', encoding='utf-8') as f:
        job_description = f.read()
    return original_resume, job_description

def get_agents() -> list[Agent]:
    """Return a list of agents that will participate in the group style discussion."""
    projectmanager = ChatCompletionAgent(
        name="ProjectManager",
        description=PROJECT_MANAGER_DESCRIPTION,
        instructions=PROJECT_MANAGER_INSTRUCTIONS,
        service=AzureChatCompletion(),
    )
    jobmarketanalyst = ChatCompletionAgent(
        name="JobMarketAnalyst",
        description=JOB_MARKET_ANALYST_DESCRIPTION,
        instructions=JOB_MARKET_ANALYST_INSTRUCTIONS,
        service=AzureChatCompletion(),
    )
    strategist = ChatCompletionAgent(
        name="Strategist",
        description=STRATEGIST_DESCRIPTION,
        instructions=STRATEGIST_INSTRUCTIONS,
        service=AzureChatCompletion(),
    )
    # The order of the agents in the list will be the order in which they will be picked by the round robin manager
    return [projectmanager, jobmarketanalyst, strategist]

def agent_response_callback(message: ChatMessageContent) -> None:
    """Observer function to print the messages from the agents and log them."""
    entry = f"**{message.name}**\n{message.content}\n"
    print(entry)
    conversation_log.append(entry)


def get_instructions(job_description, original_resume):
    return f"""
Compile a comprehensive personal and professional profile using the provided resume.

1. Craft a new resume based on the old one and the suggestions from the previous task 
2. Maintain fidelity to source documents; do not hallucinate.
3. Repeat the process as many times you need until the new resume scores more than 85% on the necessary keywords.

The expected output is:
A detailed resume in MD format with at least 85% match with the job description keywords, including:
- revised summary
- reorganized work_experience entries
- highlighted skills
- tailored education section
- Objective Statement summarizing key skills and experience relevant to the target role
- Specific project details and measurable accomplishments
- **EXTREMLY IMPORTANT** the generated resume **MUST** be compared with the with keywords and the job 
    description and if it is less than 85% do it again and again untill you reach a scoring greather than 85%
- **MANDATORY** Output the newly generated resume and the result of the newly generated resume compared with 
    keywords and the job description and wait for the human input.

### Job Description

The job description is provided is provided below:

{job_description}
###

### Original Resume

The original resume is provided below:

{original_resume}

###
"""

async def main():
    """Main function to run the agents."""
    parser = argparse.ArgumentParser(description="Multi-agent resume optimizer")
    parser.add_argument('--resume', type=str, default='./docs/resume.md', help='Path to the resume markdown file')
    parser.add_argument('--jobdesc', type=str, default='./docs/sample/job-description.md', help='Path to the job description markdown file')
    args = parser.parse_args()

    # 1. Create a group chat orchestration with a round robin manager
    agents = get_agents()
    group_chat_orchestration = GroupChatOrchestration(
        members=agents,
        # max_rounds is odd, so that the project manager gets the last round
        manager=RoundRobinGroupChatManager(max_rounds=7),
        agent_response_callback=agent_response_callback,
    )

    original_resume, job_description = load_files(args.resume, args.jobdesc)

    # 2. Create a runtime and start it
    runtime = InProcessRuntime()
    runtime.start()

    # 3. Invoke the orchestration with a task and the runtime
    task = get_instructions(job_description, original_resume)
    orchestration_result = await group_chat_orchestration.invoke(
        task=task,
        runtime=runtime,
    )

    # 4. Wait for the results
    value = await orchestration_result.get()
    result_entry = f"***** Result *****\n{value}\n"
    print(result_entry)
    conversation_log.append(result_entry)

    # Write the entire conversation to docs/entire-conversation.md
    with open('./docs/entire-conversation.md', 'w', encoding='utf-8') as f:
        f.writelines(conversation_log)
    print("Entire conversation saved to ./docs/entire-conversation.md")

    # 5. Stop the runtime after the invocation is complete
    await runtime.stop_when_idle()


if __name__ == "__main__":
    asyncio.run(main())
