FactoryBot.define do

  factory :production_list do

    factory :inferno_fury_cruise_missile_production_list do
      user
      eve_item { create( :inferno_fury_cruise_missile ) }
      trade_hub { TradeHub.find_by_eve_system_id( 30000142 ) || create( :jita ) }
      runs_count {1}
      quantity_to_produce {100}
    end

    factory :mjolnir_fury_cruise_missile_production_list do
      user
      eve_item { create( :mjolnir_fury_cruise_missile ) }
      trade_hub { TradeHub.find_by_eve_system_id( 30000142 ) || create( :jita ) }
      runs_count {1}
      quantity_to_produce {100}
    end

  end
end
