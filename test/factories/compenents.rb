FactoryGirl.define do
  factory :component do
    factory :component_morphite do
      cpp_eve_item_id 11399
      name 'Morphite'
    end
    factory :component_rocket_fuel do
      cpp_eve_item_id 9830
      name 'Rocket Fuel'
    end
    factory :component_ram_amunition_tech do
      cpp_eve_item_id 11476
      name 'R.A.M.- Ammunition Tech'
    end
    factory :component_plasma_pulse_generator do
      cpp_eve_item_id 11695
      name 'Plasma Pulse Generator'
    end
    factory :component_phenolic_composite do
      cpp_eve_item_id 16680
      name 'Phenolic Composites'
    end
  end
end
