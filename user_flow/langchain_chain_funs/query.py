import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(current_dir, '..')
sys.path.append(root_dir)
from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from user_utils.user_utils import get_session_history
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
import json
from langchain_community.callbacks.manager import get_bedrock_anthropic_callback
import asyncio
load_dotenv()

async def ask_question_stream(session_id: str, question: str, rag_chain, output):
    if not question:
        raise HTTPException(status_code=400, detail="Invalid input")

    # Retrieve chat history
    history = get_session_history(session_id)
    inputs = {"input": question, "chat_history": history.messages}

    async def stream_chunks():
        final_answer = ""
        with get_bedrock_anthropic_callback() as cb:
            for chunk in rag_chain.stream(inputs):
                for key in chunk:
                    if key in ['input', 'chat_history']:
                        continue
                    elif key == "context":
                        context = chunk[key]
                        contxt_chunks = [
                            {
                                "chunk": ref.page_content,
                                "documentURL": ref.metadata["s3URI"],
                                "pageNumber": ref.metadata["page"],
                                "documentTitle": ref.metadata["title"],
                            }
                            for ref in context
                        ]
                        output["chunks"] = contxt_chunks
                        continue
                    if key not in output:
                        output[key] = chunk[key]
                    else:
                        output[key] += chunk[key]

                    # Collect the answer for the final JSON response
                    if key == "answer":
                        final_answer += chunk[key]  # Append to final answer

                    # Stream each chunk back to the user
                    yield f"{chunk[key]} "

            # Update history with the new messages
            history.messages.append(HumanMessage(content=question))
            history.messages.append(AIMessage(content=output.get('answer', '')))

            # After streaming, send a separator (this can be anything, e.g. "\n---END OF STREAM---\n")
            yield "\n---END OF STREAM---\n"

            # Prepare the final JSON response
            final_output = {
                "visitorID": output['visitorID'],
                "assetID": output['assetID'],
                "projectID": output['projectID'],
                "question": output['question'],
                "guidelinesPass": output['guidelinesPass'],
                "removedPII": output['removedPII'],
                "questionTime": output['questionTime'],
                "answer": final_answer,
                "answerTime": datetime.now().strftime('%Y%m%d %H:%M:%S'),
                "chunks": output['chunks'],
                "top_k": output['top_k'],
                "inputTokens" : output["inputTokens"]+cb.prompt_tokens,
                "outputTokens" : output["outputTokens"]+cb.completion_tokens
            }
            
            # Send the final JSON output after the separator
            yield json.dumps(final_output)

    return StreamingResponse(stream_chunks(), media_type="text/plain")


async def unethical_stream(output):
    message = "The question does not pass the ethical guidelines"
    
    async def stream_characters():
        # Stream character by character
        for char in message:
            yield char
            await asyncio.sleep(0.05)
        
        # End-of-stream marker
        yield "\n---END OF STREAM---\n"
        await asyncio.sleep(0.05)
        # Final JSON response
        output["answer"] = message
        yield json.dumps(output)


    return StreamingResponse(stream_characters(), media_type="text/plain")


