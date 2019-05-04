import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors as mcolors
from enum import Enum

class Heuristic(Enum):
    LARGEST_DEGREE_FIRST=0
    SATURATION_DEGREE=1

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
        colors = list(dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS).values())
        colors = colors[8:]

        for newmeeting, newparticipants in self.meetings.items():
            self.G.add_node(len(meetingMatrix), label=newmeeting, color='red')
            for meeting in range(len(meetingMatrix)):
                intersection = np.intersect1d(newparticipants, meetingMatrix[meeting])
                if len(intersection)>0:
                    self.G.add_edge(meeting, len(meetingMatrix), label=str(intersection))
            meetingMatrix.append(newparticipants)

        graph_colors = self.color_graph(self.G, colors, Heuristic.LARGEST_DEGREE_FIRST)


        pos = nx.spring_layout(self.G)
        nx.draw_networkx(self.G, pos, labels=nx.get_node_attributes(self.G, 'label'), with_labels=True, node_color=graph_colors)
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=nx.get_edge_attributes(self.G, "label"), font_size=6, rotate=False, label_pos=0.3)

        plt.title("Largest Degree First")
        plt.savefig('largest_degree_first.png', bbox_inches='tight')
        plt.figure()

        plt.title("Saturation Degree")
        graph_colors = self.color_graph(self.G, colors, Heuristic.SATURATION_DEGREE)
        nx.draw_networkx(self.G, pos, labels=nx.get_node_attributes(self.G, 'label'), with_labels=True, node_color=graph_colors)
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=nx.get_edge_attributes(self.G, "label"), font_size=6,
                                     rotate=False, label_pos=0.3)

        plt.savefig('saturation_degree.png', bbox_inches='tight')
        plt.show()

    def color_graph(self, G, colors, heuristic):

        strategy = nx.coloring.strategy_largest_first

        if heuristic == Heuristic.SATURATION_DEGREE:
            strategy = nx.coloring.strategy_saturation_largest_first
        nodecolors = []
        d = nx.coloring.greedy_color(self.G, strategy=strategy)
        for node in range(len(d)):
            nodecolors.append(colors[d[node]])

        return nodecolors


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
