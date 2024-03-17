class MsgType:
    # Define message types as class attributes for better organization and readability
    ListRooms      = 'l'
    JoinRoom       = 'r'
    RegularMessage = 'm'
    SetUsername    = 'n'
    InvalidRoom    = 'f'
    RefuseBan      = 'b'
    Notification   = 'j'
    Login          = 'p'
    SuccessLogin   = 'v'
    LeaveRoom      = 'e'
    FailLogin      = 'g'

class MsgCommands:
    LeaveRoom   = 'leaveroom'

# Define constants for the message format and communication parameters
Format = 'utf-8'  # Encoding format for data conversion
BufferSize = 1024  # Size of the buffer for reading data
Header = bytes([0x01])  # Start of message marker
Footer = bytes([0x03])  # End of message marker

def read_config(filename='config.txt'):
    """
    Reads host and port configuration from a file.

    Args: filename (str): Name of the configuration file.

    Returns: tuple: A tuple containing host (str) and port (int).
    """
    with open(filename, 'r') as f:
        lines = f.readlines()
        host = lines[0].strip()  # Read host from the first line of the file
        port = int(lines[1].strip())  # Read port from the second line of the file
    return host, port

def serialize(msg_type, data):
    """
    Serializes data for transmission.

    Args: data (str): Data to be serialized.

    Returns: bytes: Serialized data ready for transmission.
    """
    data = msg_type + data

    # Convert data from string to bytes using ASCII encoding
    data_bytes = data.encode('ascii')

    # Calculate checksum by summing up the ASCII values and masking with 0xFF
    checksum = sum(data_bytes) & 0xFF

    # Construct the formatted buffer with header, data, checksum, and footer
    formatted_buffer = Header + data_bytes + bytes([checksum]) + Footer
    return formatted_buffer

def process_buffer(buffer):
    """
    Processes the received buffer and extracts messages.

    Args: buffer (bytes): Received data buffer.

    Returns: str or None: Extracted message if valid, None otherwise.
    """

    # Trying to find header and footer
    while (Header in buffer) and (Footer in buffer):
        # Find the start and end indices of the message within the buffer
        start_index = buffer.index(Header)
        end_index = buffer.index(Footer) + len(Footer)

        # Extract the message content between the header and footer
        message = buffer[start_index+1:end_index-2]

        # Extract the checksum byte
        checksum = int.from_bytes(buffer[end_index-2:end_index-1], byteorder='big')

        # Calculate the checksum of the message
        calculated_checksum = sum(message) & 0xFF

        # Verify the checksum
        if calculated_checksum == checksum:
            # Remove the processed part of the buffer
            del buffer[:end_index]
            return message.decode('ascii')  # Decode message to string
        
        print("invalid checksum")
        buffer = buffer[start_index+1:]
        
    return None
