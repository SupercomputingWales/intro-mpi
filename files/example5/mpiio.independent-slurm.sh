#!/bin/bash --login
#SBATCH -n 4
#SBATCH -t 0-00:05:00
#SBATCH -J MPIIO.Independent
#SBATCH -p compute
#SBATCH --account scwXXXX
#SBATCH -o out.mpiio.independent.%j

# if run on a training session add your reservation code as
# #SBATCH --reservation=training

# Load required modules.
module purge
module load mpi4py/3.1.5

# Run a number of copies of the code equal to the number of
# MPI processes requested.
mpirun -np 4${SLURM_NTASKS} python3 mpiio.independent.py
