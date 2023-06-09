#!/bin/bash
set -e
echo "System update"
paru
read -rsn1 -p "Press any key to continue."
sudo checkservices
rm /tmp/updates.lck
