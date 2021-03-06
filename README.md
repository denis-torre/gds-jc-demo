# GDS JC 04/03 - Interactive Demo
The tutorial consists of the following steps:
1. [Access Minerva using Visual Studio Code](#part-1-access-minerva-using-visual-studio-code) (https://code.visualstudio.com/)
2. [Clone this GitHub repository to your directory](#part-2-clone-this-github-repository-to-your-directory) (https://github.com/denis-torre/gds-jc-demo)
3. [Run a sample RNA-Seq pipeline built using ruffus](#part-3-run-a-sample-rna-seq-pipeline-built-using-ruffus) (https://cgat-ruffus.readthedocs.io/en/latest/)

Full presentation available at https://docs.google.com/presentation/d/1nOn15aq2bRukDW6HVWAKCvYJutviG01JTg5_fZQERVI/edit?usp=sharing

## Part 1. Access Minerva using Visual Studio Code
1. Download Visual Studio Code at https://code.visualstudio.com/Download
2. Open Visual Studio Code and access the "Extensions" tab on the left

![image](images/vscode.png)

3. Install the Remote SSH extension (also available at https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh)

![image](images/remote-ssh.png)

4. Open the Manage tab (click on the gear at the bottom left) and select "Command Palette"

![image](images/command-palette-1.png)

5. Search "Connect to Host" and select either option (use current or new window)

![image](images/ssh-connect-1.png)

6. If "chimera.hpc.mssm.edu" or "minerva.hpc.mssm.edu" are available, select either one (whichever you normally use - they are stored in your local ssh config).

![image](images/ssh-connect-2.png)

If these are not available, select "Add New SSH Host..." and enter the ssh command as you would using Terminal (e.g. `ssh YOUR_USERNAME@chimera.hpc.mssm.edu`):

![image](images/ssh-connect-3.png)

Enter your password followed by your VIP code, as with logging in via Terminal.

7. You are now connected to Minerva through SSH. To better interact with the filesystem, click on "Open folder..." to open a desired directory (e.g. your work folder `/sc/arion/work/YOUR_USERNAME`).

![image](images/vscode-minerva-1.png)

8. You can now interact with the file system using the File Explorer on the left.

![image](images/vscode-minerva-2.png)

9. Finally, select View > Open Terminal from the top menu. The terminal is connected to Minerva and can be used to run code, load modules, etc.

![image](images/vscode-minerva-3.png)

## Part 2. Clone this GitHub repository to your directory

1. Open the Manage tab (click on the gear at the bottom left) and select "Command Palette"

![image](images/command-palette-2.png)

2. Search "Git Clone":

![image](images/git-clone-1.png)

3. Insert the path of this GitHub repository (https://github.com/denis-torre/gds-jc-demo), select "Clone from URL", and choose a directory to download it in (e.g. your work folder `/sc/arion/work/YOUR_USERNAME`).

![image](images/git-clone-2.png)

4. Open the cloned repository (if the prompt below does not appear, select "File > Open" and insert the path to the repository):

![image](images/git-open.png)

5. You can now explore the repository using the file explorer. Open the `rnaseq-pipeline/pipeline/pipeline-rnaseq.py` file to explore the main pipeline structure.

![image](images/git-repo.png)

## Part 3. Run a sample RNA-Seq pipeline built using ruffus

The `rnaseq-pipeline` directory contains a basic RNA-Seq analysis pipeline built using Ruffus. The pipeline begins with a sample text file with gene counts (`counts.tsv`), runs a simple differential expression analysis across different comparisons, and generates some plots to display the results.


Here is a schematic representation of the workflow:

![image](images/pipeline-workflow.png)

In order to run the pipeline, the following steps need to be performed.

1. Using the terminal, change your working directory to `rnaseq-pipeline` using `cd rnaseq-pipeline` (or other command depending on your current directory). If your terminal is not open, select View > Terminal from the top menu.
 
![image](images/pipeline-1.png)

2. Load the default R and Python modules:

```
module load R
module load python
```

3. Run the pipeline using the command below. The `--target_tasks` option allows to specify the name of the function to run. NOTE: make sure you are in the correct directory (e.g. `/sc/arion/work/YOUR_USERNAME/gds-jc-demo/rnaseq-pipeline`)

```
python pipeline/pipeline-rnaseq.py --target_tasks plotVennDiagram
```

Here, we specify the name of the last function in the pipeline (`plotVennDiagram`). Ruffus will automatically run all previous functions in the pipeline and save the output in the `rnaseq-pipeline/data` directory. Alternatively, each step can be run individually by specifying each function's name using the `--target_tasks` parameter.

4. Explore the results in the `rnaseq-pipeline/data` directory. VS Code can display images and PDF files directly from within the interface, with no need to copy them to your local machine ([vscode-pdf](https://marketplace.visualstudio.com/items?itemName=tomoki1207.pdf) extension is required for viewing PDFs).

![image](images/volcano-plot.png)

5. Using the [GitLens extension](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens), the entire history of the repository can be interactively explored directly through Visual Studio Code (Note: this currently does not work on Minerva, as the default git version installed is outdated. The screenshot below was taken from a local session.)

![image](images/gitlens.png)