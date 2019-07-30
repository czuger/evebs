FactoryBot.define do
  factory :universe_system do
    cpp_system_id { 1 }
    name { "MyString" }
    cpp_constellation_id { 1 }
    cpp_star_id { 1 }
    security_class { "MyString" }
    security_status { 1.5 }
    stations_ids { [ 60002407 ] }

    factory :vellaine_system do
      cpp_system_id { 30001380 }
      name { 'Vellaine' }
    end
  end
end
