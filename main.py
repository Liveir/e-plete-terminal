# main.py

import asyncio
from rfid_handler import RFIDHandler
from sync_handler import SyncHandler

# Author/s:
# Description: This program manages RFID transactions via a portable terminal device
#              and synchronizes data with a remote server.

async def main():
    """
    Asynchronous main function to initialize and run RFID and synchronization handlers
    in parallel.

    Args:
        None

    Returns:
        None
    """
    rfid_handler = RFIDHandler()
    sync_handler = SyncHandler()

    tasks = [
        asyncio.create_task(rfid_handler.store_student_data()), # asynchronously fetches latest student data once
        asyncio.create_task(rfid_handler.handle_events()), # handler for RFID events
        asyncio.create_task(sync_handler.handle_events(rfid_handler)), # handler for synchronization of local data with remote server
    ]
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
