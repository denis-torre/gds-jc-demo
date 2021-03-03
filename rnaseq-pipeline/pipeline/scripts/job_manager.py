#################################################################
#################################################################
############### LSF Job Manager
#################################################################
#################################################################
##### Author: Denis Torre
##### Icahn School of Medicine at Mount Sinai

#############################################
########## 1. Default options
#############################################
# Packages
import os, time, pathlib
from datetime import datetime
import numpy as np

#############################################
########## 2. Run job
#############################################
# Function to submit jobs using LSF
def run_job(cmd_str, outfile, modules=[], conda_env=False, workdir=os.getcwd(), P='acc_GuccioneLab', q='express', W='00:30', R='rusage[mem=2000]', n='1', GB=None, print_cmd=False, print_outfile=False, run_locally=False, ow=False, mkdir=False, stdout=None, stderr=None, lsf=None, jobname=None, wait=False):

    # Print
    if print_cmd:
        # print(cmd_str.replace('		', '\n	'))
        print(cmd_str.replace('  ', '').replace('	', ''))
    elif print_outfile:
        print(outfile)
    else:

        # Job and log names
        now = datetime.now().strftime("%Y%m%d_%H%M%S.%f")[:-3]
        outbase = os.path.basename(outfile) if not jobname else jobname
        job_name = '{now}_{outbase}'.format(**locals())+'-job'

        # Add memory - either specified by R (default) or GB (automatically includes integer GB and adds span ptile based on n)
        R_value = '"rusage[mem={GB}000] span[hosts=1]"'.format(**locals()) if GB else '\"'+R+'\"'

        # Output files
        stdout = 'pipeline/logs/{job_name}/{job_name}.stdout'.format(**locals()) if not stdout else stdout
        stderr = 'pipeline/logs/{job_name}/{job_name}.stderr'.format(**locals()) if not stderr else stderr

        # Update job options
        job_options = {
            'P': P,
            'q': q,
            'W': W,
            'R': R_value,
            'n': n,
            'J': job_name,
            'o': stdout,
            'eo': stderr
        }

        ### NEW
        # 1. Initialize list
        lsf_list = ['#!/bin/bash']

        # 2. Add job options
        for key, value in job_options.items():
            lsf_list.append('#BSUB -{key} {value}'.format(**locals()))

        # 3. Add workdir
        lsf_list.append('')
        lsf_list.append('cd {workdir}'.format(**locals()))

        # 4. Conda environment
        if conda_env:
            lsf_list.append('deactivate && module purge && source /hpc/packages/minerva-centos7/anaconda3/2018.12/etc/profile.d/conda.sh && conda activate {conda_env}'.format(**locals()))
            lsf_list.append('')

        # 5. Add module load
        if len(modules):
            modules_str = ' '.join(modules)
            lsf_list.append('module load {modules_str}'.format(**locals()))
            lsf_list.append('')

        # 6. Add command
        lsf_list.append(cmd_str.strip())

        # 7. Add module unload
        if len(modules):
            lsf_list.append('')
            lsf_list.append('module unload {modules_str}'.format(**locals()))

        # 8. Join
        lsf_list.append('')
        lsf_string = '\n'.join(lsf_list)

        # Print
        lsf_name = 'pipeline/logs/{job_name}/{job_name}.lsf'.format(**locals()) if not lsf else lsf

        # Make dir
        if mkdir:
            outdir = os.path.dirname(outfile)
            if not os.path.exists(outdir):
                pathlib.Path(outdir).mkdir(parents=True)

        # Submit
        if os.path.exists(outfile) and ow==False:
            print('Output file {outfile} already exists, not running job.'.format(**locals()))
        else:
            if run_locally == True:
                # print('Doing {}...'.format(outfile))
                os.system(cmd_str)
            else:
                time.sleep(0.03)

                # Create log directory
                os.makedirs(os.path.dirname(lsf_name))

                # Write file
                with open(lsf_name, 'w') as openfile:
                    openfile.write(lsf_string)

                # Execute
                output = os.popen('bsub < {lsf_name};'.format(**locals())).read() # old
                
                print('\n### Ruffus job {job_name} - {output}'.format(**locals()))

                # Wait
                if wait == True:

                    # Initialize job status
                    job_status = None

                    # Check completion
                    while not os.path.exists(stdout):

                        # Wait
                        time.sleep(10)

                        # Check job status
                        updated_job_status = os.popen('bjobs -o "job_name stat" | grep {job_name} | cut -f2 -d " "'.format(**locals())).read().strip()

                        # Print change
                        if job_status != updated_job_status and updated_job_status:
                            print('### Ruffus job {job_name} - {updated_job_status}'.format(**locals()))
                            job_status = updated_job_status

                    # Get job status
                    exit_status = os.popen('grep -e "Resource" -B 2 {stdout} | head -n1'.format(**locals())).read().strip()
                    print('### Ruffus job {job_name} - {exit_status} ({stdout}).'.format(**locals()))

#############################################
########## 2. Run R script
#############################################
# Function to submit R jobs using LSF

def run_r_job(func_name, func_input, outfile, r_source, additional_params=None, **kwargs):

    # Process input
    if isinstance(func_input, list) or isinstance(func_input, tuple):
        func_input = ','.join(func_input)

    # Process additional params
    if isinstance(additional_params, list) or isinstance(additional_params, tuple):
        additional_params = ','.join([str(x) for x in additional_params])

    # Command
    cmd_str = """Rscript /hpc/users/torred23/pipelines/support/run.R --func_name={func_name} --r_source={r_source} --func_input="{func_input}" --outfile={outfile}""".format(**locals())

    # Additional parameters
    if additional_params:
        cmd_str = '{cmd_str} --additional_params="{additional_params}"'.format(**locals())

    # Add ;
    cmd_str += ';'

    # Run
    run_job(cmd_str, outfile, **kwargs)
