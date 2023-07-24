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
    """
    Description: To add a new user to the User Database
    returns: success/failed status
    """
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

        response_msg["message"] =  "User add Successfully!"
        logger.info(response_msg)
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(response_msg)
    finally:
        cursor.close()
        conn.close()
    return response_msg

@app.post("/newMerchant")
def new_merchant(merchant: MerchantCreate):
    """
        Description: To add a new merchant to the Data base
        returns: success/failed status
    """
    response_msg = {
        "status": "success",
        "data": None,
        "message": None
    }

    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = f"INSERT INTO merchant (name, email, fee) VALUES ('{merchant.name}', '{merchant.email}', {merchant.fee})"
        cursor.execute(query)
        conn.commit()

        response_msg["message"] = "Merchant added Successfully!"
        logger.info(response_msg)
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(response_msg)
    finally:
        cursor.close()
        conn.close()
    return response_msg


@app.post("/transact")
async def transact(transaction: TransactionCreate):
    """
        Description: Perform a transaction between a user and a merchant.
        Returns: success/failed status
    """
    response_msg = {
        "status": "success",
        "data": None,
        "message": None
    }

    try:
        conn = create_connection()
        cursor = conn.cursor(buffered=True)

        query = f"SELECT balance FROM user WHERE user_id={transaction.u_id}"
        cursor.execute(query)
        balance = float(cursor.fetchone()[0])

        # if user not having sufficent credit limit
        if balance >= transaction.amount:
            # adding transaction to the Transaction table
            query = f"INSERT INTO transactions (u_id, m_id, amount) VALUES ({transaction.u_id}, {transaction.m_id}, {transaction.amount})"
            cursor.execute(query)
            conn.commit()

            # Updating user balance accordingly
            query = f"UPDATE user SET balance={balance - transaction.amount} WHERE user_id={transaction.u_id}"
            cursor.execute(query)
            conn.commit()
            response_msg["message"] = "Transaction successfully updated!"
        else:
            response_msg["status"] = "failed"
            response_msg["message"] = "Insufficient balance"
        logger.info(response_msg)
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(response_msg)
    finally:
        cursor.close()
        conn.close()
    return response_msg


@app.get("/getMerchant/{mid}")
async def get_merchant(mid: int):
    """
        Description:  Get merchant information by merchant ID.
        Returns:If successful, the data will contain merchant information. If failed,
              the status will be "failed" and the messege will contain the error details.
    """
    response_msg = {
        "status": "success",
        "data": None,
        "message": None
    }

    try:
        conn = create_connection()
        cursor = conn.cursor(buffered=True)
        cursor.execute(f"SELECT * FROM merchant WHERE merchant_id={mid}")
        response_json = to_json(cursor)
        response_msg["data"] = response_json

        response_msg["message"] = "Merchant retrieved successfully"
        logger.info(response_msg)
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(response_msg)
    finally:
        cursor.close()
        conn.close()

    return response_msg


@app.post("/updateFee")
async def update_fee(mid: int, fee: int):
    """
    Description: Update the fee for a specific merchant.
    Returns: success/failed status.
    """
    response_msg = {
        "status": "success",
        "data": None,
        "message": None
    }
   
    try:
        conn = create_connection()
        cursor = conn.cursor()
         # Updating merchant accordingly
        query = f"UPDATE merchant SET fee={fee} WHERE merchant_id={mid}"
        cursor.execute(query)
        conn.commit()

        response_msg["message"] = "Merchant fee updated successfully"
        logger.info(response_msg)
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(response_msg)
    finally:
        cursor.close()
        conn.close()

    return response_msg


@app.post("/repay")
async def repay(name: str, amount: int):
    """
    Description: Perform a repayment for a specific user
    Returns: If successful, the message will indicate the success. If failed,
            the status will be "failed" and the message will contain the error details.

    """
    response_msg = {
        "status": "success",
        "data": None,
        "message": None
    }

    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = f"SELECT balance FROM user WHERE name='{name}'"
        cursor.execute(query)
        balance = float(cursor.fetchone()[0])

        # here we are updating the balance and amount accordingly
        query = f"UPDATE user SET balance={balance + amount} WHERE name='{name}'"
        cursor.execute(query)
        conn.commit()

        response_msg["message"] = "Repayment successful"
        logger.info(response_msg)
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(response_msg)
    finally:
        cursor.close()
        conn.close()

    return response_msg


@app.get("/fee/{merchant}")
async def get_merchant_fee(merchant: str):
    """
    Description: Get the fee for a specific merchant by their name.
    Returns: succes/failed status
    """
    response_msg = {
        "status": "success",
        "data": None,
        "message": None
    }

    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = f"SELECT fee FROM merchant WHERE name='{merchant}'"
        cursor.execute(query)
        fee = float(cursor.fetchone()[0])

        response_msg["data"] = {"fee": fee}
        response_msg["message"] = "Merchant fee retrieved successfully"
        logger.info(response_msg)
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(response_msg)
    finally:
        cursor.close()
        conn.close()

    return response_msg


@app.get("/dues/{user}")
async def get_user_dues(user: str):
    """
    Description : Get the total dues for a specific user.
    Returns : If successful, the data will contain the user's total dues. If failed,
        the status will be "failed" and the message will contain the error details.
    """
    response_msg = {
        "status": "success",
        "data": None,
        "message": None
    }

    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = f"SELECT SUM(amount) FROM transactions WHERE u_id=(SELECT user_id FROM user WHERE name='{user}')"
        cursor.execute(query)
        dues = float(cursor.fetchone()[0])

        response_msg["data"] = {"dues": dues}
        response_msg["message"] = "User dues retrieved successfully"
        logger.info(response_msg)
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(response_msg)
    finally:
        cursor.close()
        conn.close()

    return response_msg


@app.get("/usersAtLimit")
async def get_users_at_limit():
    """
    Description: Get the list of users who have reached the default credit limit.
    Returns:If successful, the data will contain a list of users. If failed,
        the status will be "failed" and the message will contain the error details.
    """
    response_msg = {
        "status": "success",
        "data": None,
        "message": None
    }

    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = f"SELECT name FROM user WHERE balance={DEFAULT_CREDIT_LIMIT}"
        cursor.execute(query)
        users = [row[0] for row in cursor.fetchall()]

        response_msg["data"] = {"users": users}
        response_msg["message"] = "Users at credit limit retrieved successfully"
        logger.error(response_msg)
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(response_msg)
    finally:
        cursor.close()
        conn.close()

    return response_msg


@app.get("/totalDues")
async def get_total_dues():
    """
    Description: Get the total dues of all transactions.
    Returns:If successful, the data will contain the total dues. If failed,
        the status will be "failed" and the message will contain the error details.
    """
    response_msg = {
        "status": "success",
        "data": None,
        "message": None
    }

    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = "SELECT SUM(amount) FROM transactions"
        cursor.execute(query)
        total_dues = float(cursor.fetchone()[0])
        response_msg["data"] = {"total_dues": total_dues}
        
        response_msg["message"] = "Total dues retrieved successfully"
        logger.info(response_msg)
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(response_msg)

    return response_msg
