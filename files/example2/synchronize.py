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
