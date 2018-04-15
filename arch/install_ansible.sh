ssh ubuntu@$1 "sudo apt-add-repository ppa:ansible/ansible;sudo apt-get -o Acquire::ForceIPv4=true  update;sudo apt-get install ansible -y;"
