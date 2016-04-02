import paramiko
import logging


# C is for 'constants' "... and that's good enough for me."
class C(object): 
  USERNAME_INDEX = 0
  PASSWORD_INDEX = 1

  #COMMAND_SENT = 'CommandSent'
  COMMAND = 'command'
  STANDARD_OUT = 'standardOut'
  STANDARD_ERROR = 'standardError'
  EXIT_CODE = 'exitCode'


_long_version_warning = '''--- WARNING!!! ---: you are using an old version of the paramiko library. If SshIt actually works,
then your SSH daemons are likely woefully out of date and can probably be targeted by some very nasty security bugs.
if SshIt didn't work, update to at least v1.15. SshIt was developed using paramiko v1.15.1'''

if float('.'.join(paramiko.__version__.split('.')[:2])) < 1.15:
  logging.warn(_long_version_warning)

# TODO: accept RSA keys.
# TODO: Threaded version of this function.
# TODO: add the logic for "continue_on_..." vars.
def exec_commands(host_config, commands, continue_on_ssh_error=True, continue_on_command_error=True):
  '''
  dict:host_config: Dictionary where the key is a valid hostname and the value is username/password pair
                    example: {'localhost':('username','watermeloncat')}
  iterable:commands: A list, tuple, or other iterable containing strings of the commands to run 
                    example: ['ls -lah', 'find / -exec "cat /dev/null > {};" # DO NOT USE THIS EXAMPLE']
  bool:continue_on_ssh_error: When true (default), processing of the hosts/commands will continue.
                              When false, all work will stop and an error will be raised.
  bool:continue_on_command_error: When true (default), SshIt will disregard the exit codes of the commands being run. 
                                  When false, processing will cease when an exit code other than zero is seen.
  '''
  result = {}
  for host,creds in host_config.items():
    result_part = []

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=creds[C.USERNAME_INDEX], password=creds[C.PASSWORD_INDEX])
    for command in commands:
      stdin,stdout,stderr = ssh.exec_command(command)
      result_part.append({C.COMMAND:command, C.STANDARD_OUT:stdout.read(), C.STANDARD_ERROR:stderr.read(), C.EXIT_CODE:stdout.channel.recv_exit_status()})

    result.update({host:result_part})
    ssh.close()
  return result
