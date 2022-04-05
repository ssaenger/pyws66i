import unittest
from unittest import TestCase, mock
import re
import socket

from pyws66i import get_ws66i, ZoneStatus, TIMEOUT


class TestZoneStatus(TestCase):
    def test_zone_status_broken(self):
        self.assertIsNone(ZoneStatus.from_string(None))


class TestWs66i(TestCase):
    def setUp(self):
        self.patcher = mock.patch('pyws66i.Telnet')
        self.mock_telnet = self.patcher.start()
        self.telnet_instance = self.mock_telnet.return_value
        self.ws66i = get_ws66i("168.192.1.123")
        self.ws66i.open()
        self.telnet_instance.open.assert_called_once()


    def tearDown(self):
        self.ws66i.close()
        self.patcher.stop()


    def test_close(self):
        # ----------- test close is called-----------
        # call
        self.ws66i.close()
        self.telnet_instance.close.assert_called_once()


    def test_bad_open(self):
        # ----------- test expect raises TimeoutError -----------
        # call
        self.telnet_instance.open.side_effect = TimeoutError()
        self.assertRaises(ConnectionError, self.ws66i.open)

        # ----------- test expect raises OSError -----------
        # call
        self.telnet_instance.open.side_effect = OSError()
        self.assertRaises(ConnectionError, self.ws66i.open)

        # ----------- test expect raises socket.timeout -----------
        # call
        self.telnet_instance.open.side_effect = socket.timeout()
        self.assertRaises(ConnectionError, self.ws66i.open)

        # ----------- test expect raises socket.gaierror -----------
        # call
        self.telnet_instance.open.side_effect = socket.gaierror()
        self.assertRaises(ConnectionError, self.ws66i.open)


    def test_zone_status(self):
        # ----------- Test good format -----------
        # setup
        zone = 11
        expected_write = f'?{zone}\r'.encode()
        expected_string_coded = "1100010000131112100401".encode()
        expected_pattern_coded = f"({zone})(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)".encode()

        # call
        self.telnet_instance.expect.return_value = [None, re.search(expected_pattern_coded, expected_string_coded), None]
        status = self.ws66i.zone_status(zone)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)
        self.telnet_instance.expect.assert_called_with([expected_pattern_coded], timeout=TIMEOUT)
        self.assertEqual(zone, status.zone)
        self.assertFalse(status.pa)
        self.assertTrue(status.power)
        self.assertFalse(status.mute)
        self.assertFalse(status.do_not_disturb)
        self.assertEqual(13, status.volume)
        self.assertEqual(11, status.treble)
        self.assertEqual(12, status.bass)
        self.assertEqual(10, status.balance)
        self.assertEqual(4, status.source)
        self.assertTrue(status.keypad)


        # ----------- test expect raises EOFError -----------
        # Clear Mock
        self.telnet_instance.reset_mock()

        # setup
        zone = 11
        expected_write = f'?{zone}\r'.encode()
        expected_pattern_coded = f"({zone})(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)".encode()

        # call
        self.telnet_instance.expect.side_effect = EOFError()
        status = self.ws66i.zone_status(zone)

        # check
        self.telnet_instance.get_socket.assert_called()
        self.telnet_instance.write.assert_called()
        self.telnet_instance.expect.assert_called_with([expected_pattern_coded], timeout=TIMEOUT)
        self.telnet_instance.close.assert_called_once()
        self.assertIsNone(status)

        # ----------- test fails open -----------
        # Clear Mock
        self.telnet_instance.reset_mock()

        # call
        self.telnet_instance.get_socket.return_value = None
        self.telnet_instance.open.side_effect = TimeoutError()
        status = self.ws66i.zone_status(zone)

        # check
        self.telnet_instance.get_socket.assert_called()
        self.telnet_instance.open.assert_called_once()
        self.telnet_instance.write.assert_not_called()
        self.telnet_instance.expect.assert_not_called()
        self.telnet_instance.close.assert_not_called()
        self.assertIsNone(status)

        # ----------- test expect raises TimeoutError -----------
        # Clear Mock
        self.telnet_instance.reset_mock()

        # call
        self.telnet_instance.open.side_effect = None
        self.telnet_instance.get_socket.return_value = None
        self.telnet_instance.expect.side_effect = TimeoutError()
        status = self.ws66i.zone_status(zone)

        # check
        self.telnet_instance.get_socket.assert_called()
        self.telnet_instance.open.assert_called_once()
        self.telnet_instance.write.assert_called_once()
        self.telnet_instance.expect.assert_called_once()
        self.telnet_instance.close.assert_called_once()
        self.assertIsNone(status)

        # ----------- test expect raises socket.timeout -----------
        # Clear Mock
        self.telnet_instance.reset_mock()

        # call
        self.telnet_instance.get_socket.return_value = None
        self.telnet_instance.expect.side_effect = socket.timeout()
        status = self.ws66i.zone_status(zone)

        # check
        self.telnet_instance.get_socket.assert_called()
        self.telnet_instance.open.assert_called_once()
        self.telnet_instance.write.assert_called_once()
        self.telnet_instance.expect.assert_called_once()
        self.telnet_instance.close.assert_called_once()
        self.assertIsNone(status)

        # ----------- test expect raises UnboundLocalError -----------
        # Clear Mock
        self.telnet_instance.reset_mock()

        # call
        self.telnet_instance.get_socket.return_value = None
        self.telnet_instance.expect.side_effect = UnboundLocalError()
        status = self.ws66i.zone_status(zone)

        # check
        self.telnet_instance.get_socket.assert_called()
        self.telnet_instance.open.assert_called_once()
        self.telnet_instance.write.assert_called_once()
        self.telnet_instance.expect.assert_called_once()
        self.assertIsNone(status)

        # ----------- test expect raises BrokenPipeError -----------
        # Clear Mock
        self.telnet_instance.reset_mock()

        # call
        self.telnet_instance.get_socket.return_value = None
        self.telnet_instance.expect.side_effect = BrokenPipeError()
        status = self.ws66i.zone_status(zone)

        # check
        self.telnet_instance.get_socket.assert_called()
        self.telnet_instance.open.assert_called_once()
        self.telnet_instance.write.assert_called_once()
        self.telnet_instance.expect.assert_called_once()
        self.assertIsNone(status)

        # ----------- test connection re-established, success -----------
        # call
        # This is a way to check if a method was called or not...
        self.telnet_instance.reset_mock()

        # setup
        zone = 11
        expected_write = f'?{zone}\r'.encode()
        expected_string_coded = "1100010000131112100401".encode()
        expected_pattern_coded = f"({zone})(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)".encode()

        # call
        self.telnet_instance.expect.side_effect = None
        self.telnet_instance.expect.return_value = [None, re.search(expected_pattern_coded, expected_string_coded), None]
        status = self.ws66i.zone_status(zone)

        # check
        self.telnet_instance.get_socket.assert_called_once()
        self.telnet_instance.open.assert_called_once()
        self.telnet_instance.write.assert_called_once()
        self.telnet_instance.expect.assert_called_once()
        self.telnet_instance.close.assert_not_called()

        # check
        self.assertIsNotNone(status)

        # ----------- test zone_status with closed connection -----------
        # Clear Mock
        self.telnet_instance.reset_mock()

        # setup
        # A way to check that "write" is not called
        prev_write_count = self.telnet_instance.write.call_count

        # call
        self.ws66i.close()
        status = self.ws66i.zone_status(zone)

        # check
        self.telnet_instance.close.assert_called_once()
        self.telnet_instance.get_socket.assert_not_called()
        self.telnet_instance.open.assert_not_called()
        self.assertEqual(prev_write_count, self.telnet_instance.write.call_count)
        self.telnet_instance.expect.assert_not_called()
        self.assertIsNone(status)


    def test_set_power(self):
        # ----------- test 2nd arg is True -----------
        # setup
        zone = 12
        expected_write = f'<{zone}PR01\r'.encode()

        # call
        self.ws66i.set_power(zone, True)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test 2nd arg is "True" -----------
        # call
        self.ws66i.set_power(zone, "True")

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test 2nd arg is 1 -----------
        # call
        self.ws66i.set_power(zone, 1)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test 2nd arg is False -----------
        # setup
        expected_write = f'<{zone}PR00\r'.encode()

        # call
        self.ws66i.set_power(zone, False)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test 2nd arg is None -----------
        # call
        self.ws66i.set_power(zone, None)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test 2nd arg is 0 -----------
        # call
        self.ws66i.set_power(zone, 0)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test 2nd arg is "" -----------
        # call
        self.ws66i.set_power(zone, "")

        # check
        self.telnet_instance.write.assert_called_with(expected_write)


    def test_set_mute(self):
        # ----------- test 2nd arg is True -----------
        # setup
        zone = 13
        expected_write = f'<{zone}MU01\r'.encode()

        # call
        self.ws66i.set_mute(zone, True)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test 2nd arg is "True" -----------
        # call
        self.ws66i.set_mute(zone, "True")

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test 2nd arg is 1 -----------
        # call
        self.ws66i.set_mute(zone, 1)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test 2nd arg is False -----------
        # setup
        expected_write = f'<{zone}MU00\r'.encode()

        # call
        self.ws66i.set_mute(zone, False)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test 2nd arg is None -----------
        # call
        self.ws66i.set_mute(zone, None)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test 2nd arg is 0 -----------
        # call
        self.ws66i.set_mute(zone, 0)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test 2nd arg is "" -----------
        # call
        self.ws66i.set_mute(zone, "")

        # check
        self.telnet_instance.write.assert_called_with(expected_write)


    def test_set_volume(self):
        # ----------- test vol 1 -----------
        # setup
        zone = 14
        expected_write = f'<{zone}VO01\r'.encode()

        # call
        self.ws66i.set_volume(zone, 1)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test above 38 -----------
        # setup
        expected_write = f'<{zone}VO38\r'.encode()

        # call
        self.ws66i.set_volume(zone, 100)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test vol below 0 -----------
        # setup
        expected_write = f'<{zone}VO00\r'.encode()

        # call
        self.ws66i.set_volume(zone, -10)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test vol 22 -----------
        # setup
        expected_write = f'<{zone}VO22\r'.encode()

        # call
        self.ws66i.set_volume(zone, 22)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

    def test_set_treble(self):
        # ----------- test treble 1 -----------
        # setup
        zone = 15
        expected_write = f'<{zone}TR01\r'.encode()

        # call
        self.ws66i.set_treble(zone, 1)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test treble above 14 -----------
        # setup
        expected_write = f'<{zone}TR14\r'.encode()

        # call
        self.ws66i.set_treble(zone, 100)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test treble below 0 -----------
        # setup
        expected_write = f'<{zone}TR00\r'.encode()

        # call
        self.ws66i.set_treble(zone, -10)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test treble 5 -----------
        # setup
        expected_write = f'<{zone}TR05\r'.encode()

        # call
        self.ws66i.set_treble(zone, 5)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)


    def test_set_bass(self):
        # ----------- test bass 1 -----------
        # setup
        zone = 15
        expected_write = f'<{zone}BS01\r'.encode()

        # call
        self.ws66i.set_bass(zone, 1)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test bass above 14 -----------
        # setup
        expected_write = f'<{zone}BS14\r'.encode()

        # call
        self.ws66i.set_bass(zone, 100)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test bass below 0 -----------
        # setup
        expected_write = f'<{zone}BS00\r'.encode()

        # call
        self.ws66i.set_bass(zone, -10)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test bass 11 -----------
        # setup
        expected_write = f'<{zone}BS05\r'.encode()

        # call
        self.ws66i.set_bass(zone, 5)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)


    def test_set_balance(self):
        # ----------- test balance 1 -----------
        # setup
        zone = 15
        expected_write = f'<{zone}BL01\r'.encode()

        # call
        self.ws66i.set_balance(zone, 1)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test balance above 20 -----------
        # setup
        expected_write = f'<{zone}BL20\r'.encode()

        # call
        self.ws66i.set_balance(zone, 100)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test balance below 0 -----------
        # setup
        expected_write = f'<{zone}BL00\r'.encode()

        # call
        self.ws66i.set_balance(zone, -10)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test balance 16 -----------
        # setup
        expected_write = f'<{zone}BL16\r'.encode()

        # call
        self.ws66i.set_balance(zone, 16)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)


    def test_set_source(self):
        # ----------- test source 1 -----------
        # setup
        zone = 16
        expected_write = f'<{zone}CH01\r'.encode()

        # call
        self.ws66i.set_source(zone, 1)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test source above 6 -----------
        # setup
        expected_write = f'<{zone}CH06\r'.encode()

        # call
        self.ws66i.set_source(zone, 100)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test source below 0 -----------
        # setup
        expected_write = f'<{zone}CH01\r'.encode()

        # call
        self.ws66i.set_source(zone, -10)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)

        # ----------- test source 6 -----------
        # setup
        expected_write = f'<{zone}CH06\r'.encode()

        # call
        self.ws66i.set_source(zone, 16)

        # check
        self.telnet_instance.write.assert_called_with(expected_write)


    def test_restore_zone(self):
        # setup
        expected_zone = 11
        expected_string_coded = "1100010000131112100401".encode()
        expected_pattern_coded = f"({expected_zone})(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)".encode()
        ew_pr = f'<{expected_zone}PR01\r'.encode()
        ew_mu = f'<{expected_zone}MU00\r'.encode()
        ew_vo = f'<{expected_zone}VO13\r'.encode()
        ew_tr = f'<{expected_zone}TR11\r'.encode()
        ew_bs = f'<{expected_zone}BS12\r'.encode()
        ew_bl = f'<{expected_zone}BL10\r'.encode()
        ew_ch = f'<{expected_zone}CH04\r'.encode()
        expected_list = [mock.call(ew_pr), mock.call(ew_mu), mock.call(ew_vo), mock.call(ew_tr), mock.call(ew_bs), mock.call(ew_bl), mock.call(ew_ch)]

        # call and check
        zone_status = ZoneStatus.from_string(re.search(expected_pattern_coded, expected_string_coded))
        self.ws66i.restore_zone(zone_status)
        self.assertTrue(self.telnet_instance.write.call_args_list == expected_list)


if __name__ == "__main__":
    unittest.main()
