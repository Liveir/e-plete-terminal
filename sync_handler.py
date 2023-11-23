# rfid_handler.py


import asyncio
import aiohttp
from datetime import datetime
from connection_handler import ConnectionHandler

# Handles all routines for asynchronous operation of syncing the data 
# stored locally in the terminal to the database upon detection of 
# LAN connection.

class SyncHandler:
    def __init__(self):
        self.connection_handler = ConnectionHandler() # instantiated to be able to use check_connection()

    async def handle_events(self, rfid_handler):
        """
        Asynchronous method to handle events and synchronize transactions.

        Args:
            rfid_handler (RFIDHandler): An instance of the RFIDHandler class.

        Returns:
            None
        """
        while True:
            if await self.connection_handler.check_connection():
                await self.sync_transactions(rfid_handler)
            await asyncio.sleep(1)

    async def sync_transactions(self, rfid_handler):
        """
        Asynchronously syncs transactions with the server.

        Args:
            rfid_handler (RFIDHandler): An instance of the RFIDHandler class.

        Returns:
            None
        """
        async with rfid_handler.lock:
            if not await self.connection_handler.check_connection():
                print("API endpoint not found.")
                return

            print("API endpoint connection successful.")

            if await self.deduct_balance(rfid_handler.current_transactions):
                rfid_handler.clear_transactions()
                await rfid_handler.store_student_data()

    async def deduct_balance(self, current_transactions):
        """
        Asynchronously deducts balances based on current transactions.

        Args:
            current_transactions (dict): A dictionary of current transactions.

        Returns:
            bool: True if deduction is successful, False otherwise.
        """
        students_endpoint = 'http://192.168.0.105:8000/student/'

        async with aiohttp.ClientSession() as session:
            print(current_transactions)
            if current_transactions == {}:
                print("No transactions found.")
                return False
            try:
                async with session.get(students_endpoint) as response:
                    students_data = await response.json()
                    for tag, amount in current_transactions.items():
                        student_match = next((student for student in students_data if student['RFID'] == tag), None)
                        if student_match:
                            student_match['StudentBalance'] -= amount
                            student_endpoint = f"http://192.168.0.105:8000/student/{student_match['StudentId']}/"
                            async with session.put(student_endpoint, json=student_match) as response:
                                print("Student data synced successfully.")
                                await self.add_transaction(session, student_match, amount)
                                return True

            except aiohttp.ClientError as e:
                print(f"Error syncing data: {e}")
                return False
            
    async def add_transaction(self, session, student, amount):
        """
        Asynchronously adds a new transaction record.

        Args:
            session (aiohttp.ClientSession): An aiohttp session.
            student (dict): Student information.
            amount (float): Transaction amount.

        Returns:
            None
        """
        transactions_endpoint = 'http://192.168.0.105:8000/transaction/'
        transaction_id = int(datetime.now().strftime("%y%m%d%H%M%S"))
        transaction_data = {
            "TransactionId": transaction_id,
            "TransactionDate": datetime.now().strftime("%Y-%m-%d"),
            "TransactionTime": datetime.now().strftime("%I:%M:%S %p"),
            "TransactionAmount": amount,
            "Student": student,
            "TransactionType": "payment"
        }

        try:
            async with session.post(transactions_endpoint, json=transaction_data) as response:
                print("Transaction record added successfully.")
        except aiohttp.ClientError as e:
            print(f"Error adding transaction record: {e}")
