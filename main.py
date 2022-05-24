from my_classes import Simulator, Recorder
import time


recoder = Recorder(file_index=1)
simulator = Simulator(recoder)

start = time.time()

for i in range(1):
    print(i, '번째 시행')
    simulator.simulate(n_preys=10, total_time=30, ff=1)

end = time.time()
print(end - start, '초 소요')
