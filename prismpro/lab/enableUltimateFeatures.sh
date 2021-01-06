#!/usr/bin/expect -f
set timeout 60

set PC_IP [lindex $argv 0];
set PC_USER [lindex $argv 1];
set PC_PASS [lindex $argv 2];
set PE_IP [lindex $argv 3];
set PE_USER [lindex $argv 4];
set PE_PASS [lindex $argv 5];

# Note: Due to ENG-344699 we cannot call v4 APIs within the Prism Central
# So we will copy our script to the PE and run it from there.
spawn bash -c "scp enable_services.py $PE_USER@$PE_IP:~/tmp/enable_services.py"
expect {
  -re ".*es.*o.*" {
    exp_send "yes\r"
    exp_continue
  }
  -re ".*sword.*" {
    exp_send "$PE_PASS\r"
  }
}
interact

# sshpass -p "$sshPass" scp enable_services.py $sshUserName@$PE_IP:~/tmp/enable_services.py
spawn ssh -o StrictHostKeyChecking=no $PE_USER@$PE_IP
expect {
  -re ".*es.*o.*" {
    exp_send "yes\r"
    exp_continue
  }
  -re ".*sword.*" {
    exp_send "$PE_PASS\r"
  }
}
sleep 20
send "cd tmp; python enable_services.py $PC_IP $PC_USER $PC_PASS\r"
sleep 20
send "exit\r"
# sshpass -p "$sshPass" ssh -o "StrictHostKeyChecking=no" $sshUserName@$PE_IP "cd tmp; python enable_services.py $PC_IP $PC_USER $PC_PASS"

# Once the above workaround is no longer needed the following line can be uncommented
# python enable_services.py $PC_IP $PC_USER $PC_PASS
