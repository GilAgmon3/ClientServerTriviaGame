from time import sleep

import ClientMain1, ClientMain2, ServerMain

if __name__ == '__main__':
    ServerMain.run()
    sleep(1)
    ClientMain1.run()
    ClientMain2.run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
