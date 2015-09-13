namespace :data_compute do

  desc "Retrieve prices history"
  task :get_prices_history_update => :environment do
    puts 'About to prices history'
    Crest::GetPriceHistory.new
  end

  desc "Retrieve prices history (first time)"
  task :get_prices_history_init => :environment do
    puts 'About to prices history'
    Crest::GetPriceHistory.new(true)
  end

end