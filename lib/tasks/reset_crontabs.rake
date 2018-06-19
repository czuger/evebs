namespace :crontabs do
  desc 'Reset crontabs'
  task :reset => :environment do
    Crontab.update_all( status: false  )
  end
end

