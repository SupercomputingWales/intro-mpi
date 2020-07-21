#!/bin/bash --login
#SBATCH -n 12
#SBATCH -t 0-00:05:00
#SBATCH -J PointNonBlocking
#SBATCH --account scw1148
#SBATCH -p compute
#SBATCH -o point.nonblock.out.%J

# Load required modules.
module purge
module load mpi4py/20181128
module list

# Create an output directory on the fast scratch filesystem, and
# run from this directory.
WDPATH=/scratch/$USER/mpi_training/point_nonblock.$SLURM_JOBID
mkdir -p $WDPATH
cd $WDPATH

# Copy the python code to the run directory
cp $SLURM_SUBMIT_DIR/point_nonblock.py .

# Run a number of copies of the code equal to the number of
# MPI processes requested.
mpirun -np 12 ./point_nonblock.py
