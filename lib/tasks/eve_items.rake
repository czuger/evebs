require 'yaml'

namespace :data_setup do

  desc "Feed item objects list"
  task :update_all_items => :environment do
    puts 'About to fill the objects list'
    Esi::Types.new( debug_request: true ).update
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