require 'yaml'

namespace :data_setup do

  desc "Load blueprints and items"
  task :blueprints => :environment do
    Esi::UpdateBlueprints.new( nil ).update
    # Esi::DownloadEveItems.new(debug_request: false ).update
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

  desc 'Set faction boolean for EveItem'
  task :set_faction_boolean => :environment do
    factions_identifier = [ 'Federation Navy', 'Khanid Navy', 'Dark Blood', 'True Sansha', 'Imperial Navy', 'Caldari Navy',
                            'Republic Fleet', 'Ammatar Navy', 'Dread Guristas', 'Shadow Serpentis', 'High-grade', "Magpie",
    "Yurt", "Wetu", 'Packrat', 'Encounter Surveillance System' ]

    ActiveRecord::Base.transaction do
      EveItem.where( id: EveItem.all.select{ |e| e.market_group_path.join =~ /Special Edition Ships/ }.map{ |e| e.id } ).update_all( faction: true )
      EveItem.where( id: EveItem.all.select{ |e| e.market_group_path.join =~ /action/ }.map{ |e| e.id } ).update_all( faction: true )
      factions_identifier.each do |f|
        EveItem.where( "name LIKE '%#{f}%'" ).update_all( faction: true )
      end
    end

  end

end