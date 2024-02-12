import pandas as pd
import sys

# sorting
def sort_panda_process(frame: pd.DataFrame):
    work_frame = frame.copy()
    work_frame = work_frame.transpose()
    work_frame.sort_values(by = ['priority_value', 'phase_duration'], ascending=[False, True], inplace=True)
    return work_frame.transpose()

# mean
def avg(data: list):
    mean = 0
    for i in data:
        mean += i
    return mean / len(data)

class SJF:
    def __init__(self, file_name: str, if_cmd: bool):
        # reading the data and building data frame
        names = ['arrival_time', 'phase_duration', 'priority_value', 'how long waiting']
        data = {}
        with open(file_name, 'r') as file:
            for i in range(len(names)-1):
                data[names[i]] = file.readline().strip().split()
            self.__time_quantum_prior = int(file.readline().strip())
            self.__time_quantum_RR = file.readline().strip().split()
        pid = []
        waiting = []

        # making PID
        for i in range(len(data['arrival_time'])):
            pid.append(i + 1)
            waiting.append(0)
        data['PID'] = pid
        data['how long waiting'] = waiting

        self.__operational = pd.DataFrame(data)
        self.__operational.set_index('PID', inplace=True)
        self.__operational = self.__operational.transpose()
        for i in self.__operational.columns:
            self.__operational[i] = self.__operational[i].astype('int32')

        # data to raport
        self.__waiting_time = []
        self.__average_waiting_time = 0
        self.__num_of_processess = 0
        self.__if_cmd = if_cmd

    # is adding new process
    def __add_new_process(self, df: pd.DataFrame, ar_time: int, pid):
        next_arrival_time_local = ar_time
        next_phase_duration = int(input('give phase duration: '))
        next_priority_value = int(input('give priority value: '))
        how_long_wait = 0
        df[pid] = [next_arrival_time_local, next_phase_duration, next_priority_value, how_long_wait]

    def execute(self):
        # reading for 0. round
        actual_round = 0
        counter = 0
        operational_data = self.__operational.transpose().query('arrival_time == ' + str(actual_round)).copy()
        operational_data = operational_data.transpose()
        operational_data = sort_panda_process(operational_data)
        # actual algorithm
        while (len(list(operational_data.columns))) > 0:
            # printing actual round
            print('\nRound nr.', actual_round)
            print(operational_data)
            actual_round += 1
            # decreasing phase duration of actual algorithm
            operational_data.loc['phase_duration', list(operational_data.columns)[0]] -= 1
            # preparing to not expropriate
            kept_column_id = list(operational_data.columns)[0]
            kept_column = operational_data[kept_column_id]
            del operational_data[list(operational_data.columns)[0]]
            # increasing how long waiting and prioritare
            operational_data = operational_data.transpose()
            operational_data['how long waiting'] += 1
            if counter % self.__time_quantum_prior == 0:
                operational_data['priority_value'] += 1
            operational_data = operational_data.transpose()
            operational_data = sort_panda_process(operational_data)
            operational_data.insert(0, kept_column_id, kept_column)
            counter += 1
            #deleting if process is finished
            if operational_data.loc['phase_duration', list(operational_data.columns)[0]] == 0:
                self.__waiting_time.append(operational_data.loc['how long waiting', list(operational_data.columns)[0]])
                self.__num_of_processess += 1
                del operational_data[list(operational_data.columns)[0]]
                if len(list(operational_data.columns)) == 0:
                    break

            # adding new processes from file
            add_from_file = self.__operational.transpose().query('arrival_time ==' + str(actual_round))
            if len(add_from_file.values) > 0:
                operational_data = operational_data.transpose()
                operational_data = pd.concat([operational_data, self.__operational.transpose().query('arrival_time ==' + str(actual_round))])
                operational_data = operational_data.transpose()
            # adding new process from user (only if it is to print in cmd/powershell)
            if self.__if_cmd:
                answer = input('Do You wanna add new process? y/n: ')
                if 'Y' in answer.upper():
                    pid = max(list(self.__operational.columns) + list(operational_data.columns)) + 1
                    self.__add_new_process(operational_data, actual_round, pid)

    def preparing_to_raport(self):
        raport = pd.DataFrame()
        print('*' * 15, "SUMMARY", '*' * 15)
        index = ['average waiting time', 'number of processes']
        values = [avg(self.__waiting_time), self.__num_of_processess]
        raport['checked'] = index
        raport['values'] = values
        raport.set_index('checked', inplace = True)
        print(raport)

# generating raport
def in_txt():
    file_name = input('please, enter the file name:')
    print('*'*10, "MAIN MENU", '*'*10)
    print('1. Generate .txt raport\n2. Run simulation in console')
    which = input("(1/2): ")
    if which == '1':
        with open('raport.txt', 'w') as file:
            # all what in console goes to the file
            sys.stdout = file
            to_test = SJF(file_name, False)
            to_test.execute()
            to_test.preparing_to_raport()
    elif which == '2':
        to_test = SJF(file_name, True)
        to_test.execute()
        to_test.preparing_to_raport()

in_txt()

