import os
from cli import parse_args
from downloader import download_file, get_java_download_url, download_and_extract_java, get_vanilla_download_url
from server import run_server, configure_server_properties, generate_start_script, find_java_executable
from utils import confirm_action, get_operating_system, check_java, accept_eula

def main():
    args = parse_args()
    
    operating_system = get_operating_system()
    
    print("Minecraft Server Management Tool")
    print(f"Operating System: {operating_system}")
    print(f"Server Type: {args.server_type}")
    print(f"Server Version: {args.server_version}")
    
    java_executable = "java"
    java_status = check_java()
    if java_status == "abort":
        return
    elif java_status == "download":
        java_version = input("Enter the Java version to download (e.g., 17, 18): ")
        if not confirm_action(f"Do you want to download Java version {java_version}?"):
            return
        java_download_url = get_java_download_url(java_version, operating_system)
        if java_download_url:
            java_dir = download_and_extract_java(java_download_url, java_version)
            if java_dir:
                java_executable = find_java_executable(java_dir)
                if not java_executable:
                    print("Could not find java executable in the downloaded JDK.")
                    return
        else:
            print("Could not find a download for the specified Java version.")
            return

    server_dir = f"mc-server-{args.server_version}"
    if args.server_type == "vanilla":
        if not confirm_action(f"Do you want to download the vanilla Minecraft server version {args.server_version}?"):
            return
        download_url = get_vanilla_download_url(args.server_version)
        if download_url:
            os.makedirs(server_dir, exist_ok=True)
            server_jar_path = os.path.join(server_dir, "server.jar")
            if download_file(download_url, server_jar_path):
                if not confirm_action("Do you want to run the server to generate initial files?"):
                    return
                run_server(server_dir, java_executable=java_executable, xmx=args.xmx, xms=args.xms)
                accept_eula(server_dir)
                configure_server_properties(server_dir)
                generate_start_script(server_dir, operating_system, java_executable=java_executable, xmx=args.xmx, xms=args.xms)

    elif args.server_type == "plugins":
        print("Plugin server download not implemented yet.")
    elif args.server_type == "mods":
        print("Modded server download not implemented yet.")

if __name__ == "__main__":
    main()
