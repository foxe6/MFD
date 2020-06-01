import requests
import threading
import threadwrapper
from omnitools import args, md5hd, crc32hd, sha1hd, p
from filehandling import join_path
import time
import queue


class MFD(object):

    def __init__(self, save_dir: str, piece_size: int = 1024*1024*(2**4), retry: int = 5) -> None:
        self.save_dir = save_dir
        self.piece_size = piece_size
        self.retry = retry
        self.terminate = False
        self.filename = ""
        self.__header = {"Range": "bytes={}-{}"}
        self.parts = queue.Queue()
        self.file_size = 0
        self.parts_track = {}
        process = threading.Thread(target=self.combiner)
        process.daemon = True
        process.start()

    def combiner(self):
        while not self.terminate:
            k, v = self.parts.get()
            try:
                if v is not None:
                    with open(join_path(self.save_dir, self.filename), 'r+b') as f:
                        f.seek(k * self.piece_size, 0)
                        f.write(v)
                        f.close()
                    self.parts_track.pop(k)
                self.parts.task_done()
            except Exception as e:
                print(e, k, len(v), v[:16], v[-16:], flush=True)

    def stop(self):
        self.terminate = True

    def __get_file_size(self, url: str) -> int:
        try:
            header = self.__header.copy()
            header["Range"] = header["Range"].format(0, 1)
            header = requests.get(url, headers=header).headers
            file_size = int(header["Content-Range"].split("/")[-1])
            if "Content-disposition" in header:
                self.filename = header["Content-disposition"].split("filename=")[-1][1:-1]
            else:
                filename = url.split("/")[-1]
                # if "." not in filename:
                #     filename = "download_"+str(int(time.time()))
                self.filename = filename
            return file_size
        except:
            raise Exception("server does not support multi-threaded file downloading")

    def __create_empty_file(self):
        with open(join_path(self.save_dir, self.filename), "wb") as f:
            f.seek(self.file_size-1)
            f.write(b"\0")
            f.close()

    def download(self, url: str, connections: int = 2**3, cal_hash: bool = False):
        self.file_size = self.__get_file_size(url)
        self.__create_empty_file()
        tw = threadwrapper.ThreadWrapper(threading.Semaphore(connections))
        p(f"[MFD] Downloading {url} with {connections} connections", end="")
        for i in range(0, self.file_size // self.piece_size + 1):
            def job(i):
                header = self.__header.copy()
                end = (i+1) * self.piece_size - 1
                if i == self.file_size//self.piece_size+1:
                    end = self.file_size
                header["Range"] = header["Range"].format(i * self.piece_size, end)
                for j in range(0, self.retry):
                    try:
                        content = requests.get(url, headers=header).content
                        self.parts.put((i, content))
                        return
                    except:
                        time.sleep(1)
                raise Exception(f"failed to download {url} range "+header["Range"])

            self.parts_track[i] = 0
            tw.add(job, args(i))
        tw.wait()
        while len(self.parts_track) > 0:
            time.sleep(1/10)
        _f = join_path(self.save_dir, self.filename)
        p(f"\r[MFD] Downloaded {url} => "+_f)
        if cal_hash:
            fd = open(_f, "rb")
            # return {"md5": md5hd(fd), "crc32": crc32hd(fd), "sha1": sha1hd(fd), "file_path": _f}
            return {"sha1": sha1hd(fd), "file_path": _f}
        else:
            return {"file_path": _f}

