import requests
import threading
import threadwrapper
from omnitools import def_template, md5hd, crc32hd, sha1hd, p
from filehandling import join_path
import time
import queue


__ALL__ = ["MFD"]


class MFD(object):
    def __init__(self, save_dir: str, piece_size: int = 1024*1024*(2**4), retry: int = 5) -> None:
        self.save_dir = save_dir
        self.piece_size = piece_size
        self.retry = retry
        self.terminate = False
        self.filename = ""
        self.url = ""
        self.__header = {"Range": "bytes={}-{}"}
        self.parts = queue.Queue()
        self.file_size = 0
        self.pending_write_parts = []
        self.failed_parts = []
        process = threading.Thread(target=self.combiner)
        process.daemon = True
        process.start()

    def combiner(self) -> None:
        while not self.terminate:
            k, v = self.parts.get()
            try:
                if v is not None:
                    with open(join_path(self.save_dir, self.filename), 'r+b') as f:
                        f.seek(k * self.piece_size, 0)
                        f.write(v)
                        f.close()
                    self.pending_write_parts.remove(k)
                    self.failed_parts.remove(k)
                self.parts.task_done()
            except Exception as e:
                print(e, k, len(v), v[:16], v[-16:], flush=True)

    def stop(self) -> None:
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

    def __create_empty_file(self) -> None:
        with open(join_path(self.save_dir, self.filename), "wb") as f:
            f.seek(self.file_size-1)
            f.write(b"\0")
            f.close()

    def __download(self, i: int) -> None:
        header = self.__header.copy()
        end = (i+1) * self.piece_size - 1
        if i == self.file_size//self.piece_size+1:
            end = self.file_size
        header["Range"] = header["Range"].format(i * self.piece_size, end)
        try:
            content = requests.get(self.url, headers=header).content
            self.parts.put((i, content))
        except:
            p(f"failed to download {self.url} range "+header["Range"])

    def retry_download(self, connections: int = 2**3):
        tw = threadwrapper.ThreadWrapper(threading.Semaphore(connections))
        for i in self.failed_parts:
            self.pending_write_parts.append(i)
            tw.add(def_template(self.__download, i))
        tw.wait()
        while len(self.pending_write_parts) > 0:
            time.sleep(1/10)

    def download(self, url: str, connections: int = 2**3, cal_hash: bool = False,
                 quiet: bool = False) -> dict:
        self.url = url
        self.file_size = self.__get_file_size(url)
        self.__create_empty_file()
        if not quiet:
            p(f"[MFD] Downloading {url} with {connections} connections", end="")
        for i in range(0, self.file_size // self.piece_size + 1):
            self.failed_parts.append(i)
        self.retry_download(connections)
        retry_ct = 0
        while len(self.failed_parts) > 0:
            if retry_ct >= self.retry:
                raise Exception(f"failed to download {self.url} after {self.retry} retries")
            self.retry_download(connections)
            retry_ct += 1
        _f = join_path(self.save_dir, self.filename)
        if not quiet:
            p(f"\r[MFD] Downloaded {url} => "+_f)
        if cal_hash:
            fd = open(_f, "rb")
            # return {"md5": md5hd(fd), "crc32": crc32hd(fd), "sha1": sha1hd(fd), "file_path": _f}
            return {"sha1": sha1hd(fd), "file_path": _f}
        else:
            return {"file_path": _f}

