FactoryBot.define do
  factory :blueprint do

    sequence :name do |n|
      "Blueprint #{n}"
    end

    nb_runs {1}
    prod_qtt {1}
    cpp_blueprint_id {50}

    factory :inferno_fury_cruise_missile_blueprint do

      nb_runs {100}
      cpp_blueprint_id {31479}
      produced_cpp_type_id {2621}

      after(:create) do |blueprint|
        create( :material_morphite, blueprint: blueprint, required_qtt: 15 )
        create( :material_rocket_fuel, blueprint: blueprint, required_qtt: 129 )
        create( :material_plasma_pulse_generator, blueprint: blueprint, required_qtt: 14 )

        # create( :material_ram_amunition_tech, blueprint: blueprint )
        # create( :material_phenolic_composite, blueprint: blueprint )
      end
    end

    factory :mjolnir_fury_cruise_missile_blueprint do

      nb_runs {100}
      cpp_blueprint_id {24536}
      produced_cpp_type_id {24535}

      after(:create) do |blueprint|
        create( :material_morphite, blueprint: blueprint, required_qtt: 15 )
        create( :material_rocket_fuel, blueprint: blueprint, required_qtt: 129 )
        create( :material_plasma_pulse_generator, blueprint: blueprint, required_qtt: 14 )

        # create( :material_ram_amunition_tech, blueprint: blueprint )
        # create( :material_phenolic_composite, blueprint: blueprint )
      end
    end

  end
end