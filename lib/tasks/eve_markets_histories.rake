namespace :process do

  desc 'Download eve markets/histories'
  task :eve_markets_histories => :environment do
    Esi::DownloadPricesHistory.new( debug_request: false ).update_table
  end

  desc 'Compute prices history average'
  task :compute_prices_history_average => :environment do
    Crest::ComputePriceHistoryAvg.new
  end

  desc 'Compute component costs from Jita prices - then refresh all items costs'
  task :costs => :environment do
    EveItem.compute_cost_for_all_items
  end

end