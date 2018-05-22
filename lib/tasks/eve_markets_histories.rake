namespace :process do

  desc 'Download eve markets/histories'
  task :eve_markets_histories => :environment do
    Banner.p 'About to update the table eve_markets_histories'

    Esi::DownloadPricesHistory.new( debug_request: false ).update_table
  end

  desc 'Compute prices history average'
  task :compute_prices_history_average => :environment do

    Banner.p 'Recomputing prices history average'

    Crest::ComputePriceHistoryAvg.new

    Banner.p 'End of recomputing prices history average'
  end

  desc 'Compute component costs from Jita prices - then refresh all items costs'
  task :costs => :environment do

    debug = ENV[ 'EBS_DEBUG_MODE' ] && ENV[ 'EBS_DEBUG_MODE' ].downcase == 'true'

    Banner.p 'Recomputing costs from Jita prices'
    puts 'CAUTION : make sure that crest_prices_last_month_averages is loaded with Jita prices'
    Component.set_min_prices_for_all_components

    puts 'Refreshing all items costs'
    EveItem.where(involved_in_blueprint:true).all.each do |ei|
      puts "Recomputing cost for #{ei.name}"
      ei.compute_cost
    end
    Banner.p 'End for all recomputing cost'
  end

end