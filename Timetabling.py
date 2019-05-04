import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from functools import reduce


class Timetable:

    meetings = None
    G = None

    def __init__(self):
        self.G = nx.Graph()
        self.meetings = {}

    def addMettingParticipants(self, meetingname, participants):
        if self.meetings.get(meetingname) is None:
            self.meetings[meetingname] = participants
        else:
            self.meetings[meetingname].extend(participants)

    def schedule(self):

        meetingMatrix = []
        for newmeeting, newparticipants in self.meetings.items():
            self.G.add_node(len(meetingMatrix), label=newmeeting)
            for meeting in range(len(meetingMatrix)):
                intersection = np.intersect1d(newparticipants, meetingMatrix[meeting])
                if len(intersection)>0:
                    self.G.add_edge(meeting, len(meetingMatrix), label=str(intersection))
            meetingMatrix.append(newparticipants)

        pos = nx.spring_layout(self.G)
        nx.draw_networkx(self.G, pos, labels=nx.get_node_attributes(self.G, 'label'), with_labels=True)
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=nx.get_edge_attributes(self.G, "label"), font_size=6, rotate=False, label_pos=0.3)

       #nx.draw_networkx_edge_labels(self.G, pos)
        d = nx.coloring.greedy_color(self.G, strategy=nx.coloring.strategy_largest_first)
        # print(d)
        # d = nx.coloring.greedy_color(self.G, strategy=nx.coloring.strategy_saturation_largest_first)
        # print(d)
        plt.show()
        plt.savefig("./schedule.png")





if __name__ == '__main__':

    edmund = "Edmund"
    graham = "Graham"
    kath = "Kath"
    sanja = "Sanja"

    timetable = Timetable()
    timetable.addMettingParticipants("1", [edmund, graham, sanja])
    timetable.addMettingParticipants("2", [graham])
    timetable.addMettingParticipants("3", [graham, kath, sanja])
    timetable.addMettingParticipants("4", [edmund, sanja])
    timetable.addMettingParticipants("5", [edmund, kath, sanja])
    timetable.addMettingParticipants("6", [kath])
    timetable.addMettingParticipants("7", [edmund])

    timetable.schedule()
