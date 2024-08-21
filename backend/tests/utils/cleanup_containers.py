import subprocess

def cleanup_containers():
    subprocess.run("docker stop $(docker ps -q)", shell=True)
    subprocess.run("docker rm $(docker ps -a -q)", shell=True)
    subprocess.run("docker container prune -f", shell=True)

