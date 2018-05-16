desc 'Print time for logs'
task :print_time => :environment do
  Banner.p( DateTime.now.strftime('%c') )
end
