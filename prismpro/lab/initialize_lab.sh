#!/bin/bash
set -x

PC_IP="$1"

echo "Creating cron job for capacity"

( crontab -l 2>/dev/null; echo '@hourly /usr/bin/timeout 1h bash -lc "cd /home/nutanix/lab/capacity_data/;python capacity_prismpro_write.py" > /tmp/debug.log' ) | crontab -
crontab -l

cd capacity_data

echo 'Writing VMBL Data'
# Write VBML data to IDF
python xfit_prismpro_write.py

cd ../

# Register the PE
python create_zeus_entity.py $PC_IP 00057d50-00df-b390-0000-00000000eafd Prism-Pro-Cluster
sleep 60

# Check that Prism-Pro-Cluster exists in clusters/list, if not, run the create_zeus_entity.py command again

echo "Checking that Prism-Pro-Cluster exists"

/bin/bash verify_init.sh $PC_IP > /home/nutanix/verify_init.log 2>&1
