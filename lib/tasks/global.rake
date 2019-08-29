# namespace :process do
#   desc 'Full data setup'
#   task :full => [:environment, :trade_hubs, :regions, 'price_history:init', :update_all_items, :blueprints_setup, :stations, :market_groups]
# end

namespace :process do
  namespace :full do

    desc 'Full process - hourly'
    task :hourly => :environment do

      Misc::Banner.p( 'Hourly process started', true )

      chrono = Misc::Chrono.new

      Misc::Crontab.start( :hourly )

      Esi::DownloadPublicTradesOrders.new( { verbose_output: false } ).download
      Misc::PrintProcessMemUsage.new

      Esi::DownloadMarketsPrices.new.download
      Misc::PrintProcessMemUsage.new

      ActiveRecord::Base.transaction do
        Process::UpdateEveItemsMarketPrices.new.update
        Misc::PrintProcessMemUsage.new

        Process::UpdatePublicTradesOrders.new.update
        Misc::PrintProcessMemUsage.new

        Process::UpdateTradeVolumeEstimationsFromPublicTradeOrders.new.update
        Misc::PrintProcessMemUsage.new

        Sql::UpdatePricesMin.execute
        Sql::UpdatePricesAdvicesImmediate.execute

        Sql::UpdateBuyOrdersAnalytics.execute

        Misc::LastUpdate.set( :hourly )
      end

      Misc::Crontab.stop( :hourly )

      chrono.p
      Misc::Banner.p( 'Hourly process finished', true )
    end

    desc 'Full process - daily'
    task :daily => :environment do

      Misc::Banner.p( 'Daily process started', true )

      chrono = Misc::Chrono.new

      ActiveRecord::Base.transaction do
        Esi::DownloadHistoryReadItemsLists.new.update
      end

      Esi::DownloadHistory.new.download

      ActiveRecord::Base.transaction do
        Process::UpdateTradeVolumeEstimationFromDownloadedHistoryData.new.update

        Process::DeleteOldSalesFinals.delete

        # Be sure to compute avg prices weeks before to compute items costs.
        Sql::UpdateWeeklyPriceDetails.execute

        Process::UpdateEveItemsCosts.new.update

        Sql::UpdatePricesAdvicesDaily.execute

        Misc::LastUpdate.set( :daily )
      end

      chrono.p
      Misc::Banner.p( 'Daily process finished', true )
    end

    desc 'Full process - weekly'
    task :weekly => :environment do

      Misc::Banner.p( 'Weekly process started', true )

      chrono = Misc::Chrono.new

      # Updating new systems if any
      Esi::DownloadUniverseRegions.new( debug_request: false ).download

      Process::ParseBlueprintsFile.new.parse

      Esi::DownloadBlueprints.new( { verbose_output: false } ).download
      Esi::DownloadEveItems.new( { verbose_output: false } ).download

      Esi::DownloadMarketGroups.new.download

      Process::CleanBlueprints.new.clean

      ActiveRecord::Base.transaction do
        Process::UpdateUniverseRegions.new.update

        Process::UpdateMarketGroups.new.update
        Process::UpdateBlueprints.new.update

        Process::UpdateEveItems.new.update
        Process::SetEveItemDepthLevel.new.set

        Process::UpdateBlueprintMaterials.new.update

        Misc::CheckItemsProductionsLevels.new.check

        # Even it does not change the DB, we want the DB chances to be available
        # once the market tree has changed
        Process::BuildJsonMarketTree.new.build

        Misc::LastUpdate.set( :weekly )
      end

      Rake::Task[ 'sitemap:refresh' ].invoke if Rails.env.production?

      chrono.p
      Misc::Banner.p( 'Weekly process finished', true )
    end
  end
end