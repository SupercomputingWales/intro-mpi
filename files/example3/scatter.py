#!/bin/env python3
# Scatter data across multiple processes. The data consists of a
# two-dimensional numpy array, which each process receiving a row.

# load the required modules
from mpi4py import MPI

if __name__ == "__main__":

    # Initialise a communicator and get the rank of this process.
    try:
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        nprocs = comm.size
    except Exception as err:
        sys.exit("Error: %s" % err)


    # The root process initially holds the data array. It is populated with
    # integers and shaped to match the number of processes. Note, this is
    # for convenience - in reality allocating your data amongst processes
    # can be a major challenge.
    if rank == 0:
        senddata = [(x+1)**x for x in range(nprocs)]
        print('we will be scattering:',senddata)
    else:
        senddata = None

    # Each process has an initially empty array set up to receive its share
    # of the data.
    recvdata = [None]

    # Break up the two-dimensional array amongst processes.
    recvdata=comm.scatter(senddata, root=0)

    # Each process prints out the data it has received.
    print ("rank = ", rank, "recvdata = ", recvdata)
