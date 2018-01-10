FactoryBot.define do
  factory :blueprint do

    nb_runs 1
    prod_qtt 1
    cpp_blueprint_id 50

    factory :inferno_fury_cruise_blueprint do

      nb_runs 100
      cpp_blueprint_id 31479

      after(:create) do |blueprint|
        create( :material_morphite, blueprint: blueprint )
        create( :material_rocket_fuel, blueprint: blueprint )
        create( :material_ram_amunition_tech, blueprint: blueprint )
        create( :material_plasma_pulse_generator, blueprint: blueprint )
        create( :material_phenolic_composite, blueprint: blueprint )
      end

    end
  end
end