FactoryBot.define do
  factory :blueprint_component do
    factory :component_morphite do
      cpp_eve_item_id 11399
      name 'Morphite'
      cost 1000
    end
    factory :component_rocket_fuel do
      cpp_eve_item_id 9830
      name 'Rocket Fuel'
      cost 2000
    end
    factory :component_ram_amunition_tech do
      cpp_eve_item_id 11476
      name 'R.A.M.- Ammunition Tech'
      cost 10
    end
    factory :component_plasma_pulse_generator do
      cpp_eve_item_id 11695
      name 'Plasma Pulse Generator'
      cost 500
    end
    factory :component_phenolic_composite do
      cpp_eve_item_id 16680
      name 'Phenolic Composites'
      cost 2500
    end
  end
end
