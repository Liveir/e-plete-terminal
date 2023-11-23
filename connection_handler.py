# connection_handler.py

import subprocess

# Handler for checking LAN connection to the IP address
# where the database server is hosted.

class ConnectionHandler:
    async def check_connection(self):
        """
        Checks the network connection to a specified IP address.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        try:
            # Use subprocess to run a ping command to check the connection
            # '-c 1': sends only one packet
            # '192.168.0.105': IP address to ping
            # check=True: raises CalledProcessError for non-zero return codes
            # stdout=subprocess.PIPE: captures the output, but it's not used here
            subprocess.run(['ping', '-c', '1', '192.168.0.105'], check=True, stdout=subprocess.PIPE)
            return True  # Connection successful
        except subprocess.CalledProcessError:
            return False  # Connection failed
