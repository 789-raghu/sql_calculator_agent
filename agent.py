import streamlit as st
import sqlite3
import os
import json
from langchain.utilities import SQLDatabase
from langchain.llms import OpenAI
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent
from langchain.agents.agent_types import AgentType
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Streamlit app
st.title('SQL Database Chatbot')

# Request API key at the beginning of each session
api_key = st.text_input('Enter your OpenAI API key:', type='password')

if api_key:
    os.environ['OPENAI_API_KEY'] = api_key

    # Path to the database
    database_file_path = './sql_lite_database.db'

    # Function to set up the database
    def setup_database():
        if os.path.exists(database_file_path):
            os.remove(database_file_path)
            st.write("File 'sql_lite_database.db' found and deleted.")
        else:
            st.write("File 'sql_lite_database.db' does not exist.")

        # Connect to the database
        conn = sqlite3.connect(database_file_path)
        cursor = conn.cursor()

        # Create tables
        create_table_query1 = """
        CREATE TABLE IF NOT EXISTS SUPPLIERS (
            SUPPLIER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME TEXT NOT NULL,
            ADDRESS TEXT NOT NULL,
            CONTACT TEXT NOT NULL
        );
        """
        create_table_query2 = """
        CREATE TABLE IF NOT EXISTS PRODUCTS (
            PRODUCT_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME TEXT NOT NULL,
            DESCRIPTION TEXT NOT NULL,
            PRICE REAL NOT NULL,
            SUPPLIER_ID INTEGER NOT NULL,
            FOREIGN KEY (SUPPLIER_ID) REFERENCES SUPPLIERS(SUPPLIER_ID)
        );
        """
        create_table_query3 = """
        CREATE TABLE IF NOT EXISTS INVENTORY (
            INVENTORY_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            PRODUCT_ID INTEGER NOT NULL,
            QUANTITY INTEGER NOT NULL,
            MIN_REQUIRED INTEGER NOT NULL,
            FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCTS(PRODUCT_ID)
        );
        """
        queries = [create_table_query1, create_table_query2, create_table_query3]
        for query in queries:
            cursor.execute(query)

        # Insert data into the tables
        suppliers_data = [
            {"name": "Samsung Electronics", "address": "Seoul, South Korea", "contact": "800-726-7864"},
            {"name": "Apple Inc.", "address": "Cupertino, California, USA", "contact": "800–692–7753"},
            {"name": "OnePlus Technology", "address": "Shenzhen, Guangdong, China", "contact": "400-888-1111"},
            {"name": "Google LLC", "address": "Mountain View, California, USA", "contact": "855-836-3987"},
            {"name": "Xiaomi Corporation", "address": "Beijing, China", "contact": "1800-103-6286"},
        ]
        products_data = [
            {"name": "Samsung Galaxy S21", "description": "Samsung flagship smartphone", "price": 799.99, "supplier_id": 1},
            {"name": "Samsung Galaxy Note 20", "description": "Samsung premium smartphone with stylus", "price": 999.99, "supplier_id": 1},
            {"name": "iPhone 13 Pro", "description": "Apple flagship smartphone", "price": 999.99, "supplier_id": 2},
            {"name": "iPhone SE", "description": "Apple budget smartphone", "price": 399.99, "supplier_id": 2},
            {"name": "OnePlus 9", "description": "High performance smartphone", "price": 729.00, "supplier_id": 3},
            {"name": "OnePlus Nord", "description": "Mid-range smartphone", "price": 499.00, "supplier_id": 3},
            {"name": "Google Pixel 6", "description": "Google's latest smartphone", "price": 599.00, "supplier_id": 4},
            {"name": "Google Pixel 5a", "description": "Affordable Google smartphone", "price": 449.00, "supplier_id": 4},
            {"name": "Xiaomi Mi 11", "description": "Xiaomi high-end smartphone", "price": 749.99, "supplier_id": 5},
            {"name": "Xiaomi Redmi Note 10", "description": "Xiaomi budget smartphone", "price": 199.99, "supplier_id": 5},
        ]
        inventory_data = [
            {"product_id": 1, "quantity": 150, "min_required": 30},
            {"product_id": 2, "quantity": 100, "min_required": 20},
            {"product_id": 3, "quantity": 120, "min_required": 30},
            {"product_id": 4, "quantity": 80, "min_required": 15},
            {"product_id": 5, "quantity": 200, "min_required": 40},
            {"product_id": 6, "quantity": 150, "min_required": 25},
            {"product_id": 7, "quantity": 100, "min_required": 20},
            {"product_id": 8, "quantity": 90, "min_required": 18},
            {"product_id": 9, "quantity": 170, "min_required": 35},
            {"product_id": 10, "quantity": 220, "min_required": 45},
        ]

        for supplier in suppliers_data:
            cursor.execute("""
                INSERT INTO SUPPLIERS (NAME, ADDRESS, CONTACT)
                VALUES (?, ?, ?)
            """, (supplier['name'], supplier['address'], supplier['contact']))

        for product in products_data:
            cursor.execute("""
                INSERT INTO PRODUCTS (NAME, DESCRIPTION, PRICE, SUPPLIER_ID)
                VALUES (?, ?, ?, ?)
            """, (product['name'], product['description'], product['price'], product['supplier_id']))

        for inventory in inventory_data:
            cursor.execute("""
                INSERT INTO INVENTORY (PRODUCT_ID, QUANTITY, MIN_REQUIRED)
                VALUES (?, ?, ?)
            """, (inventory['product_id'], inventory['quantity'], inventory['min_required']))

        conn.commit()
        cursor.close()
        conn.close()

    # Setup the database
    setup_database()

    # Connect to the database
    db = SQLDatabase.from_uri('sqlite:///sql_lite_database.db')

    # Initialize OpenAI LLM
    llm = OpenAI(
        temperature=0,
        verbose=True,
        openai_api_key=api_key
    )

    # Setup agent
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )

    # Chat box for user to ask questions
    st.write("## Ask a question about the database:")
    question = st.text_input("Your question:")

    if st.button("Submit"):
        if question:
            # Process the user's question using the agent
            response = agent_executor.run(question)
            st.write("### Response:")
            st.write(response)
        else:
            st.write("Please enter a question.")
else:
    st.write("Please enter your OpenAI API key to proceed.")
