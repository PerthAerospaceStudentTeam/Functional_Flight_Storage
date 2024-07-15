# Functional Flight Storage
Secondary Storage for PAST Cubesat

# Project Structure
- All supporting documentation can be found in `support-documents`
- `usage` contains the information on how to use and interface with the storage chips
  - `hardware` contains the files related to the hardware of the flight storage
    - Corresponding PCB schematics can be found in `pcbs`
      - `gerbers` contain the ready to use schematics
      - `altium` contains the source altium files
    - `gridfinity-mount` contains the information on how to mount the storage chips to the gridfinity specs [found here](https://github.com/PerthAerospaceStudentTeam/Modular_FlatSat-Style_Avionics_Testbed)
  - `software` contains the files related to the software of the flight storage
    - `testing` contains all testing logic and the outputs from them
    - `W25N01GVSFIG-storage-driver` contains the driver for the W25N01GVSFIG chip
