# rfid_handler.py

import asyncio
import aiohttp
from connection_handler import ConnectionHandler

# Handles all routines for asynchronous operation of receiving
# data from an RFID tag-reader and stores relevant information
# locally.

class RFIDHandler:
    def __init__(self):
        self.current_transactions = {} # local storage of all transactions made via RFID-tap
        self.student_balance = {} # local storage of students' balance
        self.lock = asyncio.Lock() # resource lock to prevent parallel access of coroutines
        self.connection_handler = ConnectionHandler() # instantiated to be able to use check_connection()

    async def handle_events(self):
        """
        Asynchronous method to handle RFID events.

        This method simulates RFID events, checks balances, and stores transactions.

        Args:
            None

        Returns:
            None
        """
        while True:
            await asyncio.sleep(5)

            # Dummy RFID tag and amount
            # tag = "3f09d0a9-9ef3-4142-81b6-bc6c121a3417"
            # amount = 10

            tag = ''
            amount = 0

            # ! RFID READING LOGIC GOES HERE (create your function)
            # ! store RFID tag in 'tag'
            # ! adjust fare pricing with 'amount'

            async with self.lock:
                allow_transaction = await self.check_balance(tag, amount)
                if allow_transaction:
                    if tag in self.current_transactions:
                        # Key already exists, add the new amount to the existing value
                        self.current_transactions[tag] += amount
                        self.student_balance[tag] -= amount
                    else:
                        # Key doesn't exist, set the value to the new amount
                        self.current_transactions[tag] = amount
                    print(self.current_transactions)
                    print(self.student_balance)
                    print(f"RFID tag {tag} tapped. Amount: {amount} - Transaction stored.")
                else:
                    print(f"RFID tag {tag} tapped. Amount: {amount} - Transaction not stored (insufficient balance).")

            await asyncio.sleep(5)

    async def check_balance(self, tag, amount):
        """
        Asynchronously checks the balance of a student.

        Args:
            tag (str): RFID tag of the student.
            amount (float): Transaction amount.

        Returns:
            bool: True if the transaction is allowed, False otherwise.
        """
        student_balance = self.student_balance.get(tag, 0)
        if student_balance >= amount:
            return True
        else:
            return False
            
    async def store_student_data(self):
        """
        Asynchronously fetches and stores student balances.

        Args:
            None

        Returns:
            None
        """
        while True:
            students_endpoint = 'http://192.168.0.105:8000/student/'
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(students_endpoint) as response:
                        students_data = await response.json()
                        self.student_balance = {student.get('RFID', ''): student.get('StudentBalance', 0) for student in students_data}
                        print("Student balances stored locally.")
                        break

                except aiohttp.ClientError as e:
                    print(f"Error fetching student balance: {e}")
                    break
            
    def clear_transactions(self):
        """
        Clears the current transaction data.

        Args:
            None

        Returns:
            None
        """
        self.current_transactions = {}
        print("Transaction data cleared.")
