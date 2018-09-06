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
        Esi::DownloadSalesOrders.new( debug_request: false ).update

        Sql::PricesMins.update
        BpcPricesMin.feed_table

        Sql::UpdatePricesAdvices.update

        Sql::UpdateBuyOrdersAnalytics.update

        # Esi::DownloadMyOrders.new.update()
      end

      Banner.p( 'Finished' )

      Crontab.stop( :hourly )
    end

    desc 'Full process - daily'
    task :daily => :environment do


      ActiveRecord::Base.transaction do
        # Esi::UpdateVolumeFromHistory.new.update

        Sql::UpdatePricesAvgWeeks.update

        EveItem.compute_cost_for_all_items
      end

      Banner.p( 'Finished' )
    end

    desc 'Full process - weekly'
    task :weekly => :environment do
      Process::ParseBlueprintsFile.new.parse

      Esi::DownloadBlueprints.new.download
      Esi::DownloadEveItems.new.download

      Process::SetEveItemDepthLevel.new.set

      Esi::DownloadMarketGroups.new.download

      Process::CleanBlueprints.new.clean

      ActiveRecord::Base.transaction do
        Process::UpdateMarketGroups.new.update
        Process::UpdateBlueprints.new.update
        Process::UpdateEveItems.new.update
        Process::UpdateBlueprintMaterials.new.update


        # Even it does not change the DB, we want the DB chances to be available
        # once the market tree has changed
        Process::BuildJsonMarketTree.new.build
      end

      Banner.p( 'Finished' )
    end
  end
end