require 'yaml'

namespace :process do

  desc "Load blueprints and items"
  task :blueprints => :environment do
    Esi::UpdateBlueprints.new( nil ).update
    Esi::DownloadEveItems.new(debug_request: false ).update
  end

  # TODO : move elements or rename this
  desc "Update market groups"
  task :update_market_groups => :environment do
    Esi::DownloadMarketGroups.new( debug_request: false ).update
  end

  desc "Build JSON market groups + eve items tree"
  task :build_items_tree => :environment do
    MarketGroup.build_items_tree
  end

end