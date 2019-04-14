from multiprocessing import Process, Manager, Pool

from generator import QRGenerator
from sender import Sender

if __name__ == '__main__':
    m = Manager()
    q = m.Queue()
    gen = QRGenerator(q)
    sender = Sender(q)

    def process(code):
        gen.generate(code)

    sender_process = Process(target=sender.send)
    sender_process.start()

    with Pool() as pool:
        res = pool.map_async(process, range(10))
        res.wait()
        q.put(Sender.Stop())

    sender_process.join()
