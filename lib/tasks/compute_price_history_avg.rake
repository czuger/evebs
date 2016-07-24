namespace :data_compute do

  desc "Compute prices history average"
  task :compute_prices_history_average => :environment do

    puts 'Recomputing prices history average'

    Crest::ComputePriceHistoryAvg.new

    puts 'End of recomputing prices history average'
  end

end