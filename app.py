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
from urllib.parse import quote_plus

st.set_page_config(page_title="Langchain: Chatbot with SQL DB", page_icon="🐬")
st.title("🐬 Langchain: Chatbot with SQL DB")


LOCAL_DB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"
MSSQL = "USE_MSSQL"

radio_opt = ["Use SQLLite 3 Database - Student.db","Connect to your SQL Data","Connect to SQL Server (MSSQL)"]

st.sidebar.title("Settings")
selected_opt = st.sidebar.radio(label="Chosse the DB which you want to use",options=radio_opt)

if radio_opt.index(selected_opt) == 1:
    db_url = MYSQL
    mysql_host = st.sidebar.text_input("Provide My SQL Host")
    mysql_user = st.sidebar.text_input("My SQL User")
    mysql_password = st.sidebar.text_input("My SQL Password",type = "password")
    mysql_db = st.sidebar.text_input("My SQL Database")
elif radio_opt.index(selected_opt) == 2:
    db_url = MSSQL
    mssql_server = st.sidebar.text_input("SQL Server (e.g., HOST or HOST\\INSTANCE or HOST,1433)")
    mssql_db = st.sidebar.text_input("Database(eg., master, MyDb, CompanyDB)")
    msssql_auth = st.sidebar.selectbox("Authentication",["Windows (Integrated)","SQL Login"])
    if msssql_auth == "SQL Login":
        msssql_user = st.sidebar.text_input("SQL Login (user id)")
        mssql_password = st.sidebar.text_input("SQL Password",type="password")
    else:
        mssql_user = None
        mssql_password = None
    mssql_trust_cert = st.sidebar.checkbox("Trust Server Certificate (dev/test)",value=False,help="Enable only if you cannot validate the certificate (dev/test).")
    mssql_driver = st.sidebar.text_input("ODBC Driver", value="ODBC Driver 18 for SQL Server",help="Must be installed on the server running this app.")
else:
    db_url = LOCAL_DB
    
api_key = st.sidebar.text_input(label="Enter the GROQ API KEY",type = "password")

if not db_url:
    st.info("Please enter the database information")

if not api_key:
    st.info("Please enter the GROQ API KEY")
    
    
llm = ChatGroq(groq_api_key = api_key, model_name = "llama-3.1-8b-instant", streaming= True)

#Storing the cache information
@st.cache_resource(ttl="2h")
def configure_db(db_url,mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None,
    mssql_server=None, mssql_db=None, mssql_auth=None, mssql_user=None, mssql_password=None,
    mssql_trust_cert=False, mssql_driver="ODBC Driver 18 for SQL Server"):
    if db_url == LOCAL_DB:
        dbfilepath = (Path(__file__).parent/"comapny.db").absolute()
        print(dbfilepath)
        
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro",uri=True)
        return SQLDatabase(create_engine("sqlite:///",creator=creator))
    elif db_url == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL Conncection details.")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))
    elif db_url == MSSQL:
        if not (mssql_server and mssql_db and mssql_driver):
            st.error("Please Provide SQL server, database and ODBC Driver.")
            st.stop()
        # Build ODBC connection string
        # Note: SERVER supports HOST, HOST\\INSTANCE, or HOST,PORT
        base=(
            f"DRIVER={{{mssql_driver}}};"
            f"SERVER={mssql_server};"
            f"DATABASE={mssql_db};"
            f"Encrypt=yes;"
            f"TrustServerCertificate={'yes' if mssql_trust_cert else 'no'};"
        )
        if mssql_auth == "Windows (Integrated)":
            odbc_str = base+"Trusted_connection=yes;"
        else:
            if not (mssql_user and mssql_password):
                st.error("Provide SQL Login and Password for SQL Login auth.")
                st.stop()
            odbc_str = base + f"UID={mssql_user};PWD={mssql_password};Trusted_Connection=no;"

        connect_uri = "mssql+pyodbc:///?odbc_connect=" + quote_plus(odbc_str)
        engine = create_engine(connect_uri, fast_executemany=True)
        return SQLDatabase(engine)
    else:
        st.error("Unsupported database choice.")
        st.stop()
        

if db_url == MYSQL:
    db = configure_db(
        db_url,
        mysql_host=mysql_host, mysql_user=mysql_user, mysql_password=mysql_password, mysql_db=mysql_db
    )
elif db_url == MSSQL:
    db = configure_db(
        db_url,
        mssql_server=mssql_server,
        mssql_db=mssql_db,
        mssql_auth=msssql_auth,
        mssql_user=mssql_user,
        mssql_password=mssql_password,
        mssql_trust_cert=mssql_trust_cert,
        mssql_driver=mssql_driver
    )    
else:
    db = configure_db(db_url)
    
    
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent  = create_sql_agent(llm=llm,toolkit=toolkit,verbose=True,agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role":"assistant","content":"How can i help you?"}]
    
    
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])
    
    
user_query = st.chat_input(placeholder="Ask anything from the database....")

if user_query:
    st.session_state.messages.append({"role":"user","content":user_query})
    st.chat_message("user").write(user_query)
    
    with st.chat_message("assistant"):
        streamlit_callback  = StreamlitCallbackHandler(st.container())
        response = agent.run(user_query,callbacks=[streamlit_callback])
        st.session_state.messages.append({"role":"assistant","content":"response"})
        st.write(response)