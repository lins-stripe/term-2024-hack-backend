#!/usr/bin/env python

import asyncio
import sqlite3

import json
from websockets.asyncio.server import serve

'''
input
{
    "amount": <int>
}
'''


async def set_in_db(amount):
    with sqlite3.connect('example.db') as connection:
        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # 3. Create a Table
        # Let's create a simple table named 'users' with three columns: id, name, and age
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY,
                amount INTEGER NOT NULL
            )
        ''')

        # Commit the changes to the database (this saves the changes)
        connection.commit()

        # 4. Insert Data
        cursor.execute('''
            REPLACE INTO requests (id, amount)
            VALUES (1, ?)
        ''', (amount,))

        # Commit the changes to the database
        connection.commit()

        # # 5. Query Data
        # # Query the data from the 'users' table to ensure it was inserted correctly
        cursor.execute('SELECT * FROM requests ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()  # Fetch all rows from the executed query
        print(row)

        # return id
        return[row][0][0]

async def access_db(id):
    print("hih")
    with sqlite3.connect('example.db') as connection:
        print("accessing db")
        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # 4. Insert Data
        cursor.execute('''
            SELECT amount FROM requests WHERE id = ?
        ''', (id,))

        # # 5. Query Data
        # # Query the data from the 'users' table to ensure it was inserted correctly
        # cursor.execute('SELECT * FROM users')
        rows = cursor.fetchall()  # Fetch all rows from the executed query
        print("accessed row")

        print(rows)
        ret_val = None
        if len(rows) == 0:
            return None
        else:
            ret_val = rows[-1][0]
        
        cursor.execute('''
            DELETE FROM requests WHERE id = 1
        ''')
        connection.commit()

        return ret_val


'''
input:
{
    "amount": <int>
}
'''
async def set_amount(websocket):
    req = await websocket.recv()
    print(f"set_amount recieved {req}")

    # parse the req json object
    req_json = {}
    try:
        req_json = json.loads(req)
        print(f"Received JSON object: {req_json}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        await websocket.send("error")
        return
    
    id = await set_in_db(req_json["amount"])

    await websocket.send(f"{id}")
    print(f"done")

'''
input:
{
    "id": <int>
}
'''
async def get_amount(websocket):
    print(f"get_amount recieved")
    req = await websocket.recv()

    # parse the req json object
    req_json = {}
    try:
        req_json = json.loads(req)
        print(f"Received JSON object: {req_json}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        await websocket.send("error")
        return

    amount = await access_db(req_json["id"])

    if amount == None:
        await websocket.send("")
        return
    
    await websocket.send(f"{amount}")
    print(f"done")

async def handler(websocket):
    if websocket.request.path == "/set_amount":
        await set_amount(websocket)
    elif websocket.request.path == "/get_amount":
        await get_amount(websocket)
    else:
        return

async def main():
    async with serve(handler, "localhost", 8765):
        await asyncio.get_running_loop().create_future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
