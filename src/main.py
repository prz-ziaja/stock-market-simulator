import time
from CommunicationBox import CommunicationBox
from Kernel import Kernel
from Plot.Plot import Plot
from ModelChecker import ModelChecker


def test():
    initial_set = [(500, 20, 10, 200),
                   (500, 50, 10, 200),
                   (500, 20, 30, 200)]
    for data_set in initial_set:
        nn, np, nt, ni = data_set

        startIndex = 1700;
        time_begin = time.time()
        cb = CommunicationBox(startIndex)

        kernel = Kernel(cb, startIndex, nn, np, nt, ni)

        time_end = time.time()
        Plot.displayPlot(cb)
        filename = 'symulation_data' + str(int(time.time())) + '.csv'
        cb.saveToFile(kernel, filename)
        print(time_end - time_begin)
        ModelChecker.check_model(startIndex, cb, int(kernel.returnParams().split('NUM_OF_ITERATIONS:')[1]),
                                 kernel.returnParams(), filename)


if __name__ == "__main__":
    startIndex = 1700
    time_begin = time.time()
    cb = CommunicationBox(startIndex)

    NUM_NOISY_TRADER = 400
    NUM_PRZEMEK_TRADER = 20
    NUM_TREND_TRADER = 15
    NUM_OF_ITERATIONS = 1000
    kernel = Kernel(cb, startIndex, NUM_NOISY_TRADER, NUM_PRZEMEK_TRADER, NUM_TREND_TRADER, NUM_OF_ITERATIONS)

    time_end = time.time()
    Plot.displayPlot(cb)
    filename = 'symulation_data'+str(int(time.time()))+'.csv'
    cb.saveToFile(kernel,filename)
    print(time_end - time_begin)
    ModelChecker.check_model(startIndex, cb, int(kernel.returnParams().split('NUM_OF_ITERATIONS:')[1]), kernel.returnParams(), filename)


