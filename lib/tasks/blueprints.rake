namespace :data_setup do
  desc "Feed blueprints informations"
  task :blueprints_setup => :environment do
    puts 'About to feed the blueprint database'
    blueprints=YAML.load_file('lib/tasks/blueprints.yaml')
    api = EAAL::API.new(nil,nil)
    api.scope = "eve"
    blueprints.each do |bp_id,bp|
      if bp['activities']['manufacturing']
        blueprint_id = bp_id
        manufacturing = bp['activities']['manufacturing']
        produced_item_id = manufacturing['products'].first['typeID']
        produced_item_qtt = manufacturing['products'].first['quantity']
        max_production_limit = bp['maxProductionLimit']
        puts "#{blueprint_id}, #{produced_item_id}, #{produced_item_qtt}, #{max_production_limit}"
        internal_eve_item = EveItem.where( 'cpp_eve_item_id = ?',produced_item_id).first
        blueprint = Blueprint.find_or_create_by!( cpp_blueprint_id: blueprint_id, eve_item_id: internal_eve_item.id,
          prod_qtt: produced_item_qtt, nb_runs: max_production_limit )
        if manufacturing['materials']
          manufacturing['materials'].each do |material|
            component_id = material['typeID']
            qtt = material['quantity']
            component = Component.where( 'cpp_eve_item_id=?',component_id).first
            unless component
              component_name = api.TypeName(:ids => component_id).types.first.typeName
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
end

=begin
TODO :
  - Crer un modele blueprint
  - Crer un modele component
  - Crer une HBTM entre les deux

  - Pour le chargement :
  Lire tous les blueprints
  L'id de l'objet produit est dans activities.manufacturing.product (qtt, typeID)
  Les composants sont dans activities.manufacturing.materials (qtt, TypeID)
  maxProductionLimit donne le nombre de runs

  Ne pas oublier d'enregistrer l'eve_id (en plus de l'id interne)
=end
