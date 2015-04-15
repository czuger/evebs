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
  desc "Fill name_lowcase"
  task :fill_name_lowcase => :environment do
    EveItem.all.to_a.each do |ei|
      ei.update_attribute( :name_lowcase, ei.name.downcase )
    end
  end
end