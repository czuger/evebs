require 'yaml'

EAAL.cache = EAAL::Cache::FileCache.new( 'tmp' )

namespace :data_setup do
  desc "Feed item objects list"
  task :eve_objects => :environment do
    puts 'About to fill the objects list'
    blueprints_array=Blueprint.load_blueprint_array
    eve_item_hash=EveItem.download_items_hash
    blueprints_array.each do |bp|
      item_id = bp[:produced_item_id]
      unless EveItem.find_by_cpp_eve_item_id( item_id )
        item_name = eve_item_hash[item_id]
        if item_name
          puts "About to insert #{item_id}, #{item_name}"
          EveItem.find_or_create_by( cpp_eve_item_id: item_id, name: item_name, name_lowcase: item_name.downcase )
        end
      end
    end
  end
  desc "Fill name_lowcase"
  task :fill_name_lowcase => :environment do
    EveItem.all.to_a.each do |ei|
      puts "About to lowercase #{ei.name}"
      ei.update_attribute( :name_lowcase, ei.name.downcase )
    end
  end
end