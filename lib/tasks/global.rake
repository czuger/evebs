# namespace :process do
#   desc 'Full data setup'
#   task :full => [:environment, :trade_hubs, :regions, 'price_history:init', :update_all_items, :blueprints_setup, :stations, :market_groups]
# end

namespace :process do
  namespace :full do

    desc 'Full process - hourly'
    task :hourly => :environment do

      Crontab.start( :hourly )

      Esi::DownloadPublicTradesOrders.new( { verbose_output: false } ).download
      Esi::DownloadMarketsPrices.new.download

      ActiveRecord::Base.transaction do
        Process::UpdateEveItems.new.update

        Process::UpdatePublicTradesOrders.new.update

        Sql::UpdatePricesMin.execute
        Sql::UpdatePricesAdvicesImmediate.execute

        Sql::UpdateBuyOrdersAnalytics.execute
      end

      Crontab.stop( :hourly )

      Banner.p( 'Finished' )
    end

    desc 'Full process - daily'
    task :daily => :environment do


      ActiveRecord::Base.transaction do
        # Esi::UpdateVolumeFromHistory.new.update

        Process::DeleteOldSalesFinals.delete
        Process::UpdateEveItemsCosts.new.update
        Sql::UpdatePricesAdvicesDaily.execute
      end

      Banner.p( 'Finished' )
    end

    desc 'Full process - weekly'
    task :weekly => :environment do
      Process::ParseBlueprintsFile.new.parse

      Esi::DownloadBlueprints.new( { verbose_output: false } ).download
      Esi::DownloadEveItems.new( { verbose_output: false } ).download

      Process::SetEveItemDepthLevel.new.set

      Esi::DownloadMarketGroups.new.download

      Process::CleanBlueprints.new.clean

      ActiveRecord::Base.transaction do
        Process::UpdateMarketGroups.new.update
        Process::UpdateBlueprints.new.update

        # Eve items are now updated on a hourly base due to cpp market prices integration.
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