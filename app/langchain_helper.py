import os

from dotenv import load_dotenv
from langchain.chains import create_sql_query_chain
from langchain.prompts import (
    FewShotPromptTemplate,
    PromptTemplate,
    SemanticSimilarityExampleSelector,
)
from langchain_community.utilities import (
    SQLDatabase,  # <-- adapt if your langchain has SQLDatabase elsewhere
)
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings

from app.few_shots import few_shots_questions as few_shots

load_dotenv()


# read from env if not passed
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")


def get_db():
    """Get database connection"""
    db_uri = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return SQLDatabase.from_uri(db_uri, sample_rows_in_table_info=3)


def get_llm():
    """Initialize LLM"""
    return ChatGoogleGenerativeAI(
        model=os.getenv("GOOGLE_MODEL", "gemini-2.5-flash"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.1,
    )


def get_few_shot_prompt():
    """Create and return the few-shot prompt template"""
    # Embeddings setup
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    to_vectorize = [" ".join(example.values()) for example in few_shots]

    vectorstore = Chroma.from_texts(
        texts=to_vectorize, embedding=embeddings, metadatas=few_shots
    )

    example_selector = SemanticSimilarityExampleSelector(
        vectorstore=vectorstore,
        k=2,
        input_keys=["input"],
    )

    postgresql_prefix = """You are a **PostgreSQL expert**. Given an input question, first create a syntactically correct PostgreSQL query to run, then look at the results of the query and return the answer to the input question.
    Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the **FETCH FIRST {top_k} ROWS ONLY** clause as per PostgreSQL. You can order the results to return the most informative data in the database.
    Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
    Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
    Pay attention to use **CURRENT_DATE** or **NOW()::date** function to get the current date, if the question involves "today".

    Use the following format:

    Question: Question here
    SQLQuery: Query to run with no pre-amble
    SQLResult: Result of the SQLQuery
    Answer: Final answer here

    No pre-amble.
    """

    example_prompt = PromptTemplate(
        input_variables=["input", "SQLQuery", "SQLResult", "Answer"],
        template="\nQuestion: {input}\nSQLQuery: {SQLQuery}\nSQLResult: {SQLResult}\nAnswer: {Answer}",
    )

    return FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix=postgresql_prefix,
        suffix="""{table_info}\n\nQuestion: {input}\nSQLQuery:""",
        input_variables=["input", "table_info", "top_k"],
    )


def get_few_shot_db_chain():
    """Create and return the database chain"""
    db = get_db()
    llm = get_llm()
    few_shot_prompt = get_few_shot_prompt()

    return (
        create_sql_query_chain(
            llm=llm,
            db=db,
            prompt=few_shot_prompt,
        ),
        db,
    )


def execute_query(chain, db, question: str):
    """Execute a query and return the formatted response"""
    # First, get the SQL query using the chain
    question_data = {
        "question": question,
        "table_info": db.table_info,
        "top_k": 100,
        "input": question,  # Added this for the few-shot prompt
    }

    # Get the SQL query
    sql_query = chain.invoke(question_data)

    # Execute the SQL query
    sql_result = db.run(sql_query)

    # Format the final response using LLM
    template = f"""Based on the SQL query and its result, provide a clear answer to the question.
    Question: {question}
    SQL Query: {sql_query}
    Query Result: {sql_result}
    
    Please provide a clear, concise answer in one sentence:"""

    llm = get_llm()
    return llm.invoke(template).content


def process_question(question: str):
    """Main execution function"""
    # Get the chain and database connection
    chain, db = get_few_shot_db_chain()

    response = execute_query(chain, db, question)
    return response
