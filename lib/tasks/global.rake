# namespace :process do
#   desc 'Full data setup'
#   task :full => [:environment, :trade_hubs, :regions, 'price_history:init', :update_all_items, :blueprints_setup, :stations, :market_groups]
# end

namespace :process do
  namespace :full do

    desc 'Full process - hourly'
    task :hourly => :environment do

      # Esi::DownloadPublicTradesOrders.new( { verbose_output: true } ).download

      ActiveRecord::Base.transaction do

        # Process::UpdatePublicTradesOrders.new.update
        # Process::UpdateEveItemsCosts.new.update

        Sql::UpdatePricesMin.execute

      #
      #   Sql::UpdatePricesAdvices.execute
      #
      #   Sql::UpdateBuyOrdersAnalytics.execute
      #
      #   # Esi::DownloadMyOrders.new.update()
      end

      Banner.p( 'Finished' )
    end

    desc 'Full process - daily'
    task :daily => :environment do


      ActiveRecord::Base.transaction do
        # Esi::UpdateVolumeFromHistory.new.update

        Sql::UpdatePricesAvgWeeks.execute

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