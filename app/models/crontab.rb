class Crontab < ApplicationRecord

  def self.start( cron_name )
    r = Crontab.where( cron_name: cron_name ).first_or_create!

    if r.status
      Banner.p 'Process actually running. Exiting'
      exit
    end

    r.update!( status: true )
  end

  def self.stop( cron_name )
    Crontab.where( cron_name: cron_name ).update_all( status: false )
  end

end
