FactoryGirl.define do
  sequence :cpp_eve_item_id do |n|
    n
  end
  sequence :name do |n|
    "Item id #{n}"
  end
  sequence :name_lowcase do |n|
    "item id #{n}"
  end
  factory :eve_item do
    cpp_eve_item_id 5
    name
    name_lowcase
    cost 5
    involved_in_blueprint true
    factory :inferno_fury_cruise_missile do
      cpp_eve_item_id 2621
      name "Inferno Fury Cruise Missile"
      name_lowcase "inferno fury cruise missile"
      cost 1815252.83
      blueprint {FactoryGirl.create( :inferno_fury_cruise_blueprint )}
    end
    factory :mjolnir_fury_cruise_missile do
      cpp_eve_item_id 24535
      name "Mjolnir Fury Cruise Missile"
      name_lowcase "mjolnir fury cruise missile"
      cost 1815252.83
      blueprint {FactoryGirl.create( :inferno_fury_cruise_blueprint )}
    end
    factory :inferno_precision_cruise_missile do
      cpp_eve_item_id 2637
      name "Inferno Precision Cruise Missile"
      name_lowcase "inferno precision cruise missile"
      cost 1815252.83
    end
    # Todo : add items in EveItem if u want the test to work
    factory :morphite do
      cpp_eve_item_id 11399
      name 'Morphite'
      name_lowcase 'morphite'
      cost 0
    end
    factory :rocket_fuel do
      cpp_eve_item_id 9830
      name 'Rocket Fuel'
    end
    factory :ram_amunition_tech do
      cpp_eve_item_id 11476
      name 'R.A.M.- Ammunition Tech'
    end
    factory :plasma_pulse_generator do
      cpp_eve_item_id 11695
      name 'Plasma Pulse Generator'
    end
    factory :phenolic_composite do
      cpp_eve_item_id 16680
      name 'Phenolic Composites'
    end

  end
end
