# namespace :process do
#   desc 'Full data setup'
#   task :full => [:environment, :trade_hubs, :regions, 'price_history:init', :update_all_items, :blueprints_setup, :stations, :market_groups]
# end

namespace :process do
  namespace :full do

    desc 'Full process - hourly'
    task :hourly => :environment do

      Crontab.start( :hourly )

      ActiveRecord::Base.transaction do
        Esi::DownloadSalesOrders.new( debug_request: false ).update( only_cpp_region_id: nil )

        Sql::PricesMins.update
        Sql::PricesAdvices.update

        Esi::DownloadMyOrders.new.update()
      end

      Banner.p( 'Finished' )

      Crontab.stop( :hourly )
    end

    desc 'Full process - daily'
    task :daily => :environment do

      Crontab.start( :hourly )

      ActiveRecord::Base.transaction do
        Comp::SalesFinals.run
        Sql::PricesAvgWeeks.update
        EveItem.compute_cost_for_all_items
      end

      Crontab.stop( :hourly )

      # Esi::UpdateStructures.new( debug_request: false ).update
      Banner.p( 'Finished' )
    end

    desc 'Full process - weekly'
    # TODO, revoir le process, faire le calcul des couts avant la creation du nouveau arbre d'objets.
    task :weekly => :environment do
      Banner.p 'About to download types in regions'
      Esi::DownloadTypeInRegion.new( debug_request: false ).update

      Banner.p 'About to download types in regions'
      Esi::DownloadMarketGroups.new( debug_request: false ).update

      Esi::EveItems.new(debug_request: false ).update

      Banner.p 'About to update the table eve_markets_histories'

      Banner.p 'About to update blueprints'
      Fuzzwork::Blueprints.new.update

      # Esi::DownloadPricesHistory.new( debug_request: false ).update_table
      #
      # Crest::ComputePriceHistoryAvg.new
      #
      # EveItem.compute_cost_for_all_items

      MarketGroup.build_items_tree

      Banner.p( 'Finished' )
    end
  end
end