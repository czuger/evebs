FactoryBot.define do

  factory :universe_system do

    cpp_system_id {'123456'}
    name {'Test trade hub'}
    cpp_star_id { 1 }
    security_class { 'A' }
    security_status { 1.5 }

    factory :universe_jita do
      cpp_system_id {'30000142'}
      name {'Jita'}
      universe_constellation { UniverseConstellation.find_by_cpp_constellation_id( 20000020 ) || create( :constellation_kimotoro ) }

      after(:create) do
        create(:jita)
      end
    end

    factory :vellaine_system do
      cpp_system_id { 30001380 }
      name { 'Vellaine' }
    end
  end
end
