class Crontab < ApplicationRecord

  def self.start( cron_name )
    r = Crontab.where( cron_name: cron_name ).first_or_create!
    exit if r.status
    r.update!( status: true )
  end

  def self.start( cron_name )
    r = Crontab.where( cron_name: cron_name ).update_all( status: false )
  end

end
