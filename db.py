from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from config import mongo_uri,db_name 

client = MongoClient(mongo_uri, server_api=ServerApi("1"))

try:
    client.admin.command("ping")
    print("Connected to MongoDB")
    client.get_database("users").get_collection("users")

except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")

async def get_user(user_id: int):
    try:
        user = client.get_database(db_name).get_collection("users").find_one({"user_id": user_id})
        if user:
            transactions = list(
                client.get_database(db_name)
                .get_collection("transactions")
                .find({"user_id": user_id})
                .sort("createdAt", -1)
            )
            client.get_database(db_name).get_collection("users").update_one(
                {"user_id": user_id},
                {"$set": {"transactions": transactions}},
            )
            user["transactions"] = transactions
            return user
        return None
    except Exception as e:
        print(f"Failed to get user {user_id}: {e}")
        return None

async def create_user(user_id: int):
    try:
        client.get_database(db_name).get_collection("users").insert_one(
            {
                "user_id": user_id,
                "balance": 0,
                "transactions": [],
            }
        )
        log = f"Created user {user_id}"
        return log
    except Exception as e:
        error = f"Failed to create user {user_id}: {e}"
        return error

async def get_user_balance(user_id: int) -> int:
    try:
        user = await get_user(user_id)
        if user:
            balance = user.get("balance", 0)
            return balance 
        elif user is None:
            await create_user(user_id)
            return 0
        else:
            raise ValueError("User not found")
    except Exception as e:
        print(f"Failed to get balance for user {user_id}: {e}")
        return 0
    
async def get_last_transaction(user_id: int):
    try:
        transaction = client.get_database(db_name).get_collection("transactions").find_one(
            {"user_id": user_id},
            sort=[("createdAt", -1)]
        )
        if transaction:
            return transaction
        return None
    except Exception as e:
        print(f"Failed to get last transaction for user {user_id}: {e}")
        return None

async def deposit(user_id: int, amount: int):
    balance = await get_user_balance(user_id)
    try:
        transaction = {
            "type": "deposit",
            "amount": amount,
            "user_id": user_id,
            "createdAt": datetime.now(),
        }

        client.get_database(db_name).get_collection("transactions").insert_one(transaction)
        client.get_database(db_name).get_collection("users").update_one(
            {"user_id": user_id},
            {
                "$set": {"balance": balance + amount},
                "$push": {"transactions": transaction}
            },
            upsert=True,
        )

        return True
    except Exception as e:
        error = f"Failed to deposit {amount} to user {user_id}: {e}"
        print(error)
        return False

async def withdraw(user_id: int, amount: int):
    balance = await get_user_balance(user_id)
    try:
        if balance < amount:
            raise ValueError("Insufficient balance")
        transaction = {
            "type": "withdraw",
            "amount": amount,
            "user_id": user_id,
            "createdAt": datetime.now(),
        }

        client.get_database(db_name).get_collection("transactions").insert_one(transaction)
        client.get_database(db_name).get_collection("users").update_one(
            {"user_id": user_id},
            {
                "$set": {"balance": balance - amount},
                "$push": {"transactions": transaction}
            },
            upsert=True,
        )
        return True
    except Exception as e:
        error = f"Failed to withdraw {amount} from user {user_id}: {e}"
        print(error)
        return False

async def add_payment_method(user_id: int,method_type: str, data: dict ):
    method = {
            "type": method_type,
            "data": data
        }
    
    try:
        client.get_database(db_name).get_collection("users").update_one(
            {"user_id": user_id},
            {
                "$push": {"payment_methods": method}
            },
            upsert=True,
        )
        return True
    except Exception as e:
        error = f"Failed to add {method_type} payment method to user {user_id}: {e}"
        print(error)
        return False
    
async def get_payment_methods(user_id: int) -> list[dict]:
    try:
        user = await get_user(user_id)
        if user:
            payment_methods = user.get("payment_methods", [])
            return payment_methods
        return []
    except Exception as e:
        print(f"Failed to get payment methods for user {user_id}: {e}")
        return []