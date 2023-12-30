from threading import Thread, local
from time import sleep


class TranslationLocal(local):
    lang = 'en'


class Translation:
    local = TranslationLocal()


def thread1(threadname):
    for x in range(10):
        print('### thread1', Translation.local.lang)
        sleep(1)


def thread2(threadname):
    for x in range(10):
        Translation.local.lang = 'fr'
        print('==> thread2', Translation.local.lang)
        sleep(1)


thread1 = Thread(target=thread1, args=("Thread-1",))
thread2 = Thread(target=thread2, args=("Thread-2",))

thread1.start()
thread2.start()
thread1.join()
thread2.join()
