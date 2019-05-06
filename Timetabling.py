import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors as mcolors
from enum import Enum
import datetime

class Heuristic(Enum):
    LARGEST_DEGREE_FIRST=0
    SATURATION_DEGREE=1

class Timetable:

    meetings = None
    participants = None
    G = None
    fromTime = None
    toTime = None

    def __init__(self):
        self.G = nx.Graph()
        self.meetings = {}
        self.participants=set()

    def addMettingParticipants(self, meetingname, participants):
        if self.meetings.get(meetingname) is None:
            self.meetings[meetingname] = participants
        else:
            self.meetings[meetingname].extend(participants)

    def schedule(self, fromTime, toTime):
        meetingMatrix = []
        self.fromTime = fromTime
        self.toTime = toTime

        for newmeeting, newparticipants in self.meetings.items():
            #create node for each meeting
            self.participants.update(newparticipants)
            self.G.add_node(len(meetingMatrix), label=newmeeting, degree=0, neighbours=[])
            #check if a meeting has common participants for previously added meetings in the matrix, create an edge between nodes, if there are conflicts
            for meeting in range(len(meetingMatrix)):
                intersection = np.intersect1d(newparticipants, meetingMatrix[meeting])
                if len(intersection)>0:
                    #add edge to the graph, keep track of neighbours
                    self.G.add_edge(meeting, len(meetingMatrix), label=str(intersection))
                    self.G.node[meeting]["degree"] += 1
                    self.G.node[meeting]["neighbours"].append(len(meetingMatrix))
                    self.G.node[len(meetingMatrix)]["degree"] += 1
                    self.G.node[len(meetingMatrix)]["neighbours"].append(meeting)

            meetingMatrix.append(newparticipants)

        self.displayAttendance()
        #get a list of colours for the graph using largest degree first heuristic
        graph_colors = self.color_graph(self.G, Heuristic.LARGEST_DEGREE_FIRST)

        #draw a graph, save to a file and display on screen
        pos = nx.spring_layout(self.G)
        nx.draw_networkx(self.G, pos, labels=nx.get_node_attributes(self.G, 'label'), with_labels=True, node_color=graph_colors)
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=nx.get_edge_attributes(self.G, "label"), font_size=6, rotate=False, label_pos=0.3)

        self.displaySchedule(graph_colors, "Timetable (Largest Degree First Heuristic)")
        plt.title("Largest Degree First")
        plt.savefig('largest_degree_first.png', bbox_inches='tight')
        plt.figure()

        # get a list of colours for the graph using saturation degree ordering heuristic
        # draw a graph, save to a file and display on screen
        plt.title("Saturation Degree")
        graph_colors = self.color_graph(self.G, Heuristic.SATURATION_DEGREE)
        self.displaySchedule(graph_colors, "Timetable (Saturation Degree Heuristic)")
        nx.draw_networkx(self.G, pos, labels=nx.get_node_attributes(self.G, 'label'), with_labels=True, node_color=graph_colors)
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=nx.get_edge_attributes(self.G, "label"), font_size=6,
                                     rotate=False, label_pos=0.3)

        plt.savefig('saturation_degree.png', bbox_inches='tight')
        plt.show()

    def color_graph(self, G, heuristic):
        #get a list of colors
        colors = list(dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS).values())
        colors = colors[8:]

        if heuristic == Heuristic.SATURATION_DEGREE:
            return self.saturated_heuristic(G, colors)

        return self.largest_first_heuristic(G, colors)

    def largest_first_heuristic(self, G, colors):
        nodes = G.nodes._nodes
        #initialize node color arrays, each index corresponds to a graph node
        node_colors = [None] * len(nodes)
        #sort nodes by degree desc
        sorted_degrees = sorted(nodes, key=lambda name: nodes[name]['degree'], reverse=True)
        for node in sorted_degrees:
            neighbours = nodes[node]['neighbours']
            for color in colors:
                if node_colors[node] is not None:
                    break
                #check if any of the neighbours use the color, use first one available
                for neighbour in neighbours:
                    if node_colors[neighbour] == color:
                        node_colors[node] = None
                        break
                    node_colors[node] = color

        return node_colors

    def saturated_heuristic(self, G, colors):

        nodes = G.nodes._nodes
        node_colors = [None] * len(nodes)
        already_colored=[]
        distinct_colors = {v: set() for v in G}

        for i in range(len(nodes)):

            #nothing is coloured at the start, so find the node with the largest degree
            if i == 0:
                node = max(nodes, key=lambda name: nodes[name]['degree'])
                #colour the node
                node_colors[node]=colors[0]
                already_colored.append(node)
                #add used color to the neighbours to calculate saturation later
                for v in nodes[node]['neighbours']:
                    distinct_colors[v].add(colors[0])
            else:
                #calculate the saturation for the nodes
                saturation = {v: len(c) for v, c in distinct_colors.items()
                              if v not in already_colored}
                #find a node with the highest saturation, if two nodes have the same saturation choose the one with larger degree
                node = max(saturation, key=lambda v: (saturation[v], nodes[v]['degree']))

                #color the node choosing a color that has not been used by neighbours
                color = None
                for c in colors:
                    if c not in distinct_colors[node]:
                        color=c
                        node_colors[node]=color
                        already_colored.append(node)
                        break
                # add used color to the neighbours to calculate saturation later
                for v in nodes[node]['neighbours']:
                    distinct_colors[v].add(color)

        return node_colors

    # display the attendance list
    def displayAttendance(self):
        print("\t\t", end='')
        for professor in self.participants:
            print("\t\t" + professor, end='')

        for meeting, participants in self.meetings.items():
            print("\nMeeting " + meeting + "\t\t\t", end='')
            for professor in self.participants:
                if professor in participants:
                    print("1\t\t\t", end='')
                else:
                    print("0\t\t\t", end='')

    # display schedule
    def displaySchedule(self, graphcolors, title):
        timeslots = {}
        print("\n\n" + title)
        for i in range(len(graphcolors)):
            if graphcolors[i] in timeslots.keys():
                timeslots[graphcolors[i]].append(i)
            else:
                timeslots[graphcolors[i]]=[i]

        count = 1
        duration = self.toTime - self.fromTime
        timeslot_duration = duration/len(timeslots)
        startTime = self.fromTime


        for timeslot in timeslots.values():
            endTime = startTime+timeslot_duration
            print("\nTime Slot " + str(count) + " (" + startTime.strftime('%Y-%m-%d %H:%M') + " - " + endTime.strftime('%Y-%m-%d %H:%M') + ")\t\t", end='')

            for meeting in timeslot:
                meeting_name=str(self.G.nodes[meeting]['label'])
                print("Meeting " + meeting_name, end='')
                print(" (", end='')
                print(", ".join(self.meetings[meeting_name]), end='')
                print(")\t\t\t\t\t\t", end='')
            startTime=endTime
            count+=1


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

    startTime = datetime.datetime.strptime('20/09/2019 14:00', "%d/%m/%Y %H:%M")
    endTime = datetime.datetime.strptime('20/09/2019 18:00', "%d/%m/%Y %H:%M")

    timetable.schedule(startTime, endTime)
