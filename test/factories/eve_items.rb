FactoryBot.define do

  factory :eve_item do

    cost {5}
    name {'Item test'}
    cpp_eve_item_id {123456}
		description { "Hopla vous savez que la mamsell Huguette, la miss Miss Dahlias du messti de Bischheim était au Christkindelsmärik en compagnie de Richard Schirmeck (celui qui a un blottkopf), le mari de Chulia Roberstau, qui lui trempait sa Nüdle dans sa Schneck ! Yo dû, Pfourtz ! Ch'espère qu'ils avaient du Kabinetpapier, Gal !" }

    # An example of item with blueprint and market group
    factory :inferno_fury_cruise_missile do
      cpp_eve_item_id {2621}
      name {'Inferno Fury Cruise Missile'}
      cost {1815252.83}
      market_group { FactoryBot.create( :advanced_high_damage_cruise_missiles_market_group ) }
      blueprint { create( :inferno_fury_cruise_missile_blueprint ) }
    end

    # An example of item with blueprint but no market group
    factory :mjolnir_fury_cruise_missile do
      cpp_eve_item_id {24535}
      name {'Mjolnir Fury Cruise Missile'}
      cost {1815252.83}
      blueprint { create( :mjolnir_fury_cruise_missile_blueprint ) }
    end

    # An example with no blueprint and no market group
    factory :inferno_precision_cruise_missile do
      cpp_eve_item_id {2637}
      name {'Inferno Precision Cruise Missile'}
      cost {1815252.83}
		end

		# I have a bug with this specific item
		factory :barrage_l do
			cpp_eve_item_id { 12775 }
			name {'Barrage L' }
			cost { 436.68593097623614 }
			base_item { false }
			production_level { 0 }
		end

		# [
		# 	{
		# 		"id": 919,
		# 		"cpp_eve_item_id": 12775,
		# 		"name": "Barrage L",
		# 		"created_at": "2015-08-30 09:49:28.927539",
		# 		"updated_at": "2019-09-11 21:00:47.758946",
		# 		"cost": 436.68593097623614,
		# 		"market_group_id": 2513,
		# 		"blueprint_id": 918,
		# 		"volume": 0.025,
		# 		"production_level": 0,
		# 		"base_item": false,
		# 		"cpp_market_adjusted_price": 711.0,
		# 		"cpp_market_average_price": 608.36,
		# 		"description": "An advanced version of the standard Nuclear ammo with a Morphite-enriched warhead and a smart tracking system. <br><br>25% reduced tracking.<br>40% increased falloff.<br><br>Note: This ammunition can only be used by large tech level II, faction and officer Autocannons.",
		# 		"market_group_path": "[{\"name\":\"Ammunition \\u0026 Charges\",\"id\":1957},{\"name\":\"Projectile Ammo\",\"id\":1990},{\"name\":\"Advanced Autocannon Ammo\",\"id\":2503},{\"name\":\"Large\",\"id\":2513}]",
		# 		"mass": 0.01,
		# 		"packaged_volume": 0.025,
		# 		"weekly_avg_price": 518.0947323611435,
		# 		"faction": false
		# 	}
		# ]

    # Name says
    factory :dummy_eve_item do
      cpp_eve_item_id {999999}
      name {'Dummy eve item'}
    end

    # Items required for blueprints
    # Todo : add items in EveItem if u want the test to work
    factory :morphite do
      cpp_eve_item_id {11399}
      name {'Morphite'}
      cost {80}
      volume {0.01}
			base_item { true  }
    end

    factory :rocket_fuel do
      cpp_eve_item_id {9830}
      name {'Rocket Fuel'}
    end

    factory :ram_amunition_tech do
      cpp_eve_item_id {11476}
      name {'R.A.M.- Ammunition Tech'}
    end

    factory :plasma_pulse_generator do
      cpp_eve_item_id {11695}
      name {'Plasma Pulse Generator'}
    end

    factory :em_pulse_generator do
      cpp_eve_item_id {11694}
      name {'EM Pulse Generator'}
    end

    factory :phenolic_composite do
      cpp_eve_item_id {16680}
      name {'Phenolic Composites'}
    end

  end
end
