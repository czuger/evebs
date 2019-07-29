FactoryBot.define do
  factory :bpc_asset do
    quantity { 5689 }
    touched { false }

    eve_item { EveItem.find_by_cpp_eve_item_id( 2621 ) || create( :inferno_fury_cruise_missile ) }
    universe_station { UniverseStation.find_by_cpp_station_id(60002407 ) || create(:vellaine ) }
  end
end
