import os
import unittest
import tempfile

from desktopmagic.screengrab_win32 import getDisplayRects, saveRectToBmp, getRectAsImage, GrabFailed


class GetDisplayRectsTest(unittest.TestCase):
	"""
	Tests for L{getDisplayRects}
	"""
	def test_getDisplayRectsReturnsList(self):
		"""
		L{getDisplayRects} returns a list of length >= 1 with a tuple containing 4 integers,
		representing the dimensions ??? of each monitor.
		"""
		regions = getDisplayRects()
		##print "Display rects are:", regions
		self.assertIsInstance(regions, list)
		for region in regions:
			self.assertIsInstance(region, tuple)
			for num in region:
				self.assertIsInstance(num, int)


	def disabled_test_getDisplayRectsDoesNotLeak(self):
		"""
		Calling L{getDisplayRects} 100,000 times does not leak memory (you'll have to
		open taskmgr to make sure.)

		Disabled because Ivan manually confirmed that it does not leak.
		"""
		print "Open taskmgr.exe to make sure I'm not leaking memory right now."
		for i in xrange(100000):
			getDisplayRects()



class RectTests(unittest.TestCase):
	def _tryUnlink(self, fname):
		try:
			os.unlink(fname)
		except OSError:
			pass


	def test_workingCase(self):
		import Image

		fname = tempfile.mktemp()
		self.addCleanup(self._tryUnlink, fname)
		saveRectToBmp(fname, rect=(0, 0, 200, 100))
		with open(fname, "rb") as f:
			im = Image.open(f)
			self.assertEqual((200, 100), im.size)


	def test_invalidRect(self):
		fname = tempfile.mktemp()
		self.addCleanup(self._tryUnlink, fname)
		self.assertRaises(GrabFailed, lambda: saveRectToBmp(fname, rect=(100, 100, 99, 99)))
		self.assertRaises(GrabFailed, lambda: saveRectToBmp(fname, rect=(100, 100, 99, 100)))
		self.assertRaises(GrabFailed, lambda: saveRectToBmp(fname, rect=(100, 100, 100, 99)))


	def test_zeroSizeRect(self):
		"""
		A 0x0 rect works, though you get a 1x1 BMP and PNG instead of 0x0 images.
		(Not due to any logic on our part.)
		"""
		import Image

		fname = tempfile.mktemp() + '.bmp'
		fnamePng = tempfile.mktemp() + '.png'
		self.addCleanup(self._tryUnlink, fname)
		self.addCleanup(self._tryUnlink, fnamePng)
		saveRectToBmp(fname, rect=(100, 100, 100, -100))

		with open(fname, "rb") as f:
			im = Image.open(f)
			self.assertEqual((1, 1), im.size)

		im = getRectAsImage(rect=(100, 100, 100, -100))
		self.assertEqual((1, 1), im.size)
		im.save(fnamePng, format='png')

		with open(fnamePng, "rb") as f:
			im = Image.open(f)
			self.assertEqual((1, 1), im.size)


	def test_rectTooBig(self):
		fname = tempfile.mktemp()
		self.addCleanup(self._tryUnlink, fname)
		# Note that 26000x26000 is big enough to fail it on my system
		self.assertRaises(GrabFailed, lambda: saveRectToBmp(fname, rect=(0, 0, 2600000, 2600000)))


# TODO: test this case that throws an exception because coords are too big
#	im_25600 = getRectAsImage((0, 0, 25600, 25600))
#	im_25600.save('screencapture_25600_25600.png', format='png')
