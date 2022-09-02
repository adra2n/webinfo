import subprocess

def subExec(cmdline):
    cmd_proc = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    cmd_proc.wait()
    process_output = cmd_proc.stdout.read()
    # print '\n'.join(process_output)
    # print(process_output.decode())
    return process_output.decode()