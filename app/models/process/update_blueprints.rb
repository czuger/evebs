module Process

  class UpdateBlueprints

    def update
      Banner.p 'About to update blueprints'

      blueprints = YAML::load_file('data/parsed_blueprints.yaml')

      blueprints_to_destroy = Blueprint.pluck( :cpp_blueprint_id ) - blueprints.keys
      Blueprint.where( cpp_blueprint_id: blueprints_to_destroy ).destroy_all

      blueprints.values.each do |blueprint|
        on_db_blueprint = Blueprint.where( cpp_blueprint_id: blueprint[:cpp_blueprint_id] ).first_or_initialize

        on_db_blueprint.produced_cpp_type_id = blueprint[:produced_cpp_type_id]
        on_db_blueprint.nb_runs = blueprint[:nb_runs]
        on_db_blueprint.prod_qtt = blueprint[:prod_qtt]
        on_db_blueprint.name = blueprint[:name]

        on_db_blueprint.save!
      end
    end
  end

end

