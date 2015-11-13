namespace :data_setup do

  namespace :blueprint do

    desc 'Recompute items involved in blueprints'
    task :recompute_items_involved => :environment do
      ItemsInit::ItemsList.has_blueprint
      ItemsInit::ItemsList.involved_in_blueprint
    end

    desc 'Cleanup blueprints with no items'
    task :cleanup_blueprints => :environment do
      Blueprint.delete_all( 'eve_item_id IS NULL')
    end

  end

  desc "Feed blueprints informations"
  task :blueprints_setup => :environment do
    puts 'About to feed the blueprint database'
    ActiveRecord::Base.transaction do
      blueprints_array=Blueprint.load_blueprint_array
      blueprints_array.each do |bp|
        # next if bp[:skills_count] <= 1 # Blueprint shit
        blueprint_id = bp[:blueprint_id]
        unless Blueprint.find_by_cpp_blueprint_id( blueprint_id )
          next if Blueprint::UNWANTED_BLUEPRINTS.include?( blueprint_id.to_i )
          produced_item_id = bp[:produced_item_id]
          next if EveItem::UNPROCESSABLE_ITEMS.include?( produced_item_id.to_i )
          produced_item_qtt = bp[:produced_item_qtt]
          max_production_limit = bp[:max_production_limit]
          puts "Working on blueprint : eve_elueprint_id=#{blueprint_id}, eve_produced_item_id=#{produced_item_id}, qtt=#{produced_item_qtt}, max_run=#{max_production_limit}"
          internal_eve_item = EveItem.where( 'cpp_eve_item_id = ?',produced_item_id).first
          next unless internal_eve_item
          puts "Will produce : #{internal_eve_item.name}"
          blueprint = Blueprint.find_or_create_by!( cpp_blueprint_id: blueprint_id, eve_item_id: internal_eve_item.id,
                                                    prod_qtt: produced_item_qtt, nb_runs: max_production_limit )
          if bp[:materials]
            bp[:materials].each do |material|
              component_id = material['typeID']
              qtt = material['quantity']
              component = Component.where( 'cpp_eve_item_id=?',component_id).first
              unless component
                component_name = EveItem.find_by_cpp_eve_item_id( component_id ).name
                component = Component.create!( cpp_eve_item_id: component_id, name: component_name )
              end
              puts "Materials = #{component.name}, #{component_id}, #{qtt}"
              material = Material.where( 'component_id=? AND blueprint_id=?', component.id, blueprint.id ).first
              unless material
                Material.create!( blueprint_id: blueprint.id, component_id: component.id, required_qtt: qtt )
              end
            end
          end
          puts
        end
      end
      # Setup blueprint involvement
      ItemsInit::ItemsList.has_blueprint
      ItemsInit::ItemsList.involved_in_blueprint
    end
  end

  desc "Delete unproductable blueprint"
  task :blueprints_delete_unproductable => :environment do
    unwanted_names = [ 'Police Pursuit Comet', 'Moracha', ]
    unwanted_names.each do |name|
      Blueprint.joins(:eve_item).where( "eve_items.name = '#{name}'" ).each{ |i| i.destroy }
    end
    Blueprint.joins(:eve_item).where( "eve_items.name like '%Edition%'" ).each{ |i| i.destroy }
    Blueprint.joins(:eve_item).where( "eve_items.name like '%Navy%'" ).each{ |i| i.destroy }
    Blueprint.joins(:eve_item).where( "eve_items.name like '%Ishukone%'" ).each{ |i| i.destroy }

  end

end
