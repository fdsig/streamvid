import subprocess
import os
def run_bash_script(script_name):
    with open('output.log', 'w') as f:
        try:
            process = subprocess.Popen(['bash', script_name],stdout=f,stderr=f, start_new_session=True,env=os.environ.copy())
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running the script: {e}")
        

if __name__ == '__main__':
    print("Starting bash script...")
    run_bash_script('producer.sh')


    print("Bash script finished.")

