FactoryBot.define do
  factory :universe_constellation do

    factory :constellation_kimotoro do
      cpp_constellation_id { 20000020 }
      name { 'Joas' }

      universe_region { UniverseRegion.find_by_cpp_region_id( 10000002 ) || create( :universe_the_forge ) }
    end
  end
end
