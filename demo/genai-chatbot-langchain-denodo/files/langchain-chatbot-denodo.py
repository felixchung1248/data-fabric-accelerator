#----------------------------------
# IMPORTS
#----------------------------------
import sqlalchemy as db
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from flask import Flask,request

from langchain.agents import create_spark_sql_agent
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_community.agent_toolkits import SparkSQLToolkit
from langchain_community.utilities.spark_sql import SparkSQL
from langchain_openai import ChatOpenAI
from langchain_core import exceptions
import re
import os

#----------------------------------
# Setup
#----------------------------------
app = Flask(__name__)
denodo_url=os.environ['DENODO_URL']
genai_model=os.environ['GENAI_MODEL']
redis_url=os.environ['REDIS_URL']

# Initialize Spark session
spark = SparkSession.builder \
    .appName("DenodoToSparkSQLExample") \
    .config('spark.network.timeout', '800s') \
    .config('spark.executor.heartbeatInterval', '120s') \
    .getOrCreate()
schema = "langchain_example"
spark.sql(f"CREATE DATABASE IF NOT EXISTS {schema}")
spark.sql(f"USE {schema}")   

engine=db.create_engine(denodo_url)   
    
def cache_views():
    result_proxy = engine.execute("LIST VIEWS ALL")
    views = result_proxy.fetchall()

    # Iterate over the result set and print each row
    for row in views:
        view_name = row[0]  
        # Pandas DataFrame
        result_proxy = engine.execute(f"select * from {view_name}")
        pandas_df = pd.DataFrame(result_proxy.fetchall())   
        # Convert the Pandas DataFrame to a Spark DataFrame
        spark_df = spark.createDataFrame(pandas_df) 
        # Write the Spark DataFrame to a Spark table
        spark_df.write.saveAsTable(view_name)
        
    cached_views_as_turple = set((view[0], ) for view in views)
    return cached_views_as_turple
    
cached_views_as_turple = cache_views() 

print(cached_views_as_turple)

llm = ChatOpenAI(model=genai_model,temperature=0)

memory = RedisChatMessageHistory(
    url=redis_url, ttl=600, session_id="my-session"
)

@app.route('/genai-response', methods=['POST'])
def genAiResponse():
    global cached_views_as_turple
    # # Get the JSON from the POST request body
    try:   
        result_proxy = engine.execute("LIST VIEWS ALL")
        views = result_proxy.fetchall()
        views_as_turple_cur = set((view[0], ) for view in views)
        print(cached_views_as_turple)
        print(views_as_turple_cur)
        new_views = [d for d in views_as_turple_cur if d not in cached_views_as_turple]
        cached_views_as_turple = views_as_turple_cur
        print(new_views)
        for view in new_views:
            view_name = view[0]
            result_proxy = engine.execute(f"select * from {view_name}")
            pandas_df = pd.DataFrame(result_proxy.fetchall())   
            # Convert the Pandas DataFrame to a Spark DataFrame
            spark_df = spark.createDataFrame(pandas_df) 
            # Write the Spark DataFrame to a Spark table
            spark_df.write.saveAsTable(view_name)


        json_array = request.get_json()
        msg = json_array.get('msg')  
        
        spark_sql = SparkSQL(spark_session=spark, schema=schema)
        toolkit = SparkSQLToolkit(db=spark_sql, llm=llm)
        agent_executor = create_spark_sql_agent(
                    llm=llm
                    ,toolkit=toolkit
                    , verbose=True
                    , handle_parsing_errors=True
                )  
        
        agent_with_chat_history = RunnableWithMessageHistory(
            agent_executor,
            # This is needed because in most real world scenarios, a session id is needed
            # It isn't really used here because we are using a simple in memory ChatMessageHistory
            lambda session_id: memory,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

        result = agent_with_chat_history.invoke(
                    {"input": msg},
                    config={"configurable": {"session_id": "test-session"}},
                ) 
        return result['output']
    except exceptions.OutputParserException as e:
        # Handle the specific OutputParserException
        error_message = str(e)
        print(f"OutputParserException caught: {error_message}", flush=True)
        # Extract meaningful error message if it matches the expected pattern
        if error_message.startswith("Could not parse LLM output: `"):
            error_message = error_message.removeprefix("Could not parse LLM output: `")
        #return jsonify({"error": "Output parsing error", "details": error_message}), 500
    except ValueError as e:
        # Handle any other ValueError that might be related to parsing
        error_message = str(e)
        print(f"ValueError caught: {error_message}", flush=True)
        match = re.search(r"Could not parse LLM output: `(.+)`", error_message, re.DOTALL)
        match2 = re.search(r"Final Answer: (.+)", error_message, re.DOTALL)

        # Check if we found a match
        if match:
            extracted_message = match.group(1) 
            print(extracted_message)
            return(extracted_message)
        elif match2:
            extracted_message = match2.group(1) 
            print(extracted_message)
            return(extracted_message)
        else:
            return("I don't know")
        #return jsonify({"error": "ValueError", "details": error_message}), 500
    except Exception as e:
        # General exception handler for any unexpected exceptions
        error_message = str(e)
        print(f"Unexpected error caught: {error_message}", flush=True)
        #return jsonify({"error": "Unexpected error", "details": error_message}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5201)