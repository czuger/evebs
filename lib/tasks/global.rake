# namespace :process do
#   desc 'Full data setup'
#   task :full => [:environment, :trade_hubs, :regions, 'price_history:init', :update_all_items, :blueprints_setup, :stations, :market_groups]
# end

namespace :process do
  namespace :full do

    desc 'Full process - hourly'
    task :hourly => :environment do

      Misc::Crontab.start( :hourly )

      Esi::DownloadPublicTradesOrders.new( { verbose_output: false } ).download
      Esi::DownloadMarketsPrices.new.download

      ActiveRecord::Base.transaction do
        Process::UpdateEveItemsMarketPrices.new.update

        Process::UpdatePublicTradesOrders.new.update

        Sql::UpdatePricesMin.execute
        Sql::UpdatePricesAdvicesImmediate.execute

        Sql::UpdateBuyOrdersAnalytics.execute

        Misc::LastUpdate.set( :hourly )
      end

      Misc::Crontab.stop( :hourly )

      Misc::Banner.p( 'Finished' )
    end

    desc 'Full process - daily'
    task :daily => :environment do

      Misc::Banner.p( 'Daily process started' )

      ActiveRecord::Base.transaction do
        Esi::DownloadHistoryReadItemsLists.new.update
      end

      Esi::DownloadHistory.new.download

      ActiveRecord::Base.transaction do
        Process::UpdateTradeVolumeEstimation.new.update

        Process::DeleteOldSalesFinals.delete

        # Be sure to compute avg prices weeks before to compute items costs.
        Sql::UpdateWeeklyPriceDetails.execute

        Process::UpdateEveItemsCosts.new.update

        Sql::UpdatePricesAdvicesDaily.execute

        Misc::LastUpdate.set( :daily )
      end

      Misc::Banner.p( 'Daily process finished' )
    end

    desc 'Full process - weekly'
    task :weekly => :environment do

      Misc::Banner.p( 'Weekly process started' )

      # Updating new systems if any
      # Esi::DownloadUniverseSystems.new( debug_request: false ).update

      Process::ParseBlueprintsFile.new.parse

      Esi::DownloadBlueprints.new( { verbose_output: false } ).download
      Esi::DownloadEveItems.new( { verbose_output: false } ).download

      Esi::DownloadMarketGroups.new.download

      Process::CleanBlueprints.new.clean

      ActiveRecord::Base.transaction do
        Process::UpdateMarketGroups.new.update
        Process::UpdateBlueprints.new.update

        Process::UpdateEveItems.new.update
        Process::UpdateBlueprintMaterials.new.update

        Misc::CheckItemsProductionsLevels.new.check

        # Even it does not change the DB, we want the DB chances to be available
        # once the market tree has changed
        Process::BuildJsonMarketTree.new.build

        Misc::LastUpdate.set( :weekly )
      end

      Rake::Task[ 'sitemap:refresh' ].invoke

      Misc::Banner.p( 'Weekly process stopped' )
    end
  end
end