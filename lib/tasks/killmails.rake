namespace :killmails do

  desc 'Update killmails data'
  task :update => :environment do
    Killmails::CheckKillmails.new.update
  end

  desc 'Check solo'
  task :check_solo => :environment do
    Killmails::SoloHunter.new.show
  end

  desc 'Check individuals and systems'
  task :check_individuals_and_systems => [ :environment ] do
    Killmails::CheckIndividualsAndSystems.new.find_individuals
    # Killmails::CheckIndividualsAndSystems.new.check_systems
  end

end