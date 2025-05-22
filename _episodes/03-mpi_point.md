---
title: "MPI point to point communication"
teaching: 45
exercises: 15
questions:
- "How do I send a message?"
- "How do I know if it was successful?"
objectives:
- "Understand how to send a message"
- "Know when to use blocking and non-blocking communication."
keypoints:
- "Sending messages to another processor is like sending a letter."
- "Non-blocking is most flexible type of point to point communication - just make sure you check for completion."
---

The first type of communication in MPI is called "Point to Point" where you have some data and know which other MPI task
to send and receive from.

> ## Refresher
> Check you understand what `MPI_Init`, `MPI_COMM_WORLD`, `MPI_comm_rank` and `MPI_comm_size` are.
> 
> > ## `MPI_init` and `MPI_init_thread`
> > - Initialises MPI environment inside code.
> > - Strictly speaking code before this is called has undefined behaviour.
> > - Function automatically called by `mpi4py` library.
> > - Capture the error messages from this function.
> {: .solution}
> > ## `MPI_COMM_WORLD`
> > - MPI communicator representing a method to talk to all processors.
> > - The `mpi4py` library represents this with `MPI.COMM_WORLD`
> > - Having different communicators is quite advanced.
> > - This is most common communicator to use.
> {: .solution}
> > ## `MPI_comm_size`
> > - Function that returns the size of the communicator.
> > - The `mpi4py` library represents this in a class method **Get_size()**
> > - Stops having to read number of processors from elsewhere.
> > - For `MPI_COMM_WORLD` it should return the number of processors.
> > - Allows for dynamic allocation of resources without recompiling or relying on hard-coded arrays.
> {: .solution}
> > ## `MPI_comm_rank`
> > - An identifier within the communicator between `0` and `MPI_comm_size-1`
> > - The `mpi4py` library represents this in a class method **Get_rank()**
> > - Can be confusing in Fortran as arrays are usually indexed from 1.
> > - Used as part of the address when communicating messages.
> {: .solution}
> > ## `MPI_finalize`
> > - Tells the MPI layer we have finished.
> > - Any MPI calls after this will be an error.
> > - Does not stop the program.
> > - Usually called near (or at) the end.
> > - The `mpi4py` library calls this automatically when exiting.
> > - Alternatively `MPI_abort` can be used
> >   - Aborts task in communicator
> >   - One processor may cause the abort.
> >   - Should only be used for unrecoverable error.
> >   - `mpi4py` can perform this automatically with unhandled exceptions in Python using `-m mpi4py` method of running.
> {: .solution}
{: .challenge}

## Basics

Before code is written to perform communication, lets revisit a simple "Hello World" example.

> ## Hello World
> 
> Create a simple MPI program that does the following:
> - Loads the `mpi4py` module
> - Gets the rank of the MPI task.
> - Gets the maximum number of the MPI tasks.
> - Print message including its rank.
> - Leader task only prints the maximum number of tasks.
>
> > ## Solution
> > 
> > Example code available [hello_parallel.py]({{ site.baseurl }}/files/example1/hello_parallel.py)
> > Important lines are:
> > - `from mpi4py import MPI`
> > - `comm = MPI.COMM_WORLD`
> > - `rank = comm.Get_rank()`
> > - `size = comm.Get_size()`
> > - `if rank == 0:`
> {: .solution}
{: .challenge}

To run the code you can use as a basis [hello_parallel-slurm.sh]({{ site.baseurl }}/files/example1/hello_parallel-slurm.sh)

## MPI_Send and MPI_Recv

The first type of communication is using a blocking send and receive.  This will not process any further code until the
send has been completed (i.e. why it is described as blocking).  With `mpi4py` we can use `comm.send` and `comm.recv`.

A message is just identifiable data on the network:
- Think of it as an envelope
- Various datatypes can be used inside this *envelope*
- Python objects are *serialized* into standard datatypes.
- Data length can be zero to many MBs.
- Messages can have tag identifiers to further identify them.

The send and receives **have** to work in partnership. Without a receive to pick up the data from the (blocking)
send the code will hit a deadlock with the code not able to progress with both MPI tasks waiting for their
communications to complete. Therefore every send must have a receive (and vice-versa).

There is also a special `MPI_ANY_SOURCE` to receive from any sender.

## Tagging

Tags allow messages to be further identified and can be used to make messages read in the correct order. There is no
guarantee messages arrive in the order they were sent. Tags can have any value but ideally should be identifiable
uniquely so errors in communication can be traced if the tag number is given.

A special tag identifier `MPI_ANY_TAG` can ignore tag number.

## Python interface

The `mpi4py` interface to `MPI_Send` and `MPI_Recv` is with the following:

~~~
comm.send(data, dest=?, tag=?)
data = comm.recv(source=?, tag=?)
~~~
{: .language-python}

