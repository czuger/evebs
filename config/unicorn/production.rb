# Set the working application directory
# working_directory '/path/to/your/app'
working_directory '/var/www/eve_business_server/current'

# Unicorn PID file location
# pid '/path/to/pids/unicorn.pid'
pid '/var/www/eve_business_server/current/pids/unicorn.pid'

# Path to logs
# stderr_path '/path/to/log/unicorn.log'
# stdout_path '/path/to/log/unicorn.log'
stderr_path '/var/www/eve_business_server/current/log/unicorn.err'
stdout_path '/var/www/eve_business_server/current/log/unicorn.log'

# Unicorn socket
listen '/tmp/unicorn.eve-business-server.deadzed.net.sock'

# Number of processes
# worker_processes 4
worker_processes 1

# Time-out
timeout 30