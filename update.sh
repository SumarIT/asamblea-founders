#!/bin/sh 
# Script para bajar datos y actualizar el repo

while true  
do  
    python main.py
    git add .
    git commit -m "Actualización automática"
    git push
    echo "waiting..."
    sleep 3660
done
