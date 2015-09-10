namespace :data_compute do

  desc "Retrieve prices history"
  task :get_prices_history => :environment do

    puts 'About to prices history'

    r=Region.find(158)
    Crest::GetPriceHistory.new.get_region_history( r )

  end

end