from sqlalchemy import create_engine,text
import pandas as pd
import psycopg2
import json
import pickle



def extract_login(email,password):
    conn_string = "" ""
    conn = psycopg2.connect(conn_string) 
    try:
        cursor = conn.cursor() 
        sql1 = '''select email,password from signup;'''
        cursor.execute(sql1) 
        data = cursor.fetchall()
        df = pd.DataFrame(data=data)
        df.columns = ["email","password"]
        print(df)
        if email in df["email"].values:
            if password == df[df.email == email]["password"].values[0]:
                cursor.close()
                conn.close()
                return True
        else:
            cursor.close()
            conn.close()
            return False
    except Exception as e:
        print(e)
        cursor.close()
        conn.close()
        return False

def signup(name,email,password):
    conn_string = "" ""
    db = create_engine(conn_string)
    con = db.connect()
    values = {"name":[name],"email":[email],"password":[password]}
    df = pd.DataFrame(data=values)
    print(df)
    try:
        df.to_sql("signup",con,if_exists="append",index=False)
        con.close()
    except Exception as e:
        print({e})
        con.close()

def session_store(start,end, email):
    conn_string = "" ""
    db = create_engine(conn_string)
    con = db.connect()
    print(start,end)
    values = {"start":[start],"end":[end], "email":[email]}
    df = pd.DataFrame(data=values)
    print(df)
    try:
        df.to_sql("session",con,if_exists="append",index=False)
        con.close()
    except Exception as e:
        print({e})
        con.close()


def store_question_and_answers(question,answers,email,sources,time):
    conn_string = "" ""
    db = create_engine(conn_string)
    con = db.connect()
    values = {"question":[question],"answers":[answers],"email":[email],"sources":[sources],"time":[time]}
    df = pd.DataFrame(data=values)
    print(df)
    try:
        df.to_sql("questions",con,if_exists="append",index=False)
        con.close()
    except Exception as e:
        print({e})
        con.close()

def serialize_messages(messages):
    serializable = []
    for m in messages:
        if hasattr(m, "model_dump"):  # Responses API objects
            serializable.append(m.model_dump())
        elif isinstance(m, dict):     # Already a dict
            serializable.append(m)
        else:                         # Fallback to string
            serializable.append(str(m))
    return serializable

def store_tool_state(messages,email,tooltype):
    print("storing tools")
    conn_string = "" ""
    db = create_engine(conn_string)
    con = db.connect()
    values_keys = "messages"
    values_vals = json.dumps(serialize_messages(messages))
    try:
        con.execute(text("""
            INSERT INTO toolstate (messages, email,tooltype)
            VALUES (:messages, :email, :tooltype)
            ON CONFLICT (email,tooltype)
            DO UPDATE
            SET messages = EXCLUDED.messages
        """), {"messages": values_vals, "email": email, "tooltype":tooltype})

        con.commit()
        print("Tools stored successfully")

    except Exception as e:
        print("Error:", e)
    finally:
        con.close()


def extract_workflow(email):
    conn_string = ""
    conn = psycopg2.connect(conn_string) 
    try:
        cursor = conn.cursor() 
        sql1 = '''select * from workflows_table where email=%s;'''
        cursor.execute(sql1,(email,)) 
        data = cursor.fetchall()
        df = pd.DataFrame(data=data)
        df.columns = ["workflows","email"]
        workflows = {row["workflows"] for i,row in df.iterrows()}
        cursor.close()
        conn.close()
        return json.loads(list(workflows)[0])
    except Exception as e:
        print(e)
        cursor.close()
        conn.close()
        return None

def update_workflow(email,workflow):
    conn_string = "" ""
    db = create_engine(conn_string)
    con = db.connect()
    existing_values = extract_workflow(email)
    if existing_values is not None:
        existing_values.append(workflow)
    else:
        existing_values = [workflow]
    values_vals = json.dumps(existing_values)
    try:
        con.execute(text("""
            INSERT INTO workflows_table (workflows, email)
            VALUES (:workflows, :email)
            ON CONFLICT (email)
            DO UPDATE
            SET workflows = EXCLUDED.workflows;
        """), {"workflows": values_vals, "email": email})

        con.commit()
    except Exception as e:
        print("Error:", e)
    finally:
        con.close()

def delete_workflows(email):
    conn_string = "" ""
    conn = psycopg2.connect(conn_string) 
    try:
        cursor = conn.cursor() 
        cursor.execute("DELETE FROM workflows_table where email=%s",(email,))
        conn.commit()
        cursor.close()
        conn.close()
        print("All entries deleted successfully.")
    except Exception as e:
        print("Error:", e)
        cursor.close()
        conn.close()


