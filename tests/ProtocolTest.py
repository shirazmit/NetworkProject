import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from Protocol import serialize, process_buffer, MsgType, Header, Footer

class TestProtocolFunctions(unittest.TestCase):
    def test_serialize(self):
        # Test serialization with different message types and data
        data = 'Hello'
        buf = bytearray(Header.decode('ascii') + MsgType.RegularMessage + data, 'utf-8')
        buf.append((sum(buf[1:]) & 0xFF))
        buf.append(ord(Footer))
        result = serialize(MsgType.RegularMessage, data)
        self.assertEqual(result, buf)

    def test_two_merged_msgs(self):
        # Test serialization with different message types and data
        data1 = 'Hello'
        buf1 = bytearray(Header.decode('ascii') + MsgType.RegularMessage + data1, 'utf-8')
        buf1.append((sum(buf1[1:]) & 0xFF))
        buf1.append(ord(Footer))

        data2 = 'World'
        buf2 = bytearray(Header.decode('ascii') + MsgType.RegularMessage + data2, 'utf-8')
        buf2.append((sum(buf2[1:]) & 0xFF))
        buf2.append(ord(Footer))

        buf1.extend(buf2)

        res1 = process_buffer(buf1)
        res2 = process_buffer(buf1)
        self.assertEqual(res1, MsgType.RegularMessage + data1)
        self.assertEqual(res2, MsgType.RegularMessage + data2)

    def test_two_merged_msgs_with_noise(self):
        # Test serialization with different message types and data
        data1 = 'Hello'
        buf1 = bytearray(Header.decode('ascii') + MsgType.RegularMessage + data1, 'utf-8')
        buf1.append((sum(buf1[1:]) & 0xFF))
        buf1.append(ord(Footer))

        data2 = 'World'
        buf2 = bytearray(Header.decode('ascii') + MsgType.RegularMessage + data2, 'utf-8')
        buf2.append((sum(buf2[1:]) & 0xFF))
        buf2.append(ord(Footer))

        # Adding noise between every message
        buf1 = bytearray(b'Noise' + buf1)
        buf1.extend(b'JustNoise')
        buf1.extend(buf2)
        buf1.extend(b'RandomNoise')

        res1 = process_buffer(buf1)
        res2 = process_buffer(buf1)
        res3 = process_buffer(buf1)
        res4 = process_buffer(buf1)
        self.assertEqual(res1, MsgType.RegularMessage + data1)
        self.assertEqual(res2, MsgType.RegularMessage + data2)
        self.assertEqual(res3, None)
        self.assertEqual(res4, None)


if __name__ == '__main__':
    unittest.main()
