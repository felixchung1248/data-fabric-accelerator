import os
import asyncio

from flask import Flask,request

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_core import to_jsonable_python
from pydantic_ai.messages import ModelMessagesTypeAdapter

api_key = os.environ.get("OPENROUTER_API_KEY")
genai_model=os.environ['GENAI_MODEL']

model = OpenAIModel(
    genai_model,
    provider=OpenRouterProvider(api_key=api_key),
)

server = MCPServerStdio(  
    'uv',
    args=[
        "run",
        "--directory",
        "C:\\Users\\felixchung\\dremio-mcp",
        "dremio-mcp-server",
        "run",   
    ]
)

agent = Agent(model, mcp_servers=[server])
same_history = None

async def main(msg):
    async with agent.run_mcp_servers():
        global same_history
        if same_history is None:
            result = await agent.run(msg)            
        else:
            result = await agent.run(msg, message_history=same_history)

        history = result.all_messages()
        as_python_objects = to_jsonable_python(history)
        same_history = ModelMessagesTypeAdapter.validate_python(as_python_objects)
    return result.output

app = Flask(__name__)

@app.route('/genai-response', methods=['POST'])
def genAiResponse():      
    json_array = request.get_json()
    msg = json_array.get('msg')  
    output = asyncio.run(main(msg))
    return output

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5201)        