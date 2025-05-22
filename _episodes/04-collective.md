---
title: "MPI collective communication"
teaching: 45
exercises: 15
questions:
- "How do I avoid having to use multiple recvs and sends?"
- "What operations can be performed by all processors at once?"
objectives:
- "Understand what are collective communications"
- "Benefit from optimizations in commnication patterns"
keypoints:
- "Collective communications make the code easier to understand the purpose."
---

The previous section coverred the topic of point to point communication where a message can be sent from one MPI task to
another.  Although these are the building blocks of MPI there are a number of common communication patterns that are
provided within the MPI standard.  The **collective** communications are when all MPI tasks can be involved in a single
function call.  This replaces multiple calls to recv and send, easier to understand and provides internal optimisations
to communication.

## Broadcasting

If a MPI task requires data to be send to all processors then `MPI_Bcast` can be used to make sure this occurs.  It is a
very basic sending of data from a single MPI task with all the other MPI tasks receiving the data.  In `mpi4py` it is
achieved with:

~~~
comm.Bcast([buffer, MPI_INT], root=0)
~~~
{: .language-python}

Or with the general-purpose method:

~~~
buffer = comm.bcast(buffer, root=0)
~~~
{: .language-python}

Where `buffer` is the the data to be broadcast for the MPI task given as root (in this case 0).  The MPI datatype is
optional and automatic discovery can be used instead with the lowercase method name.

## Scattering and gathering

If data needs to be shared across processors to decompose the problem into a small subset it can be performed with
`MPI_Scatter`.  When the data needs to be collected again on an MPI task the gather function `MPI_Gather` can be used.
In `mpi4py` this is achieved with:

~~~
recvbuffer = comm.scatter(sendbuffer, root=0)
recvbuffer = comm.gather(sendbuffer, root=0)
~~~
{: .language-python}

For scatter, sendbuffer is defined on MPI task 0 whilst for gather recvbuffer returns a value only on MPI task 0.

There are also the uppercase `comm.Scatter` and `comm.Gather` along with non-blocking variants `comm.Iscatter` and
`comm.Igather` that has to be provided with datatypes of the data (or using `numpy` arrays).

## Further scattering and gathering

Scatter and gather are the building blocks for many other types of communication patterns with the only difference being where we want the results to reside.

> ## Gather-like
> - `MPI_Allgather` - gather one array onto all tasks. `comm.allgather` or `comm.Allgather`
> - `MPI_Gatherv` - gather arrays of different lengths onto a task. `comm.gatherv` or `comm.Gatherv`
> - `MPI_Allgatherv` - gather arrays of different lengths onto all tasks. `comm.allgatherv` or `comm.Allgatherv`
{: .callout}

> ## Scatter-like
> - `MPI_Scatter` - scatter one array onto all tasks. `comm.scatter` or `comm.Scatter`
> - `MPI_Scatterv` - scatter array into different lengths onto all tasks. `comm.scatterv` or `comm.Scatterv`
{: .callout}

> ## All-to-all
> - `MPI_Alltoall` - every task sends equal length parts to all other tasks. `comm.alltoall` or `comm.Alltoall`
> - `MPI_Alltoalllv` - every task sends unequal length parts to all other tasks. `comm.alltoallv` or `comm.Alltoallv`
{: .callout}

There are also the non-blocking versions of all communication, e.g. `MPI_Iallgather` where `mpi4py` provides
`comm.Iallgather`.

