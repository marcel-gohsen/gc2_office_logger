#!/bin/bash

export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:.
gnome-terminal -- sh -c "echo \"Start OfficeLogger...\";sleep 2s;"
./OfficeLogger
