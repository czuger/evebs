FactoryBot.define do

  factory :blueprint_material do

    blueprint
    required_qtt { -999 }

    factory :material_morphite do
      eve_item { EveItem.find_by_cpp_eve_item_id( 11399 ) || FactoryBot.create( :morphite ) }
    end

    factory :material_rocket_fuel do
      eve_item { EveItem.find_by_cpp_eve_item_id( 9830 ) || FactoryBot.create( :rocket_fuel ) }
    end

    factory :material_plasma_pulse_generator do
      eve_item { EveItem.find_by_cpp_eve_item_id( 11695 ) || FactoryBot.create( :plasma_pulse_generator ) }
    end

    factory :em_plasma_pulse_generator do
      eve_item { EveItem.find_by_cpp_eve_item_id( 11694 ) || FactoryBot.create( :em_plasma_pulse_generator ) }
    end

  end
end
