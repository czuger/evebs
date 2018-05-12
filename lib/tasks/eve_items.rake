require 'yaml'

namespace :data_setup do

  desc "Feed item objects list"
  task :update_all_items => :environment do
    puts 'About to fill the objects list'

    # TODO : remettre ces updates en prod, ces updates doivent être intégrés a la tâche hebdomadaire.
    # Esi::DownloadTypeInRegion.new( debug_request: true ).update
    # Esi::DownloadMarketGroups.new( debug_request: true ).update
    # Esi::EveItems.new(debug_request: true ).update

    Fuzzwork::Blueprints.new.update

    # Il faudra d'abord calculer crest_prices_last_month_average before compuctin prices

  end

  desc "Fill name_lowcase"
  task :fill_name_lowcase => :environment do
    EveItem.all.to_a.each do |ei|
      puts "About to lowercase #{ei.name}"
      ei.update_attribute( :name_lowcase, ei.name.downcase )
    end
  end

  desc "Build JSON market groups + eve items tree"
  task :build_items_tree => :environment do
    MarketGroup.build_items_tree
  end

end