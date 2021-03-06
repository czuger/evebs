module Misc
  class Crontab < ApplicationRecord

    def self.start( cron_name )

      # Skip it in development.
      return if Rails.env.development?

      r = Crontab.where( cron_name: cron_name ).first_or_create!

      if r.status
        Misc::Banner.p 'Process actually running. Exiting'
        exit
      end

      r.update!( status: true, updated_at: Time.now )
    end

    def self.stop( cron_name )
      Crontab.where( cron_name: cron_name ).update_all( status: false, updated_at: Time.now )
    end

  end
end