> ## Exchanging odd with even
> 
> Lets use the knowledge of sending and receiving data by exchanging data between pairs of MPI tasks.
> - Each pair will exchange data with each other
> - Tasks with an even rank number will send data to `rank+1`
> - Tasks with an odd rank number will send data to `rank-1`
>
> > ## Solution
> > 
> > The key thing is to make sure one of the pairs (either the odd or even) send the data first whilst the other pair
> > waits to receive the data.  See [point.py]({{ site.baseurl }}/files/example2/point.py) and the corresponding [slurm job script]({{ site.baseurl }}/files/example2/pointtopoint-slurm.sh).
> {: .solution}
{: .challenge}

## Non-blocking

A standard send or receive will block waiting for the operation to complete and can cause deadlocks.  The non-blocking
versions are very similar but need to be careful to wait for communication to complete before using the data location.
For example to send:

~~~
req = comm.isend(data, dest=1, tag=11)
req.wait()
~~~
{: .language-python}

Whilst to receive:

~~~
req = comm.irecv(source=0, tag=11)
data = req.wait()
~~~
{: .language-python}

Notice the `wait()` method is used to declare when the code should wait for completion.  Useful for exchanging data if
sending and receiving at the same time.

> ## Non-blocking communication
>
> Try revisiting the previous example of sending data between pairs of processors. How can this be done with
> non-blocking communication?
>
> > ## Solution
> > 
> > The key difference is the sends and receives do not need to be different (no matching send to a receive in order
> > this time.  Just `isend` and `irecv` and then `wait` for the sends to complete and then receive the data.
> > 
> > Check out the [point_nonblock.py]({{ site.baseurl }}/files/example2/point_nonblock.py) and the corresponding [slurm job script]({{ site.baseurl }}/files/example2/{{ site.baseurl }}/files/example2/point_nonblock.py).
> {: .solution}
{: .challenge}


## Synchronize

Now that it is possible to communicate between MPI tasks.  It is sometimes useful to make sure all MPI tasks are at the
same location in the code.  Could be used for:
- timing locations in the code
- tidy up the output from the code.

A task enters `MPI_Barrier` and waits for all other MPI tasks to reach the same location in the code.  If an MPI task
does not reach the barrier then a deadlock will occur.

In `mpi4py` this is achieved with `comm.barrier()`.  For example

~~~
from mpi4py import MPI
import time
comm = MPI.COMM_WORLD
id = comm.Get_rank()
time.sleep(id)
comm.barrier()
print(f"Hello from rank {id}", flush=True)
time.sleep(id)
comm.barrier()
print(f"Bye from rank {id}", flush=True)
~~~
{: .language-python}

With `comm.barrier()`:

~~~
Hello from rank 0
Hello from rank 1
Hello from rank 2
Hello from rank 3
Bye from rank 3
Bye from rank 0
Bye from rank 1
Bye from rank 2
~~~
{: .output}

Without `comm.barrier()`:

~~~
Hello from rank 0
Bye from rank 0
Hello from rank 1
Hello from rank 2
Bye from rank 1
Hello from rank 3
Bye from rank 2
Bye from rank 3
~~~
{: .output}

It should be noted that synchronization points such as `MPI_Barrier` can waste resource and harm scalability since some
MPI tasks might be waiting in the barrier not doing any work.

## Identification

It is sometimes useful to know where your MPI task is running - imagine a 1000 MPI task job across a number of servers -
how do we identify which server the MPI task was on?

With `MPI_Get_processor_name` is it possible to obtain a unique string to identify the server/resource it is running on.

In `mpi4py` it is called with:

~~~
from mpi4py import MPI
MPI.Get_processor_name()
~~~
{: .language-python}

## Optimizing communication

In `mpi4py` there are multiple ways to call the same method due to its automatic handling of Python datatypes such as
dictionaries and lists. These calls tend to start with a lowercase as in the examples above, e.g. `comm.irecv` but to
gain some speedup there are the direct C-style functions called with uppercase, e.g. `comm.Irecv` and expects the
buffers to be passed as an argument as in `comm.Irecv([buffer, MPI_INT], source=0, tag=0)`. Note the `buffer` is now in
n list with the second entry the MPI datatype of the buffer.  This speeds up commnicatation rather than `mpi4py`
converting all buffers with raw bytes with pickle but can only be used for MPI standard types.

When using `numpy` arrays, the datatype of the arrays is stored with the data and therefore `mpi4py` can query the
datatype and specify the correct MPI datatype in the communication.  This only supports standard `numpy` C datatypes.

To keep things simple we will use the lowercase variant that supports all types.



## Further information

Please check [mpi4py](https://mpi4py.readthedocs.io/en/stable/index.html) documentation site.  Especially the tutorial
secion.

{% include links.md %}

