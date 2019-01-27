namespace :maintenance do
  desc 'Delete users without character'
  task :delete_users_without_characters => :environment do
    User.where( current_character_id: nil ).destroy_all
  end

  desc 'Test computed volumes precision'
  task :test_monthly_volume_in_jita => :environment do
    Esi::JitaVolumeVerification.new.check
  end

  desc 'Check working hourly process'
  task :check_working_hourly_process => :environment do
    if Misc::LastUpdate.where( update_type: 'hourly' ).first.updated_at < DateTime.now - 1/24.0


      config = YAML.load_file('config/mail_user_data.yml')
      LoadErrorMailer.with(user: config[:user]).send_error.deliver_now
    end
  end

end

