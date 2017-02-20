# !/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import print_function
import numpy as np
import heapq
from threading import Thread, Condition
import time
from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

exitflag = 0
opt_cost = 99999
edge_seq = [[]]
condition = Condition()
file_name = 'Input.csv'


# Function for updating list
def update_lists(l, item):
    l.extend([item])
    return l


# This class is implemented for function of priority queue

class PriorityQueue:
    def __init__(self):
        self._State_queue = []
        self._State_index = 0

    def push(self, item, priority):
        heapq.heappush(self._State_queue, (priority, self._State_index,
                                           item))
        print('Item pushed with priority ' + str(priority))
        self._State_index += 1

    def pop(self):
        self._State_index -= 1
        return heapq.heappop(self._State_queue)[-1]

    def isEmpty(self):
        return self._State_index == 0


# This class is for representing graph

class garph_class:
    # Declaration of members of Class graph_class

    def __init__(self):
        self.vertex_count = 0
        self.get_count()
        self.graph = np.zeros((self.vertex_count, self.vertex_count),
                              dtype=float)
        self.generate_edge()
        self.opt_cycle = []

    def get_count(self):
        global file_name
        m = np.loadtxt(file_name, delimiter=',')
        self.vertex_count = len(m)

    # This function collects

    def generate_edge(self):
        global file_name
        m = np.loadtxt(file_name, delimiter=',')
        for i in range(0, self.vertex_count):
            for j in range(0, self.vertex_count):
                self.graph[i][j] = m[i][j]

    # This function just displays the graph in adjacency graph

    def print_graph(self):
        print(self.graph.astype(int))

    def update_opt_cycle(self, list):
        self.opt_cycle = list


# This is class represents

