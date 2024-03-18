import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from Protocol import serialize, process_buffer, MsgType, Header, Footer


class TestProtocolFunctions(unittest.TestCase):
    def test_serialize(self):
        # Test serialization with different message types and data
        data = "Hello".encode('utf-8')
        msg_type = MsgType.RegularMessage
        ascii_sum = bytes([sum(msg_type.encode('ascii') + data) & 0xFF])
        expected_output = Header + msg_type.encode('ascii') + data + ascii_sum + Footer  # Expected serialized output
        self.assertEqual(serialize(msg_type, str(data)), expected_output)

    def test_process_buffer(self):
        # Test processing a buffer with valid message
        buffer = Header + b"mHello\x10" + Footer
        expected_output = "Hello"
        self.assertEqual(process_buffer(buffer), expected_output)

        # Test processing a buffer with invalid checksum
        buffer = Header + b"mHello\x11" + Footer  # Incorrect checksum
        self.assertIsNone(process_buffer(buffer))  # The function should return None

        # Test processing a buffer without header and footer
        buffer = b"mHello"  # Missing header and footer
        self.assertIsNone(process_buffer(buffer))  # The function should return None

if __name__ == '__main__':
    unittest.main()
