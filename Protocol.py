class MsgType:
    ListRooms      = 'l'
    JoinRoom       = 'r'
    RegularMessage = 'm'
    SetUsername    = 'n'
    InvalidRoom    = 'f'
    RefuseBan      = 'b'
    Notification   = 'j'
    Login          = 'p'
    SuccessLogin   = 'v'
    SuccessRoom    = 'w'
    FailLogin      = 'g'

Format = 'utf-8'
BufferSize = 1024
Header = bytes([0x01])
Footer = bytes([0x03])

def read_config(filename='config.txt'):
    with open(filename, 'r') as f:
        lines = f.readlines()
        host = lines[0].strip()
        port = int(lines[1].strip())
    return host, port

def serialize(data):
    # Convert data from string to bytes
    data_bytes = data.encode('ascii')

    # Calculate checksum
    checksum = sum(data_bytes) & 0xFF

    # Add header, data, footer, and checksum
    formatted_buffer = Header + data_bytes + bytes([checksum]) + Footer
    return formatted_buffer

def process_buffer(buffer):
    if Header in buffer and Footer in buffer:
        start_index = buffer.index(Header)
        end_index = buffer.index(Footer) + len(Footer)

        # Extract the message content between the header and checksum, footer
        message = buffer[start_index+1:end_index-2]

        # Convert the checksum byte to an integer
        checksum = int.from_bytes(buffer[end_index-2:end_index-1], byteorder='big')

        # Calculate the checksum of the message
        calculated_checksum = sum(message) & 0xFF

        # Verify the checksum
        if calculated_checksum == checksum:
            # Remove the processed part of the buffer
            del buffer[:end_index]
            return message.decode('ascii')  # Decode message to string
        else:
            print("invalid checksum")

    return None