> ## Scatter example
>
> Scatter a chunk of data using collective functions in `mpi4py`.  Each processor should be provided with 2 chunks of
> the data from the MPI task performing the scatter.
> 
> Should we use `comm.Scatter` or `comm.scatter`?
> > ## Solution
> >
> > In this example we fix the size of the array to scatter as `nprocs`,
> > the size of the communicator (number of MPI tasks).
> > ~~~
> > if rank == 0:
>>    senddata = [(x+1)**x for x in range(nprocs)]
>>    print('we will be scattering:',senddata) 
> > else:
> >   senddata = None
> > ~~~
> > {: .language-python}
> >
> > When scattering the data the receiving array is sized to be just `allosize`.
> > ~~~
> > recvdata = [None]
> > recvdata = comm.scatter(senddata, root=0)
> > ~~~
> > {: .language-python}
> > 
> > See the example in [scatter.py]({{ site.baseurl }}/files/example3/scatter.py) and the corresponding [slurm job script]({{ site.baseurl }}/files/example3/scatter-slurm.sh).
> > 
> {: .solution}
{: .challenge}

## Reduction

A reduction allows for an operation to be performed on data as it is being communicated.  `MPI_Reduce` allows for this
operation to occur with the result returned on one MPI task.  `mpi4py` provides `comm.reduce` or `comm.Reduce`.  The supported operations can be:

- `MPI_MAX` - Returns the maximum element.
- `MPI_MIN` - Returns the minimum element.
- `MPI_SUM` - Sums the elements.
- `MPI_PROD` - Multiplies all elements.
- `MPI_LAND` - Performs a logical and across the elements.
- `MPI_LOR` - Performs a logical or across the elements.
- `MPI_BAND` - Performs a bitwise and across the bits of the elements.
- `MPI_BOR` - Performs a bitwise or across the bits of the elements.
- `MPI_MAXLOC` - Returns the maximum value and the rank of the process that owns it.
- `MPI_MINLOC` - Returns the minimum value and the rank of the process that owns it.

The `mpi4py` equivalents are part of the MPI module, for example `MPI_MAX` is `MPI.MAX`.

If the result is required on all MPI tasks then `MPI_Allreduce` is used instead.  This would be similar to a
`MPI_Reduce` followed by a `MPI_Bcast`.

> ## Beware!
>
> Reductions can produce issues. With floating-point numbers a reduction can occur in any order and therefore summations
> are non-reproducible.  This means every time you run the code it may give different answers and also across different
> number of processors.  If reproducibility is important then one way is to gather all the data to a single MPI task and
> perform the operation in a controlled manner - this would harm performance.  If you do not need reproducibility across
> different number of processors then summation on each processor and then reduce might be better.
{: .callout}

> ## Sine Integral
>
> Using the above collectives obtain the integral of `sin(x)`.
> - broadcast the number of points being used.
> - each MPI task calculates the region it needs to do.
> - perform the calculation on its range.
> - use the `MPI_Reduce` method to sum the data.
>
> Can you think of other ways of doing this?
> > ## Solution
> >
> > Lets assume rank 0 only knows the value of numpoints (read from configuration file or stdin).
> > 
> > ~~~
> > if rank == 0:
> >   recvbuffer = np.array(numpoints)
> > else:
> >   recvbuffer = np.array(0)
> > comm.Bcast([recvbuffer, MPI.INT], root=0)
> > ~~~
> > {: .language-python}
> > 
> > Next calculate the range the MPI task should use.
> > 
> > ~~~
> > nlocal = (numpoints - 1) / nprocs + 1
> > nbeg = int((rank * nlocal) + 1)
> > nend = int(min((nbeg + nlocal - 1), numpoints))
> > ~~~
> > {: .language-python}
> >
> > Perform the integration
> >
> > ~~~
> > for i in range(nbeg, nend):
> >   psum += np.sin((i - 0.5) * delta) * delta
> > ~~~
> > {: .language-python}
> > 
> > Finally perform a reductin on all the local summations on each MPI task
> >
> > ~~~
> > resbuffer = np.array(0.0, 'd')
> > comm.Reduce([psum, MPI.DOUBLE], resbuffer, op=MPI.SUM, root=0)
> > ~~~
> > {: .language-python}
> > 
> > For the complete solution see [sine.py]({{ site.baseurl }}/files/example4/sine.py) and the corresponding [slurm job script]({{ site.baseurl }}/files/example4/sine-slurm.sh).
> {: .solution}
{: .challenge}


{% include links.md %}

