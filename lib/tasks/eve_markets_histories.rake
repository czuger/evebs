namespace :data_compute do
  desc 'Compute prices history average'
  task :compute_prices_history_average => :environment do

    puts 'Recomputing prices history average'

    Crest::ComputePriceHistoryAvg.new

    puts 'End of recomputing prices history average'
  end
end

namespace :data_download do

  desc 'Download eve markets/histories'
  task :eve_markets_histories => :environment do
    puts 'About to update the table eve_markets_histories'
    Esi::DownloadPricesHistory.new( debug_request: true ).update_table
  end


end