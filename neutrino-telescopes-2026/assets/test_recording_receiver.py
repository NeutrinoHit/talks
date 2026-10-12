"""Local movie-only receiver: origin, type, size and no-overwrite checks."""
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from serve_recordable_viewers import Receiver


class ReceiverTest(unittest.TestCase):
    def call(self,root,path='/recordings/event.mp4',origin='http://127.0.0.1:8812',mime='video/mp4',body=b'movie',size=None):
        state=SimpleNamespace(server=SimpleNamespace(server_address=('127.0.0.1',8812),recordings=root,upload_limit=32,read_chunk=4),
            headers={'Origin':origin,'Content-Type':mime,'Content-Length':str(len(body) if size is None else size)},path=path,rfile=BytesIO(body))
        result=[]; state.answer=lambda status,payload:result.append((status,payload))
        Receiver.do_POST(state)
        return result[0]

    def test_only_local_movie_is_saved_without_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.assertEqual(self.call(root)[0],201)
            self.assertEqual((root/'event.mp4').read_bytes(),b'movie')
            self.assertEqual(self.call(root,body=b'new')[0],409)
            self.assertEqual((root/'event.mp4').read_bytes(),b'movie')

    def test_remote_traversal_wrong_type_oversize_and_partial_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.assertEqual(self.call(root,origin='https://example.org')[0],403)
            self.assertEqual(self.call(root,path='/recordings/../event.mp4')[0],400)
            self.assertEqual(self.call(root,mime='application/json')[0],400)
            self.assertEqual(self.call(root,mime='video/webm')[0],400)
            self.assertEqual(self.call(root,size=33)[0],413)
            self.assertEqual(self.call(root,size=10)[0],400)
            self.assertFalse((root/'event.mp4').exists())


if __name__=='__main__':unittest.main()
