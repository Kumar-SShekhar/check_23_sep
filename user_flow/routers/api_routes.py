import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(current_dir, '..')
sys.path.append(root_dir)

from fastapi import APIRouter, Request, HTTPException
from langchain_community.callbacks.manager import get_bedrock_anthropic_callback
from config.aws_config import initialize_llm
from langchain_chain_funs.db_retriever import initialize_db_retriever
from langchain_chain_funs.chains import create_rag_chain
from user_utils.user_utils import extract_json_from_string
from agents.ethical_agent import ethical_agent
from langchain_chain_funs.query import ask_question_stream, unethical_stream
from utils.common_utils import read_json_file
from user_utils.pii_remover import detect_and_mask_pii
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

router = APIRouter()
# FastAPI route to handle POST request
@router.post('/userQA')
async def userQA(request: Request):
    data = await request.json()
    question_time = datetime.now().strftime("%Y%m%d %H:%M:%S")
    # Extract parameters from request body
    session_id = data.get('sessionID')
    asset_id = data.get('assetID')
    project_id = data.get('projectID')
    question = data.get('question')
    
    # Check for missing parameters
    if not session_id or not asset_id or not project_id or not question:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    
    config_data = read_json_file(f"user_config/{project_id}_config.json")
    # return JSONResponse(content=config_data)
    llm = initialize_llm(model_id=config_data['llm_model'],temperature=config_data['temperature'])
    retriever = initialize_db_retriever(projectID=project_id,top_k=config_data['top_k'],embeddings_model=config_data['embeddings_model'])
    rag_chain = create_rag_chain(llm=llm,retriever=retriever,systemPrompt=config_data['system_prompt'])
    with get_bedrock_anthropic_callback() as cb:
        detect_pii = detect_and_mask_pii(question)
        masked_query = detect_pii['masked_text']
        print(f"masked_query: {masked_query}")
        ethical_res = extract_json_from_string(ethical_agent(llm=llm,query=masked_query,ethical_guidelines=config_data['ethical_guidelines']))
        # print(ethical_res)
        output = {
            "visitorID": session_id,
            "assetID": asset_id,
            "projectID": project_id,
            "question": question,
            "guidelinesPass": "",
            "removedPII": detect_pii["pii_removed"],
            "questionTime": question_time,
            "answer": "",
            "answerTime": datetime.now().strftime("%Y%m%d %H:%M:%S"),
            "chunks": [],
            "top_k": config_data['top_k'],
            "inputTokens": cb.prompt_tokens,
            "outputTokens":cb.completion_tokens
        }
        if ethical_res['ethical_check'].lower() == "false":
            output["guidelinesPass"] = "N"
            return await unethical_stream(output)
        else:
            output["guidelinesPass"] = "Y"
            output["inputTokens"] = cb.prompt_tokens
            output["outputTokens"] = cb.prompt_tokens
            return await ask_question_stream(session_id, masked_query, rag_chain,output)
