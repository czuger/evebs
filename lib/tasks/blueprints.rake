namespace :data_setup do
  desc "Feed blueprints informations"
  task :blueprints_setup => :environment do
    puts 'About to feed the blueprint database'
    blueprints_array=Blueprint.load_blueprint_array
    eve_item_hash=EveItem.download_items_hash
    blueprints_array.each do |bp|
      blueprint_id = bp[:blueprint_id]
      produced_item_id = bp[:produced_item_id]
      produced_item_qtt = bp[:produced_item_qtt]
      max_production_limit = bp[:max_production_limit]
      puts "#{blueprint_id}, #{produced_item_id}, #{produced_item_qtt}, #{max_production_limit}"
      internal_eve_item = EveItem.where( 'cpp_eve_item_id = ?',produced_item_id).first
      blueprint = Blueprint.find_or_create_by!( cpp_blueprint_id: blueprint_id, eve_item_id: internal_eve_item.id,
        prod_qtt: produced_item_qtt, nb_runs: max_production_limit )
      if bp[:materials]
        bp[:materials].each do |material|
          component_id = material['typeID']
          qtt = material['quantity']
          component = Component.where( 'cpp_eve_item_id=?',component_id).first
          unless component
            component_name = eve_item_hash[component_id]
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
end
