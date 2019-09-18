FactoryBot.define do
  factory :eve_market_histories_group do
    volume { 1000 }
    highest { 50.5 }
    lowest { 3.5 }
    average { 25.5 }

		universe_region { UniverseRegion.find_by_cpp_region_id( 10000002 ) || FactoryBot.create( :universe_the_forge ) }
  end
end
