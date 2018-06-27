require 'yaml'

namespace :process do

  # TODO : move elements or rename this
  desc "Update market groups"
  task :update_market_groups => :environment do
    Esi::DownloadMarketGroups.new( debug_request: false ).update
  end

  desc "Recompute blueprints"
  task :rebuild_blueprints => :environment do
    Banner.p 'About to update blueprints'
    Fuzzwork::Blueprints.new.update
  end

  desc "Build JSON market groups + eve items tree"
  task :build_items_tree => :environment do
    MarketGroup.build_items_tree
  end

  # desc "Fill name_lowcase"
  # task :fill_name_lowcase => :environment do
  #   EveItem.all.to_a.each do |ei|
  #     puts "About to lowercase #{ei.name}"
  #     ei.update_attribute( :name_lowcase, ei.name.downcase )
  #   end
  # end
  #


end