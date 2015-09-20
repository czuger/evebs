namespace :data_compute do
  namespace :get_price_history do

    desc "Retrieve prices history"
    task :update => :environment do
      puts 'About to prices history'
      Crest::GetPriceHistory.new
    end

    desc "Retrieve prices history (first time)"
    task :init => :environment do
      puts 'About to prices history'
      Crest::GetPriceHistory.new(true)
    end

  end
end