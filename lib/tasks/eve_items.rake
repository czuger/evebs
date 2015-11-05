require 'yaml'

EAAL.cache = EAAL::Cache::FileCache.new( 'tmp' )

namespace :data_setup do
  desc "Feed item objects list"
  task :load_all_items => :environment do
    puts 'About to fill the objects list'
    Crest::EveItemsFromCrest.new
  end
  desc "Fill name_lowcase"
  task :fill_name_lowcase => :environment do
    EveItem.all.to_a.each do |ei|
      puts "About to lowercase #{ei.name}"
      ei.update_attribute( :name_lowcase, ei.name.downcase )
    end
  end
end