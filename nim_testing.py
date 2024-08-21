def menu():
    # Get the directory where nim_testing.py resides
    script_dir = os.path.dirname(os.path.abspath(__file__))

    nim_file = os.path.join(script_dir, "nim_list.txt")
    api_key_file = os.path.join(script_dir, "ngc_api_key.enc")  # Store API key in the same directory as nim_testing.py
    local_nim_cache = os.path.expanduser("~/.cache/nim")
    output_dir = os.path.join(script_dir, "performance_results")

    os.makedirs(local_nim_cache, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # Prompt for the API key decryption
    print("Enter Password for API Key Decryption")
    api_key = read_api_key(api_key_file)

    # Set the API key as an environment variable
    os.environ["NGC_API_KEY"] = api_key

    options = ["Run tests against all NIMs", "Run test against a specific NIM", "Add a new NIM", "Quit"]
    while True:
        print("Select an option:")
        for i, opt in enumerate(options, 1):
            print(f"{i}. {opt}")
        choice = int(input("Enter your choice: "))

        if choice == 1:
            gpus = int(input("Enter the number of GPUs to use: "))
            request_count = input("Enter the number of requests to send (press Enter to use default of 10): ")
            request_count = int(request_count) if request_count else 10

            if os.path.exists(nim_file):
                with open(nim_file, "r") as f:
                    for line in f:
                        model, img_name = line.strip().split("|", 1)
                        img_name = img_name.strip()  # Remove any leading/trailing whitespace
                        logging.info(f"Prepared Docker command for NIM: {model}")
                        logging.info(f"Docker image: {img_name.lower()}")
                        confirm_run = input(f"Proceed with running {model} using image {img_name.lower()}? (y/n): ").strip().lower()
                        if confirm_run == 'y':
                            run_test(img_name.lower(), gpus, os.environ["NGC_API_KEY"], local_nim_cache, output_dir, request_count)

                            # Ask if the user wants to run Phase 1
                            run_phase1 = input("Do you want to run sequential and concurrent tests without streaming tokens? (y/n): ").strip().lower()
                            if run_phase1 == 'y':
                                run_test_phase1(model_name, request_count, log_file)

                            # Ask if the user wants to run the stress test
                            run_stress_test = input("Do you want to run a stress test to see how many concurrent requests your system can handle? This will test until the model is outputting 10 tokens per second. It may KILL your GPU because of the amount of load. Do this only if you are okay with murdering hardware. (y/n): ").strip().lower()
                            if run_stress_test == 'y':
                                run_stress_test_phase(model_name, log_file, request_count, max_processes, log_filename)
                        else:
                            logging.info("User cancelled the operation.")
        elif choice == 2:
            list_nims(nim_file)
            nim_number = int(input("Enter the NIM number: "))
            gpus = int(input("Enter the number of GPUs to use: "))
            request_count = input("Enter the number of requests to send (press Enter to use default of 10): ")
            request_count = int(request_count) if request_count else 10

            with open(nim_file, "r") as f:
                model_img = f.readlines()[nim_number - 1].strip()
                model, img_name = model_img.split("|", 1)
                img_name = img_name.strip()  # Remove any leading/trailing whitespace
                logging.info(f"Prepared Docker command for NIM: {model}")
                logging.info(f"Docker image: {img_name.lower()}")
                confirm_run = input(f"Proceed with running {model} using image {img_name.lower()}? (y/n): ").strip().lower()
                if confirm_run == 'y':
                    run_test(img_name.lower(), gpus, os.environ["NGC_API_KEY"], local_nim_cache, output_dir, request_count)

                    # Ask if the user wants to run Phase 1
                    run_phase1 = input("Do you want to run sequential and concurrent tests without streaming tokens? (y/n): ").strip().lower()
                    if run_phase1 == 'y':
                        run_test_phase1(model_name, request_count, log_file)

                    # Ask if the user wants to run the stress test
                    run_stress_test = input("Do you want to run a stress test to see how many concurrent requests your system can handle? This will test until the model is outputting 10 tokens per second. It may KILL your GPU because of the amount of load. Do this only if you are okay with murdering hardware. (y/n): ").strip().lower()
                    if run_stress_test == 'y':
                        run_stress_test_phase(model_name, log_file, request_count, max_processes, log_filename)
                else:
                    logging.info("User cancelled the operation.")
        elif choice == 3:
            add_nim(nim_file)
        elif choice == 4:
            kill_all_containers()  # Prompt to kill all containers before quitting
            break
        else:
            logging.info("Invalid option.")