class State:
    # Declaration of members of class

    def __init__(
            self,
            g,
            n,
            id,
            l1,
            l2,
            r,
            s,
    ):
        self.cost = float
        self.include_list = l1
        self.exclude_list = l2
        self.graph = np.zeros((n, n), dtype=int)
        self.graph = g
        self.sequence_id = id
        self.saturated_vertex = s
        self.record = r
        self.degree = int(n - 1)

    # This function checks for vertex if it has already incident two
    # edges then it marks other to exclude list or vice vera

    def update_graph(self, vertex, flag):
        index = []
        global edge_seq

        if flag == 1:
            for i in self.include_list:
                if edge_seq[i][0] == vertex:
                    update_lists(index, edge_seq[i][1])
                if edge_seq[i][1] == vertex:
                    update_lists(index, edge_seq[i][0])
            for i in range(0, (self.degree + 1) * self.degree / 2):
                if vertex in edge_seq[i]:
                    if set(index).isdisjoint(edge_seq[i]):
                        if i not in self.exclude_list:
                            self.graph[edge_seq[i][0]][edge_seq[i][1]] = \
                                922337
                            self.graph[edge_seq[i][1]][edge_seq[i][0]] = \
                                922337
                            update_lists(self.exclude_list, i)
                            #print 'in update graph saturated vertex excludes edge:' \
                                  #+ str(edge_seq[i])
                            self.update_record(i, 0)

                            # print self.record

                            if edge_seq[i][0] == vertex:
                                ind = edge_seq[i][1]
                            elif edge_seq[i][1] == vertex:
                                ind = edge_seq[i][0]
                            if self.check_saturation(ind, 0):
                                #print 'Automtically vertex saturated ' \
                                      #+ str(ind)
                                if ind not in self.saturated_vertex:
                                    update_lists(self.saturated_vertex,
                                                 ind)
                                self.update_graph(int(ind), 0)

        if flag == 0:
            for i in self.exclude_list:
                if edge_seq[i][0] == vertex:
                    update_lists(index, edge_seq[i][1])
                if edge_seq[i][1] == vertex:
                    update_lists(index, edge_seq[i][0])

                    # print index

            for i in range(0, (self.degree + 1) * self.degree / 2):
                if vertex in edge_seq[i]:
                    if set(index).isdisjoint(edge_seq[i]):
                        if i not in self.include_list:
                            update_lists(self.include_list, i)
                            #print 'in update graph saturated vertex include edge:' \
                                  #+ str(edge_seq[i])
                            self.update_record(i, 1)

                            # print self.record

                            if edge_seq[i][0] == vertex:
                                ind = edge_seq[i][1]
                            elif edge_seq[i][1] == vertex:
                                ind = edge_seq[i][0]
                            if self.check_saturation(ind, 1):
                                #print 'Automticaly vertex saturated ' \
                                      #+ str(ind)
                                if ind not in self.saturated_vertex:
                                    update_lists(self.saturated_vertex,
                                                 ind)
                                self.update_graph(int(ind), 1)

    # Cost calculation

    def calculate_cost(self):
        cost = 0

        # print self.graph

        itr = self.graph.argsort()
        for i in range(0, self.degree + 1):
            x = itr[i][0]
            y = itr[i][1]
            cost = cost + self.graph[i][x] + self.graph[i][y]
            # print str(self.graph[i][x]) + ' ' + str(self.graph[i][y])

        self.cost = cost / 2
        return self.cost

    def update_record(self, index, flag):
        global edge_seq
        i = edge_seq[index][0]
        j = edge_seq[index][1]
        if flag == 0:
            self.record[i][1] = self.record[i][1] - 1
            self.record[j][1] = self.record[j][1] - 1
        elif flag == 1:
            self.record[i][0] = self.record[i][0] + 1
            self.record[j][0] = self.record[j][0] + 1

            # print self.record

    def check_saturation(self, vertex, flag):
        if vertex not in self.saturated_vertex:
            if flag == 1:
                if self.record[vertex][0] == 2:
                    #print 'Saturation check Success for ' + str(vertex)
                    return True
                else:
                    return False
            elif flag == 0:
                if self.degree + self.record[vertex][1] == 2:
                    #print 'Saturation check Success for ' + str(vertex)
                    return True
                else:
                    return False
        else:
            #print('Oops')
            return True

            # This is the function checks if selected edge can be excluded or included and for possible states it calculates cost

    def check_exclude(self, index):
        global edge_seq
        i = edge_seq[index][0]
        j = edge_seq[index][1]

        # If vertex already have two incedent edges

        if self.check_saturation(i, 0) or self.check_saturation(j, 0):
            print("Can't add edge :" + str(edge_seq[index]))
            return False
        update_lists(self.exclude_list, index)
        #print 'in check incidence excluded appended ' + str(index)
        #print 'Lists updated on exclude:'
        #print 'include-' + str(self.include_list)
        #print 'exclude-' + str(self.exclude_list)

        self.update_record(index, 0)

        # print "check saturation..."

        if self.check_saturation(i, 0):
            #print 'vertex saturated ' + str(i)
            if i not in self.saturated_vertex:
                update_lists(self.saturated_vertex, i)
            self.update_graph(int(i), 0)

        if self.check_saturation(j, 0):
            #print 'vertex saturated ' + str(j)
            if j not in self.saturated_vertex:
                update_lists(self.saturated_vertex, j)
            self.update_graph(int(j), 0)

        self.graph[i][j] = 922337
        self.graph[j][i] = 922337
        self.calculate_cost()
        return True

        # This is the function checks if selected edge can be excluded or included and for possible states it calculates cost

    def check_include(self, index):
        global edge_seq

        # When edge is to be included

        i = edge_seq[index][0]
        j = edge_seq[index][1]

        # If vertex already have two incedent edges

        if self.check_saturation(i, 0) or self.check_saturation(j, 0):
            print("Can't add edge :" + str(edge_seq[index]))
            return False
        f = 0
        v = -1
        update_lists(self.include_list, index)

        print('Lists updated on include:')
        print('include-' + str(self.include_list))
        print('exclude-' + str(self.exclude_list))

        self.update_record(index, 1)

        # print "Check saturation for vertex " + str(i)

        if self.check_saturation(i, 1):
            f = f + 1

            # print "vertex saturated " + str(i)

            if i not in self.saturated_vertex:
                update_lists(self.saturated_vertex, i)
            self.update_graph(int(i), 1)
            v = i

            # print "Check saturation for vertex " + str(j)

        if self.check_saturation(j, 1):
            f = f + 1

            # print "vertex saturated " + str(j)

            if j not in self.saturated_vertex:
                update_lists(self.saturated_vertex, j)
            self.update_graph(int(j), 1)
            v = j

        if f == 0:

            # print "flag =" + str(f)

            cost = 0

            # print self.graph

            itr = self.graph.argsort()
            for x in range(0, self.degree + 1):
                if x is i:
                    cost = cost + self.graph[x][itr[x][0]] \
                           + self.graph[i][j]
                elif x is j:

                    # print  str(self.graph[x][itr[x][0]]) + "-> " + str(self.graph[i][j])

                    cost = cost + self.graph[x][itr[x][0]] \
                           + self.graph[j][i]
                    print(str(self.graph[x][itr[x][0]]) + ' ' \
                          + str(self.graph[j][i]))
                else:
                    cost = cost + self.graph[x][itr[x][0]] \
                           + self.graph[x][itr[x][1]]

                    # print str(self.graph[x][itr[x][0]]) + " " + str(self.graph[x][itr[x][1]])

            self.cost = cost / 2
        if f == 1:

            # print "flag =" + str(f)

            cost = 0

            # print self.graph

            itr = self.graph.argsort()
            for x in range(0, self.degree + 1):
                if x == v:
                    if v == i:
                        w = j
                    elif v == j:
                        w = i
                    if w == itr[x][0]:
                        cost = cost + self.graph[x][itr[x][0]] \
                               + self.graph[x][itr[x][1]]
                    else:

                        # print str(self.graph[x][itr[x][0]]) + " " + str(self.graph[x][itr[x][1]])

                        cost = cost + self.graph[x][itr[x][0]] \
                               + self.graph[v][w]
                else:

                    # print str(itr[x][0]) + " " + str(w)
                    # print str(self.graph[x][itr[x][0]]) + " -> " + str(self.graph[v][w])

                    cost = cost + self.graph[x][itr[x][0]] \
                           + self.graph[x][itr[x][1]]

                    # print str(self.graph[x][itr[x][0]]) + " " + str(self.graph[x][itr[x][1]])

            self.cost = cost / 2
        if f == 2:
            # print "flag =" + str(f)

            self.calculate_cost()

        return True

        # This function checks if the

    def is_valid_cycle(self):
        global exitflag
        #print 'Saturated vertex'
        #print self.saturated_vertex
        if len(self.saturated_vertex) == self.degree + 1:
            list = []
            for i in range(0, self.degree + 1):
                for j in range(0, self.degree + 1):
                    if self.graph[i][j] == 922337:
                        pass
                    else:
                        update_lists(list, j)

            if len(list) == (self.degree + 1) * 2:
                for i in range(0, self.degree + 1):
                    if list.count(i) is not 2:
                        print('Not a valid cycle!!')
                        return False
                print('Woho!! Valid cycle!')

                return True
        else:

            print('Not a vaid cycle!!')
            return False


