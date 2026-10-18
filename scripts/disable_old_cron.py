import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.1.143', username='robot', password='10112003', timeout=5)

stdin, stdout, stderr = c.exec_command('crontab -l')
current_cron = stdout.read().decode()

new_cron_lines = []
for line in current_cron.splitlines():
    if "/home/robot/heliosis.xyz/run_update.sh" in line and not line.strip().startswith("#"):
        new_cron_lines.append("# [DEAKTIF - IPTV PORTALI YAPILDI] " + line)
    else:
        new_cron_lines.append(line)

new_cron = "\n".join(new_cron_lines) + "\n"

stdin, stdout, stderr = c.exec_command("crontab -")
stdin.write(new_cron)
stdin.flush()
stdin.channel.shutdown_write()

print("Status code:", stdout.channel.recv_exit_status())
print("Updated crontab successfully.")

stdin, stdout, stderr = c.exec_command('crontab -l | grep heliosis.xyz')
print("Active lines in crontab:", stdout.read().decode())
c.close()
