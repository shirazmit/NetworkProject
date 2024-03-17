class MsgType:
    ListRooms      = 'l'
    JoinRoom       = 'r'
    RegularMessage = 'm'
    SetUsername    = 'n'
    InvalidRoom    = 'f'
    RefuseBan      = 'b'
    Notification   = 'j'

def read_config(filename='config.txt'):
    with open(filename, 'r') as f:
        lines = f.readlines()
        host = lines[0].strip()
        port = int(lines[1].strip())
    return host, port

Format = 'utf-8'
BufferSize = 1024