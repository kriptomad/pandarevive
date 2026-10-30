import unittest
from unittest import mock

from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.pandad import pandad


class TestFlashPanda(OpenpilotTestCase):
  def setUp(self):
    super().setUp()
    self.panda = mock.MagicMock()
    self.panda.__enter__.return_value = self.panda
    self.dfu = mock.MagicMock()
    self.dfu.__enter__.return_value = self.dfu
    self.hardware = mock.MagicMock()

    patches = [
      mock.patch.object(pandad, "Panda"),
      mock.patch.object(pandad, "PandaDFU"),
      mock.patch.object(pandad, "HARDWARE", self.hardware),
    ]
    self.Panda, self.PandaDFU, _ = [p.start() for p in patches]
    for p in patches:
      self.addCleanup(p.stop)

    self.Panda.return_value = self.panda
    self.Panda.wait_for_dfu.return_value = True
    self.Panda.wait_for_panda.return_value = True
    self.PandaDFU.return_value = self.dfu
    self.PandaDFU.list.return_value = []

  def test_external_panda_from_app(self):
    self.panda.bootstub = False
    with mock.patch.object(pandad, "COMMA_HARDWARE", False):
      pandad.flash_panda()
    self.hardware.recover_internal_panda.assert_not_called()
    assert self.panda.reset.call_args_list == [mock.call(enter_bootstub=True), mock.call(enter_bootloader=True)]
    self.dfu.recover.assert_called_once()
    self.panda.flash.assert_called_once()

  def test_external_panda_from_bootstub(self):
    self.panda.bootstub = True
    with mock.patch.object(pandad, "COMMA_HARDWARE", False):
      pandad.flash_panda()
    assert self.panda.reset.call_args_list == [mock.call(enter_bootloader=True)]
    self.dfu.recover.assert_called_once()

  def test_external_panda_already_in_dfu(self):
    self.PandaDFU.list.return_value = ["dfu-serial"]
    with mock.patch.object(pandad, "COMMA_HARDWARE", False):
      pandad.flash_panda()
    self.panda.reset.assert_not_called()
    self.dfu.recover.assert_called_once()
    self.panda.flash.assert_called_once()

  def test_internal_panda_uses_reset_lines(self):
    with mock.patch.object(pandad, "COMMA_HARDWARE", True):
      pandad.flash_panda()
    self.hardware.recover_internal_panda.assert_called_once()
    self.panda.reset.assert_not_called()
    self.dfu.recover.assert_called_once()


if __name__ == "__main__":
  unittest.main()
