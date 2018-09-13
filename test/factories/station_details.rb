FactoryBot.define do
  factory :station_detail do
    sequence :name do |n|
      "Station detail #{n}"
    end

    office_rental_cost {1.5}
    cpp_station_id {1}
    cpp_system_id {1}
    services { [] }
  end
end
