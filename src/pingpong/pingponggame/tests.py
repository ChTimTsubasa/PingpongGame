from django.test import TestCase
from pingponggame.models import Pad
# Create your tests here.

class PadTestCase(TestCase):
    message = {}
    def setUp(self):
        self.message['TYPE'] = "GAME"
        self.message['pad_v'] = [0.1, 0.2]
        self.message['pad_p'] = [0.2, 0.3]

    def test_pad_contruct(self):
        pad = Pad(self.message)

        self.assertEqual(pad.position_X, self.message['pad_p'][0])
        self.assertEqual(pad.position_Y, self.message['pad_p'][1])
        self.assertEqual(pad.velocity_X, self.message['pad_v'][0])
        self.assertEqual(pad.velocity_Y, self.message['pad_v'][1])

    def test_pad_toMessage(self):
        pad = Pad(self.message)
        new_m = pad.message()
        self.assertEqual(self.message['pad_v'], new_m['pad_v'])
        self.assertEqual(self.message['pad_p'], new_m['pad_p'])