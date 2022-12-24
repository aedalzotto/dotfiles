#!/bin/bash
set -e
echo "System update"
paru
read -rsn1 -p "Press any key to continue."
rm /tmp/updates.lck
