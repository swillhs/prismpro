#!/bin/bash
#!/usr/bin/expect -f
set -x

PC_IP="$1"
PC_USER="$2"
PC_PASS="$3"
PE_IP="$4"
PE_SSH_USER="$5"
PE_SSH_PASS="$6"

echo "Enabling App Discovery and VCenter Monitoring Services"
./enableUltimateFeatures.sh $PC_IP $PC_USER $PC_PASS $PE_IP $PE_SSH_USER $PE_SSH_PASS

echo "Creating cron job for capacity"

( crontab -l 2>/dev/null; echo '@hourly /usr/bin/timeout 1h bash -lc "cd /home/nutanix/lab/capacity_data/;python capacity_prismpro_write.py" > /tmp/debug.log' ) | crontab -
crontab -l

cd capacity_data

echo 'Writing VMBL Data'
# Write VBML data to IDF
python xfit_prismpro_write.py

cd ../

echo "Seeding Application Discovery Data"

cp mock_epoch_response.json ~/config/xdiscovery/mock_epoch_response.json
genesis stop dpm_server
genesis stop xdiscovery
cluster start
sudo systemctl start iptables

# ~~~ Comment out until vCenter is supported for bootcamps ~~~
# echo "Registering vCenter Cluster"
# python vcenter_con.py $PC_IP $PC_USER $PC_PASS

# ~~~ BEGIN Comment out for Automatically Register PP Cluster ~~~
# We don't automatically register PP Cluster because the PP cluster prevents users from being able to upgrade their PCs.
# We will have the webserver do this.
# Note that for other setups like Test Drive the below portion would be needed

# echo "Registering the Prism Pro Cluster"

# # Register the PE
# python create_zeus_entity.py $PC_IP 00057d50-00df-b390-0000-00000000eafd Prism-Pro-Cluster
# sleep 60

# # Check that Prism-Pro-Cluster exists in clusters/list, if not, run the create_zeus_entity.py command again

# echo "Checking that Prism-Pro-Cluster exists"

# /bin/bash verify_init.sh $PC_IP > /home/nutanix/verify_init.log 2>&1
# ~~~ END Comment out for Automatically Register PP Cluster ~~~
