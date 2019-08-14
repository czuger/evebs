FactoryBot.define do
  factory :universe_station do
    sequence :name do |n|
      "Station detail #{n}"
    end

    office_rental_cost {1.5}
    cpp_station_id {1}
    services { [] }

    factory :vellaine do
      name { 'Vellaine VI - Moon 9 - Propel Dynamics Factory' }

      cpp_station_id { 60002407 }

      universe_system { UniverseSystem.find_by_cpp_system_id( 30001380 ) || FactoryBot.create( :vellaine_system ) }
    end
  end
end
