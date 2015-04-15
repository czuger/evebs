require 'yaml'

EAAL.cache = EAAL::Cache::FileCache.new( 'tmp' )

namespace :load do
  desc "Feed item objects list"
  task :eve_objects => :environment do
    blueprints=YAML.load_file('lib/tasks/blueprints.yaml')
    api = EAAL::API.new(nil,nil)
    api.scope = "eve"

    blueprints.each do |bp|
      if bp[1]['activities']['manufacturing']
        item_id = bp[1]['activities']['manufacturing']['products'].first['typeID']
        item_name_object = api.TypeName(:ids => item_id)
        item_name = item_name_object.types.first.typeName
        puts "#{item_id}, #{item_name}"
        EveItem.find_or_create_by( eve_item_id: item_id, name: item_name )
      end
    end
  end
  desc "Add the first letter of each object to each object"
  task :add_first_letter_to_eve_object => :environment do
    EveItem.all.to_a.each do |ei|
      size_words = %w( Small Medium Large Capital Mjolnir Scourge Fury Inferno )
      size_words.each do |sw|
        if ei.name.start_with?( sw )
          removed_size_name = ei.name[ sw.length + 1 .. -1 ]
          ei.update_attribute( :name, "#{removed_size_name} (#{sw})")
        end
      end
      # No white space for beginning
      if ei.name.start_with?( ' ' )
        no_white_space = ei.name[ 1 .. -1 ]
        ei.update_attribute( :name, no_white_space )
      end
      # Remove quote from name
      if ei.name.include?( "'" )
        no_quotes = ei.name.gsub( "'", '' )
        ei.update_attribute( :name, no_quotes )
      end
      ei.update_attribute( :first_letter, ei.name[0].upcase )
    end
  end
  desc "Fill name_lowcase"
  task :fill_name_lowcase => :environment do
    EveItem.all.to_a.each do |ei|
      ei.update_attribute( :name_lowcase, ei.name.downcase )
    end
  end
end