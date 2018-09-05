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

      # Hourly process should be stopped when daily crontab is on.
      Crontab.start( :hourly )

      ActiveRecord::Base.transaction do
        # Esi::UpdateVolumeFromHistory.new.update

        Sql::UpdatePricesAvgWeeks.update

        BlueprintComponent.compute_costs
        EveItem.compute_cost_for_all_items
      end

      Crontab.stop( :hourly )

      # Esi::UpdateStructures.new( debug_request: false ).update
      Banner.p( 'Finished' )
    end

    desc 'Full process - weekly'
    task :weekly => :environment do
      Process::ParseBlueprintsFile.new.parse

      Esi::DownloadBlueprints.new.download
      Esi::DownloadEveItems.new.download

      Process::SetEveItemDepthLevel.new.set

      ActiveRecord::Base.transaction do
        Process::UpdateBlueprints.new.update
        Process::UpdateEveItems.new.update
      end

      Banner.p( 'Finished' )
    end
  end
end