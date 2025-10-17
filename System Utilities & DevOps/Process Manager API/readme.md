we often need to programmatically manage services and processes, like:
Starting multiple background scripts automatically.
Stopping them safely.
Monitoring which scripts are running.
This code is a minimal version of a process manager that can later be extended with:
Logging stdout/stderr to files.
Auto-restart if a process dies.
Scheduling.
Web interface.


Use Commads : 
python cli_manager.py start "notepad.exe"
python cli_manager.py list

python cli_manager.py stop <pid>
