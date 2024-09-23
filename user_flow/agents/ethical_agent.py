import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(current_dir, '..')
sys.path.append(root_dir)

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from dotenv import load_dotenv
load_dotenv()

## Ethical check Agent
def ethical_agent(llm,query,ethical_guidelines):
    query_agent_qa_system_prompt = (
        f"""You are an Expert AI agent having expertise in checking whether the given sentence is following all the ethical guidelines or not. You will be provided with a simple sentence and you need to just check if it is following all the below mentioned guidelines or not. If the sentence is not following any of the mentioned guidelines, simply give False as the output in the below mentioned output format.

        ### Ethical Guidelines
        {ethical_guidelines}

        Give your final output in the below json format:
        <json>
        ```json
        {{{{
            "ethical_check":"True/False",
            "reason":"reason why it is ethical or unethical"
        }}}}
        ```
        </json>

        If you encounter any type of questions like below, consider it as ethical:
	 - give me more details
	 - give me the last n questions asked
	 - provide me more details
	
	Important points to remember:
	- Your job is to just check if the sentence is following all the ethical guidelines or not.
    - You should always give your final output in the above mentioned json format.
    - Remember you just need to give True/False as your output in the above format.
    - If anything like '******' or '#######' comess in the sentence, consider it as ethical.
        few examples for this types of queries:
         - How much installed capacity from the wind and solar components of the M74 West project could contribute towards achieving the 2030 renewable energy targets, considering the energy consumption of ##############?
         - Hello, my name is ########, and my social security number is ###########
    - If the sentence contains any address or location, consider it as true. All the information that are confidential is masked using ###### or *****. You don't need to worry about this.
    - Don't give any explanation about your role. You need to jsut check if the sentence is following all the guielinws or not and give your final output in the requested format.
    """
    )
    
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", query_agent_qa_system_prompt),
            ("human", "Here is the Sentence: {input}"),
        ]
    )
    # print(qa_prompt)
    question_answer_chain = qa_prompt | llm | StrOutputParser()
    response = question_answer_chain.invoke({"input":query})
    return response