def extract_tool_state(email,tooltype):
    conn_string = ""
    conn = psycopg2.connect(conn_string) 
    try:
        cursor = conn.cursor() 
        sql1 = '''select * from toolstate where email=%s AND tooltype=%s;'''
        cursor.execute(sql1,(email,tooltype,)) 
        data = cursor.fetchall()
        print(data)
        df = pd.DataFrame(data=data)
        df.columns = ["messages","email","tooltype"]
        final_values = {row["messages"] for i,row in df.iterrows()}
        cursor.close()
        conn.close()
        return final_values
    except Exception as e:
        print(e)
        cursor.close()
        conn.close()
        return None


def delete_toolstate(email,tooltype):
    print("deleting tool state")
    conn_string = "" ""
    conn = psycopg2.connect(conn_string) 
    try:
        cursor = conn.cursor() 
        cursor.execute("DELETE FROM toolstate where email=%s AND tooltype=%s",(email,tooltype))
        conn.commit()
        cursor.close()
        conn.close()
        print("All entries deleted successfully.")
    except Exception as e:
        print("Error:", e)
        cursor.close()
        conn.close()


def update_final_values(final_values,email):
    conn_string = "" ""
    db = create_engine(conn_string)
    con = db.connect()
    values = final_values
    values_keys = json.dumps(list(values.keys()))
    values_vals = json.dumps(list(values.values()))
    try:
        con.execute(text("""
            INSERT INTO finalvalues (keys, values, email)
            VALUES (:keys, :values, :email)
            ON CONFLICT (email)
            DO UPDATE
            SET keys = EXCLUDED.keys,
                values = EXCLUDED.values;
        """), {"keys": values_keys, "values": values_vals, "email": email})

        con.commit()
    except Exception as e:
        print("Error:", e)
    finally:
        con.close()

def update_filenames(filenames,email):
    print("In update filenames")
    conn_string = "" ""
    db = create_engine(conn_string)
    con = db.connect()
    values = filenames
    values_keys = list(values.keys())
    values_vals = list(values.values())
    values_keys = json.dumps(list(values.keys()))
    values_vals = json.dumps(list(values.values()))
    try:
        con.execute(text("""
            INSERT INTO filenames (keys, values, email)
            VALUES (:keys, :values, :email)
            ON CONFLICT (email)
            DO UPDATE
            SET keys = EXCLUDED.keys,
                values = EXCLUDED.values;
        """), {"keys": values_keys, "values": values_vals, "email": email})

        con.commit()
    except Exception as e:
        print("Error:", e)
    finally:
        con.close()




def delete_final_values(email):
    conn_string = "" ""
    conn = psycopg2.connect(conn_string) 
    try:
        cursor = conn.cursor() 
        cursor.execute("DELETE FROM finalvalues where email=%s",(email,))
        conn.commit()
        cursor.close()
        conn.close()
        print("All entries deleted successfully.")
    except Exception as e:
        print("Error:", e)
        cursor.close()
        conn.close()

        


def extract_filenames(email):
    print("In extract filenames")
    conn_string = ""
    conn = psycopg2.connect(conn_string) 
    try:
        cursor = conn.cursor() 
        sql1 = '''select * from filenames where email =%s;'''
        cursor.execute(sql1,(email,)) 
        data = cursor.fetchall()
        print(data)
        df = pd.DataFrame(data=data)
        df.columns = ["key","value","email"]
        keys = json.loads(df.iloc[0].key)
        values = json.loads(df.iloc[0].value)
        final_values = {keys[i]:values[i] for i in range(len(keys)) }
        cursor.close()
        conn.close()
        return final_values
    except Exception as e:
        print(e)
        cursor.close()
        conn.close()
        return None




def extract_final_values(email):
    conn_string = "" ""
    conn = psycopg2.connect(conn_string) 
    try:
        cursor = conn.cursor() 
        sql1 = '''select * from finalvalues where email= %s;'''
        cursor.execute(sql1,(email,)) 
        data = cursor.fetchall()
        print(data)
        df = pd.DataFrame(data=data)
        df.columns = ["key","value","email"]
        keys = json.loads(df.iloc[0].key)
        values = json.loads(df.iloc[0].value)
        final_values = {keys[i]:values[i] for i in range(len(keys)) }
        cursor.close()
        conn.close()
        return final_values
    except Exception as e:
        print(e)
        cursor.close()
        conn.close()
        return None



def count_final_values(email):
    conn_string = "" ""
    conn = psycopg2.connect(conn_string) 
    try:
        cursor = conn.cursor() 
        sql1 = '''select count(*) from finalvalues where email=%s;'''
        cursor.execute(sql1,(email,)) 
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except Exception as e:
        print(e)
        cursor.close()
        conn.close()
        return None

def delete_filenames(email):
    conn_string = "" ""
    conn = psycopg2.connect(conn_string) 
    try:
        cursor = conn.cursor() 
        cursor.execute("DELETE FROM filenames where email=%s",(email,))
        conn.commit()
        cursor.close()
        conn.close()
        print("All entries deleted successfully.")
    except Exception as e:
        print("Error:", e)
        cursor.close()
        conn.close()
