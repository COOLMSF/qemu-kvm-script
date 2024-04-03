import sys, os
import subprocess
import json

def main():
    if len(sys.argv) != 2:
        print("Usage: append_dns.py <domain list>")
        sys.exit(1)
    domain = sys.argv[1]
    with open(domain, "r") as f:
        lines = f.readlines()
        cnt = 0
        for line in lines:
            # name error, ignore
            if len(line) < 3:
                continue
            cmd_get_domid = "virsh domid " + line.strip()
            domid = subprocess.run(cmd_get_domid, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.strip()
            domid = domid.decode()
            print("=======================================================")
            print("now handling:" + line.strip() + " domid:" + domid)

            # The command template with placeholders for the domain ID and JSON payload
            cmd_template_sysconfig = 'virsh qemu-agent-command {} --cmd \'{}\''
            
            # append dns to sysconfig
            json_payload_sysconfig = {
                "execute": "guest-exec",
                "arguments": {
                    "path": "bash",
                    # Need to modify depend on your interface
                    # you mey need to modify DNS server
                    "arg": ["-c", r"echo DNS1=114.114.114.114 DNS2=8.8.8.8 DNS3=1.1.1.1 | tee -a /etc/sysconfig/network-scripts/ifcfg-eth0"]
                }
            }

            # append dns to resolv.conf
            # you may need to modify nameserver
            json_payload_resolv = {
                "execute": "guest-exec",
                "arguments": {
                    "path": "bash",
                    "arg": ["-c", r'echo -e \"nameserver 114.114.114.114 nameserver 8.8.8.8 nameserver 1.1.1.1\" | tee -a /etc/resolv.conf']
                }
            }
            
            # Convert the JSON payload to a string
            json_str_sysconfig = json.dumps(json_payload_sysconfig)
            json_str_resolv = json.dumps(json_payload_resolv)
            
            # Use the format method to insert the domain ID and JSON payload into the command template
            cmd_append_dns_sysconfig = cmd_template_sysconfig.format(domid, json_str_sysconfig)
            cmd_append_dns_resolv = cmd_template_sysconfig.format(domid, json_str_resolv)
            
            # do appending dns to sysconfig
            print("now appending dns to sysconfig:" + line.strip())
            print(cmd_append_dns_sysconfig)
            result = subprocess.run(cmd_append_dns_sysconfig, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("result:")
            print(result.stdout.strip(), result.stderr.strip())

            # do appending dns to resolv.conf
            print("now appending dns to resolv.conf:" + line.strip())
            print(cmd_append_dns_resolv)
            result = subprocess.run(cmd_append_dns_resolv, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("result:")
            print(result.stdout.strip(), result.stderr.strip())

            cnt += 1

            print("=======================================================")
        print("total domain:" + str(cnt))

if __name__ == "__main__":
    main()


