import psycopg2
from psycopg2.extras import RealDictCursor
#from mcp.server.fastmcp import FastMCP, Context
from InlineAgent.agent import InlineAgent
from InlineAgent.action_group import ActionGroup

import asyncio

# Initialize MCP server
#mcp = FastMCP("PostgresServer")



def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

# ------------------------------
# READ
# ------------------------------
#@mcp.tool()
def get_employee_details(employee_id: int) -> str:
    """
    Get the employee details for the given employee_id from database.

    Parameters:
        employee_id: employee unique id number
    """
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, department, salary FROM employee WHERE id = %s", (employee_id,))
        row = cur.fetchone()
        if row:
            return f"ID: {row['id']}, Name: {row['name']}, Department: {row['department']}, Salary: {row['salary']}"
        else:
            return f"No employee found with ID {employee_id}"
    finally:
        cur.close()
        conn.close()

# @mcp.tool()
def list_employees() -> str:
    """
     Fetch all the employee from database.
     
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, department, salary FROM employee ORDER BY id")
        rows = cur.fetchall()
        if not rows:
            return "No employees found"
        return "\n".join([f"ID: {r['id']}, Name: {r['name']}, Dept: {r['department']}, Salary: {r['salary']}" for r in rows])
    finally:
        cur.close()
        conn.close()

# ------------------------------
# CREATE
# ------------------------------
# @mcp.tool()
def add_employee( name: str, department: str, salary: float) -> str:
    """
    add a new employee or create a employee in database.
    
     Parameters:
        name: employee name,
        department:  employee's department,
        salary: employee's salary
        
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO employee (name, department, salary) VALUES (%s, %s, %s) RETURNING id", 
                    (name, department, salary))
        new_id = cur.fetchone()["id"]
        conn.commit()
        return f"Employee added with ID {new_id}"
    finally:
        cur.close()
        conn.close()

# # ------------------------------
# # UPDATE
# # ------------------------------
# @mcp.tool()
def update_employee(employee_id: int, name: str = None, department: str = None, salary: float = None) -> str:
    """
    Update an existing employee record in database(only provided fields).

    Parameters:
        employee_id: employee'd id
        name: employee name,
        department:  employee's department,
        salary: employee's salary
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        updates, values = [], []
        if name:
            updates.append("name=%s")
            values.append(name)
        if department:
            updates.append("department=%s")
            values.append(department)
        if salary:
            updates.append("salary=%s")
            values.append(salary)

        if not updates:
            return "No fields provided for update"

        values.append(employee_id)
        query = f"UPDATE employee SET {', '.join(updates)} WHERE id=%s RETURNING id"
        cur.execute(query, tuple(values))
        row = cur.fetchone()
        conn.commit()

        if row:
            return f"Employee {employee_id} updated successfully"
        else:
            return f"No employee found with ID {employee_id}"
    finally:
        cur.close()
        conn.close()

# # ------------------------------
# # DELETE
# # ------------------------------
# @mcp.tool()

def delete_employee(employee_id: int) -> str:
    """
    Delete an employee record by ID

    Parameters:
        employee_id: employee'd id
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM employee WHERE id=%s RETURNING id", (employee_id,))
        row = cur.fetchone()
        conn.commit()
        if row:
            return f"Employee {employee_id} deleted successfully"
        else:
            return f"No employee found with ID {employee_id}"
    finally:
        cur.close()
        conn.close()

#@mcp.tool()
def get_knowledge_base( user_query: str) -> str:
    """
    Get the pistachios farming details from AWS bedrock knowwledgebase.

    Parameters:
        user_query: user prompt
    """
    import boto3
    output_text = ""
    response = ""
    # Replace with your values
    REGION = "us-east-1"
    AGENT_ID = "NDIOYYWRVL"       # The Bedrock Agent ID
    AGENT_ALIAS_ID = "TJ2SV1O9JH" # The alias for your agent

    # Create Bedrock Agent Runtime client
    client = boto3.client("bedrock-agent-runtime", region_name=REGION)
     
    print("before invoke agent")
    response = client.invoke_agent(
                agentId=AGENT_ID,
                agentAliasId=AGENT_ALIAS_ID,
                sessionId="streamlit-session",  # session can be static or dynamic
                inputText=user_query
            )
    print("after invoke agent")
    print(response)
    for event in response["completion"]:
        if "chunk" in event:
            output_text += event["chunk"]["bytes"].decode("utf-8")
    return output_text
# ------------------------------
# Run the MCP server
# ------------------------------

def  invoke_agent():
    db_action_group = ActionGroup(
    name="databaseAction",
    description="This is action group to get database details",
    tools=[get_employee_details,add_employee,list_employees,update_employee,delete_employee]
    )

    kb_action_group = ActionGroup(
    name="Knowledgebase",
    description="This is action group to get knowledgebase details",
    tools=[get_knowledge_base]
    )

    agent = InlineAgent(
    foundation_model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    instruction="You are a friendly assistant that is responsible for getting the current weather.",
    action_groups=[db_action_group,kb_action_group],
    agent_name="MockAgent",
    )

    return agent

# if __name__ == "__main__":

#     # db_action_group = ActionGroup(
#     # name="databaseAction",
#     # description="This is action group to get database details",
#     # tools=[get_employee_details]
#     # )

#     # kb_action_group = ActionGroup(
#     # name="Knowledgebase",
#     # description="This is action group to get knowledgebase details",
#     # tools=[get_knowledge_base]
#     # )

#     # agent = InlineAgent(
#     # foundation_model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
#     # instruction="You are a friendly assistant that is responsible for getting the current weather.",
#     # action_groups=[db_action_group,kb_action_group],
#     # agent_name="MockAgent",
#     # )


#     agent=invoke_agent()
#     out=asyncio.run(agent.invoke(input_text="Can you list all the insects that attack the pistachios?"))
#     print("here")
#     print(out)

    