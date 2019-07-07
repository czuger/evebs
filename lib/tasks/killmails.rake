namespace :killmails do

  desc 'Update killmails data'
  task :update => :environment do
    Killmails::CheckKillmails.new.update
  end

  desc 'Check solo'
  task :check_solo => :environment do
    Killmails::SoloHunter.new.show
  end

end