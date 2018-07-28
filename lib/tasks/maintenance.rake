namespace :maintenance do
  desc 'Delete users without character'
  task :delete_users_without_characters => :environment do
    User.where( current_character_id: nil ).destroy_all
  end

  desc 'Test computed volumes precision'
  task :test_monthly_volume_in_jita => :environment do
    Esi::JitaVolumeVerification.new.check
  end

end

