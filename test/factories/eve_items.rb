FactoryGirl.define do

  factory :eve_item do

    cost 5
    involved_in_blueprint true

    # An example of item with blueprint and market group
    factory :inferno_fury_cruise_missile do
      cpp_eve_item_id 2621
      name "Inferno Fury Cruise Missile"
      name_lowcase "inferno fury cruise missile"
      cost 1815252.83
      market_group { FactoryGirl.create( :advanced_high_damage_cruise_missiles_market_group ) }

      after(:create) do |eve_item|
        create( :inferno_fury_cruise_blueprint, eve_item: eve_item )
      end

    end

    # An example of item with blueprint but no market group
    factory :mjolnir_fury_cruise_missile do
      cpp_eve_item_id 24535
      name "Mjolnir Fury Cruise Missile"
      name_lowcase "mjolnir fury cruise missile"
      cost 1815252.83

      after(:create) do |eve_item|
        create( :inferno_fury_cruise_blueprint, eve_item: eve_item )
      end

    end

    # An example with no blueprint and no market group
    factory :inferno_precision_cruise_missile do
      cpp_eve_item_id 2637
      name "Inferno Precision Cruise Missile"
      name_lowcase "inferno precision cruise missile"
      cost 1815252.83
    end

    # Name says
    factory :dummy_eve_item do
      cpp_eve_item_id 999999
      name "Dummy eve item"
      name_lowcase "dummy eve item"
    end

    # Items required for blueprints
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