def generate_edge_seq(g):
    global edge_seq
    n = g.vertex_count
    n = n * (n - 1) / 2
    index = 0
    edge_seq = np.zeros((n, 2), dtype=int)
    for i in range(0, g.vertex_count):
        for j in range(0, g.vertex_count):
            if i is not j:
                if i < j:
                    edge_seq[index][0] = int(i)
                    edge_seq[index][1] = int(j)
                    index = index + 1


# generation of Root state

def generate_root():
    l1 = []
    l2 = []
    l = []
    r = np.zeros((g.vertex_count, 2), dtype=int)
    sroot = State(
        g.graph,
        g.vertex_count,
        -1,
        l1,
        l2,
        r,
        l,
    )
    cost = sroot.calculate_cost()
    print('Root generated with cost:' + str(cost))
    return sroot


def create_copy(parent):
    id = parent.sequence_id
    id = id + 1
    n = parent.degree + 1
    inc_l = []
    exc_l = []
    v_s = []
    graph = np.zeros((n, n), dtype=float)
    record = np.zeros((n, 2), dtype=int)
    for i in parent.include_list:
        inc_l.extend([i])
    for j in parent.exclude_list:
        exc_l.extend([j])
    for j in parent.saturated_vertex:
        v_s.extend([j])
    for i in range(0, n):
        for j in range(0, n):
            graph[i][j] = parent.graph[i][j]
    for i in range(0, n):
        for j in range(0, 2):
            record[i][j] = parent.record[i][j]
    child = State(
        graph,
        n,
        id,
        inc_l,
        exc_l,
        record,
        v_s,
    )

    return child


    # State(local.graph,local.edge_seq,local.degree + 1,id,local.include_list,local.exclude_list,local.record,local.saturated_vertex)



