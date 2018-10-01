namespace :crontabs do
  desc 'Reset crontabs'
  task :reset => :environment do
    Misc::Crontab.update_all( status: false  )
  end
end

