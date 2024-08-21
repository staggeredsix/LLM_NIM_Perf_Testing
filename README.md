# LLM_NIM_Perf_Testing
Basic LLM NVIDIA NIM performance testing automation.

---------------------------------------------------------------------------------------------------------------------

Project Overview:

This project provides tools for deploying and testing NVIDIA Inference Models (NIMs) in a Docker environment. This only applies to LLM NIMs.

The project consists of several Python scripts that automate the installation of necessary dependencies, the deployment and testing of NIMs, and the generation of performance charts.

Files Included
nim_testing.py: Main script for deploying and testing NIMs.

performance_test.py: Script that handles performance testing of deployed NIMs.

chart_generation.py: Generates performance charts based on test results.

requirements_install.py: Installs necessary dependencies including Docker, NVIDIA Container Toolkit, NVIDIA NGC CLI, and Python packages.

requirements.txt: Lists all required Python packages for the scripts.

README.txt: This documentation file.

nim_list.txt: Stores the list of available NIMs for testing.

ngc_api_key.enc: Stores the encrypted NGC API key (generated when the key is entered).

All tests are stored in backend/tests/ and are broken up into modules. They should be easy to modify/review.

Yes - the script asks you to kill containers when you launch and when you exit. This is to ensure the system is clean before and after running a test.

---------------------------------------------------------------------------------------------------------------------

Usage
1. Install Required Software and Python Packages
Before running any tests or deployments, ensure that all required software and Python packages are installed.

Open a terminal in the directory containing nim_testing.py.
Run the installation script:

python3 requirements_install.py

This script will install Docker, NVIDIA Container Toolkit, NVIDIA NGC CLI, and the necessary Python packages. It will also add your user to the Docker group.

Log into nvcr.io using your NGC API key : docker login nvcr.io $oauthtoken yourapikey

2. Running NIM Tests

To deploy and test NIMs:

Run the main testing script:

python3 nim_testing.py

Follow the prompts to:

Select the number of GPUs to use.

Choose the number of requests to send (default is 10).

Select whether to run tests on all NIMs or a specific NIM.

Review and confirm the Docker command before proceeding.

3. Generating Performance Charts:

After running tests, you can generate performance charts by selecting the relevant option in nim_testing.py or by running:


python3 chart_generation.py
The charts will be saved in the same directory as nim_testing.py and will be based on the logs generated during the tests.


---------------------------------------------------------------------------------------------------------------------

Configuration and Editing
1. Adding New NIMs Manually
To add new NIMs without running the script:

Open the nim_list.txt file in a text editor.
Add a new line for each NIM in the following format:

<NIM Name>|<Docker Image>
Example:

Mistral 7B Instruct|nvcr.io/nim/mistralai/mistral-7b-instruct-v03:latest

2. Editing Python Scripts

Docker Image Paths: Modify paths or configurations in nim_testing.py or nim_list.txt.

Performance Metrics: Adjust how performance is measured in performance_test.py.

Chart Generation: Customize chart appearance and data processing in chart_generation.py.

4. API Key Management
The NGC API key is stored in the same directory as nim_testing.py in an encrypted file named ngc_api_key.enc. The key is encrypted upon entry, and you will be prompted to enter a password to decrypt it when needed.

To change the API key:

Delete the existing ngc_api_key.enc file.
Run nim_testing.py and enter the new API key when prompted.

---------------------------------------------------------------------------------------------------------------------

Troubleshooting:

Common Issues
Docker Permission Errors: Ensure you have logged out and back in after the installation process to apply Docker group changes.
Missing Python 3: If Python 3 is not installed, the script will prompt you to install it.
Graph creation is likely broken, logging works.

KNOWN ISSUES : requirements installation script is probably still broken, some updates were made.

