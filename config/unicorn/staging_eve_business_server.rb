# Set the working application directory
# working_directory '/path/to/your/app'
working_directory '/var/www/eve_business_server_staging/current'

# Unicorn PID file location
# pid '/path/to/pids/unicorn.pid'
pid '/var/www/eve_business_server_staging/current/tmp/pids/unicorn.pid'

# Path to logs
# stderr_path '/path/to/log/unicorn.log'
# stdout_path '/path/to/log/unicorn.log'
stderr_path '/var/www/eve_business_server_staging/current/log/unicorn.err'
stdout_path '/var/www/eve_business_server_staging/current/log/unicorn.log'

# Unicorn socket
listen '/var/www/eve_business_server_staging/current/tmp/sockets/unicorn.sock'

# Number of processes
# worker_processes 4
worker_processes 1

# Time-out
timeout 30