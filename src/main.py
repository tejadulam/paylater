from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mysql.connector import connection
from common import logger

DEFAULT_CREDIT_LIMIT = 2000

app = FastAPI()

def create_connection():
    return connection.MySQLConnection(
        host='127.0.0.1',
        user='teju',
        password='teju',
        database='paylater'
    )

def to_json(cursor):
    columns = [column[0] for column in cursor.description]
    
    response_json = []
    for row in cursor.fetchall():
        data = dict(zip(columns, row))
        response_json.append(data)
    return response_json

class UserCreate(BaseModel):
    name: str
    email: str
    balance: int

class MerchantCreate(BaseModel):
    name: str
    email: str
    fee: int

class TransactionCreate(BaseModel):
    u_id: int
    m_id: int
    amount: int

@app.post("/newUser")
async def new_user(user: UserCreate):
    response_msg = {
        "status" : "success",
        "data" : None,
        "message" : None
    }
    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = f"INSERT INTO user (name, email, balance) VALUES ('{user.name}', '{user.email}', {user.balance})"
        cursor.execute(query)
        conn.commit()

        msg = "User add Successfully!"
        logger.info(msg)
        response_msg["message"] = msg
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
    finally:
        cursor.close()
        conn.close()
    return response_msg

@app.post("/newMerchant")
def new_merchant(merchant: MerchantCreate):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = f"INSERT INTO merchant (name, email, fee) VALUES ('{merchant.name}', '{merchant.email}', {merchant.fee})"
        cursor.execute(query)
        conn.commit()
        response = {"message": "Merchant added successfully!"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        cursor.close()
        conn.close()
    return response

@app.post("/transact")
async def transact(transaction: TransactionCreate):
    try:
        conn = create_connection()
        cursor = conn.cursor(buffered=True)

        query = f"INSERT INTO transactions (u_id, m_id, amount) VALUES ({transaction.u_id}, {transaction.m_id}, {transaction.amount})"
        cursor.execute(query)
        conn.commit()

        query = f"SELECT balance FROM user WHERE user_id={transaction.u_id}"
        cursor.execute(query)
        balance = float(cursor.fetchone()[0])

        if balance >= transaction.amount:
            query = f"UPDATE user SET balance={balance - transaction.amount} WHERE user_id={transaction.u_id}"
            cursor.execute(query)
            conn.commit()
            response = {"message": "Transaction successfully updated!"}
        else:
            response = {"error": "Insufficient balance"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        cursor.close()
        conn.close()
    return response
@app.get("/getMerchant/{mid}")
async def get_merchant(mid: int):
    conn = create_connection()
    cursor = conn.cursor(buffered=True)
    cursor.execute(f"SELECT * FROM merchant WHERE merchant_id={mid}")
    response_json = to_json(cursor)
    cursor.close()
    conn.close()
    return response_json

@app.post("/updateFee")
async def update_fee(mid: int, fee: int):
    conn = create_connection()
    cursor = conn.cursor()
    query = f"UPDATE merchant SET fee={fee} WHERE merchant_id={mid}"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Merchant fee updated successfully!"}

@app.post("/repay")
async def repay(name: str, amount: int):
    conn = create_connection()
    cursor = conn.cursor()
    query = f"SELECT balance FROM user WHERE name='{name}'"
    cursor.execute(query)
    balance = float(cursor.fetchone()[0])

    query = f"UPDATE user SET balance={balance + amount} WHERE name='{name}'"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Repayment successful!"}

@app.get("/fee/{merchant}")
async def get_merchant_fee(merchant: str):
    conn = create_connection()
    cursor = conn.cursor()
    query = f"SELECT fee FROM merchant WHERE name='{merchant}'"
    cursor.execute(query)
    fee = float(cursor.fetchone()[0])
    cursor.close()
    conn.close()
    return {"fee": fee}

@app.get("/dues/{user}")
async def get_user_dues(user: str):
    conn = create_connection()
    cursor = conn.cursor()
    query = f"SELECT SUM(amount) FROM transactions WHERE u_id=(SELECT user_id FROM user WHERE name='{user}')"
    cursor.execute(query)
    dues = float(cursor.fetchone()[0])
    cursor.close()
    conn.close()
    return {"dues": dues}

@app.get("/usersAtLimit")
async def get_users_at_limit():
    conn = create_connection()
    cursor = conn.cursor()
    query = f"SELECT name FROM user WHERE balance={DEFAULT_CREDIT_LIMIT}"
    cursor.execute(query)
    users = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return {"users": users}

@app.get("/totalDues")
async def get_total_dues():
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT SUM(amount) FROM transactions"
    cursor.execute(query)
    total_dues = float(cursor.fetchone()[0])
    cursor.close()
    conn.close()
    return {"total_dues": total_dues}