# main function controlling entire flow

if __name__ == '__main__':


    q = PriorityQueue()
    opt = PriorityQueue()
    g = garph_class()
    generate_edge_seq(g)



    if rank == 0:

        g.print_graph()

        if q:
            root = generate_root()
            q.push(root, root.cost)
        else:
            print('Error!!')

        workers = size - 1

        while q._State_index is not workers:
            if q.isEmpty() == False:
                local = q.pop()
                print("State poped - " + str(local.cost))
                print("include-" + str(local.include_list))
                print("exclude-" + str(local.exclude_list))
                # print lowerbound
                flag = 0
                # Check if cycle with less cost is already found
                # pruning
                if local.cost < opt_cost:
                    id = local.sequence_id
                    id = id + 1
                    # print "id :" + str(local.sequence_id)
                    # print "lesser lower bound"

                    print("Parent: " + str(local.cost))
                    # State generated with the edge
                    along = create_copy(local)

                    # along.adjust_sequence_id()

                    if along.check_include(id):
                        print(
                            "State generated along edge " + str(edge_seq[id]) + " with cost: " + str(along.cost))
                        flag = 1
                        if along.is_valid_cycle():
                            if opt.isEmpty() == True:
                                opt_cost = along.cost
                                #comm.bcast(opt_cost, root=rank)
                                opt.push(along, along.cost)


                            else:
                                if opt_cost > along.cost:
                                    opt_cost = along.cost
                                    #comm.bcast(opt_cost, root=rank)
                                    opt.push(along, along.cost)
                                    print(opt_cost)

                        else:
                            q.push(along, along.cost)

                    # State generated with the edge
                    print("Parent: " + str(local.cost))
                    without = create_copy(local)

                    # without.adjust_sequence_id()

                    if without.check_exclude(id):
                        print("State generated without edge " + str(edge_seq[id]) + " with cost: " + str(
                            without.cost))
                        flag = 1
                        if without.is_valid_cycle():
                            if opt.isEmpty() == True:
                                opt_cost = without.cost
                                #comm.bcast(opt_cost, root=rank)
                                opt.push(without, without.cost)

                            else:
                                if opt_cost > without.cost:
                                    opt_cost = without.cost
                                    #comm.bcast(opt_cost, root=rank)
                                    opt.push(without, without.cost)

                        else:
                            q.push(without, without.cost)

                    if flag == 0:
                        local.sequence_id += 1
                        q.push(local, local.cost)

        start_time = time.time()
        for process in range(1,size):
            print('Sending state to process',process)
            l = []
            data = q.pop()
            l.append(data)
            l.append(opt_cost)
            comm.send(l,dest = process,tag =0)



    if rank > 0:
        coworker = 1
        if rank is 1:
            coworker = 2
        l = comm.recv(source=0, tag=0)
        print('Process ',rank,' received state node.')
        remote = l[0]
        opt_cost = l[1]
        q.push(remote,remote.cost)
        while(q.isEmpty()==False):
            local = q.pop()
            if comm.Iprobe(source=coworker, tag=12):
                cost = comm.recv(source=coworker, tag=12)
                print('Received new opt cost..')
                if cost < opt_cost:
                    opt_cost = cost
            if local.cost < opt_cost:
                print(str(rank) + " popped - " + str(local.cost))
                print("include-" + str(local.include_list))
                print("exclude-" + str(local.exclude_list))
                flag = 0
                f1 = 0
                f2 = 0
                opt_flag = 0

                id = local.sequence_id
                id += 1

                if id <= len(edge_seq):

                    # print "id :" + str(local.sequence_id)
                    # print "lesser lower bound"

                    print('Parent: ' + str(local.cost))
                    along = create_copy(local)
                    print('Lists Generated:')
                    print('include-' + str(along.include_list))
                    print('exclude-' + str(along.exclude_list))

                    # along.adjust_sequence_id()

                    if along.check_include(id):
                        print('State generated by ' + str(rank)+' along edge ' + str(edge_seq[id]) \
                        + ' with cost: ' + str(along.cost))
                        flag = 1
                        if along.is_valid_cycle():

                            if opt_cost > along.cost:
                                print(opt_cost)
                                opt_cost = along.cost
                                opt_flag = 1
                                print("New optimal tour cost generated...")
                                opt.push(along, along.cost)
                                print(opt_cost)
                            else:
                                print('This cycle is not optimal')


                        else:

                            f1 = 1

                    # State generated with the edge

                    print('Parent: ' + str(local.cost))
                    without = create_copy(local)
                    print('Lists Generated:')
                    print('include-' + str(without.include_list))
                    print('exclude-' + str(without.exclude_list))

                    # without.adjust_sequence_id()

                    if without.check_exclude(id):
                        print('State generated by ' + str(rank)+' without edge ' + str(edge_seq[id]) \
                              + ' with cost: ' + str(without.cost))
                        flag = 1
                        if without.is_valid_cycle():
                            flag = 1
                            if opt_cost > without.cost:
                                print(opt_cost)
                                opt_cost = without.cost
                                opt_flag = 1
                                print("New optimal tour cost generated...")
                                opt.push(without, without.cost)
                                print(opt_cost)
                            else:
                                print('This cycle is not optimal')
                        else:

                            f2 = 1

                    # No child generated
                    if flag == 0:
                        if opt_cost> local.cost:
                            print("Pushing back the original node..")
                            local.sequence_id = id
                            q.push(local, local.cost)
                    # Child generated
                    else:
                        # Both being pushed
                        if f1 == 1 and f2 == 1:
                            if opt_cost> along.cost:
                                q.push(along,along.cost)
                            if opt_cost > without.cost:
                                q.push(without,without.cost)
                        # Single needs to be pushed
                        elif f1 == 1 and f2 == 0:
                            if opt_cost > along.cost:
                                q.push(along, along.cost)
                        # Single needs to be pushed
                        elif f1 == 0 and f2 == 1:
                            if opt_cost > without.cost:
                                q.push(without, without.cost)

                    if opt_flag==1:
                        print(str(rank)+' Sending new tour cost')
                        comm.send(opt_cost, dest = coworker, tag = 12)
            else:
                print('Pruning as cost greater than optimal cost')





        print('For process ', rank,' optimal cost is ',opt_cost)
        if opt.isEmpty() == False:
            print(opt._State_index)
            o = opt.pop()
            if o.cost <= opt_cost:
                comm.send(o,dest = 0,tag= 30)
            else:
                print('Tour with least Cost found by another process')
                comm.send(False,dest = 0,tag = 30)
        else:
            print('No tour found by ',rank)





    if rank == 0:
        execution_time = time.time() - start_time
        print("--- %s seconds ---" % (execution_time))
        for worker in range(1,size):
            ob = comm.recv(source = worker,tag = 30)
            if ob:
                print('The optimal tour cost =' + str(ob.cost))
                print('The optimal tour includes edges:')
                for i in ob.include_list:
                    print(edge_seq[i])
