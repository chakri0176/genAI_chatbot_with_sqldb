import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq

st.set_page_config(page_title="Langchain: Chatbot with SQL DB", page_icon="🐬")
st.title("🐬 Langchain: Chatbot with SQL DB")


LOCAL_DB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_opt = ["Use SQLLite 3 Database - Student.db","Connect to your SQL Data"]

st.sidebar.title("Settings")
selected_opt = st.sidebar.radio(label="Chosse the DB which you want to use",options=radio_opt)

if radio_opt.index(selected_opt) == 1:
    db_url = MYSQL
    mysql_host = st.sidebar.text_input("Provide My SQL Host")
    mysql_user = st.sidebar.text_input("My SQL User")
    mysql_password = st.sidebar.text_input("My SQL Password",type = "password")
    mysql_db = st.sidebar.text_input("My SQL Database")
else:
    db_url = LOCAL_DB
    
api_key = st.sidebar.text_input(label="Enter the GROQ API KEY",type = "password")

if not db_url:
    st.info("Please enter the database information")

if not api_key:
    st.infor("Please enter the GROQ API KEY")
    
    
llm = ChatGroq(groq_api_key = api_key, model_name = "llama-3.1-8b-instant", streaming= True)

#Storing the cache information
@st.cache_resource(ttl="2h")
def configure_db(db_url,mysql_host=None,mysql_user=None,mysql_password=None,mysql_db=None):
    if db_url == LOCAL_DB:
        dbfilepath = (Path(__file__).parent/"student.db").absolute()
        print(dbfilepath)
        
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro",uri=True)
        return SQLDatabase(create_engine("sqlite:///",creator=creator))
    elif db_url == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL Conncection details.")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))
    
    
if db_url == MYSQL:
    db = configure_db(db_url,mysql_host,mysql_user,mysql_password,mysql_db)
else:
    db = configure_db(db_url)